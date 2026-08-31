# ORM with Pydantic models with sqlmodel

_Grounded in JasonLo's repos as of 2026-08-31; current practice per SQLModel docs (v0.0.24+) and SQLAlchemy 2.x._

## Reference snippet

```python
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

class PersonDatasetLink(SQLModel, table=True):
    dataset_id: int = Field(foreign_key="dataset.id", primary_key=True)
    person_id: int = Field(foreign_key="person.id", primary_key=True)

class Dataset(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1)
    creators: list["Person"] = Relationship(back_populates="datasets", link_model=PersonDatasetLink)

class Person(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    datasets: list[Dataset] = Relationship(back_populates="creators", link_model=PersonDatasetLink)

engine = create_engine("sqlite:///metadata.db", pool_pre_ping=True)
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Dataset(name="my-data", creators=[Person(email="a@b.com")]))
    session.commit()

with Session(engine) as session:
    result = session.exec(select(Dataset).where(Dataset.name == "my-data"))
    ds = result.first()
```

## Typical usage patterns

- **Table model with validation constraints** — inherit from `SQLModel, table=True` to get both Pydantic validation and a DB-backed table; use `Field(min_length=1)`, `Field(index=True, unique=True)` to push constraints into both the schema and the DB schema simultaneously. One class definition covers data validation, serialization, and the ORM layer. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

- **Many-to-many via an explicit link model** — define a `SQLModel, table=True` link class with both foreign keys as primary keys (`primary_key=True`), then reference it from each side via `Relationship(back_populates=…, link_model=LinkClass)`. The composite PK prevents duplicate links; no extra `unique_constraint` needed. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

- **Session-per-request with a pooled engine** — create one `create_engine(url, pool_pre_ping=True, pool_size=5)` at startup, then get a fresh `Session(engine)` per request (context manager or `get_session()`). Never share a single `Session` across requests: one failed transaction poisons all later queries in that session. (seen in `UW-Madison-DSI/pelican-data-loader:app/db.py`)

## Learnings

- **Shared `Session` across reruns/requests causes transaction poisoning** → **give each request its own `Session`**. A single cached `Session` object holds transaction state; one failed query rolls back the whole session and every subsequent call fails with `InvalidRequestError`. The SQLModel-recommended pattern is `with Session(engine) as session:` scoped to a single unit of work. (seen in `UW-Madison-DSI/pelican-data-loader:app/db.py`)

- **`expire_on_commit=True` (default) makes post-commit attribute access fire a new query** → **use `expire_on_commit=False` when reading attributes after commit**. After `session.commit()` every loaded instance is "expired" — the ORM re-fetches on next attribute access. When the session is already closed or the object is detached (e.g. after a `delete` operation), this raises `DetachedInstanceError`. Set `expire_on_commit=False` in the `sessionmaker` to keep the in-memory state valid. (seen in `UW-Madison-DSI/pelican-data-loader:app/db.py`)

- **Passing `session` into constructors that call the DB prevents duplicate rows** → **thread the active session through helper functions that need to query**. If a helper like `parse_creators` opens its own `Session`, its inserts are invisible to the caller's transaction and unique-constraint violations occur on re-runs. Pass the outer session as a parameter so all reads and writes are in one transaction. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

## Agent rules

- ALWAYS create a new `Session` per request or unit of work; NEVER share a single `Session` instance across multiple requests or Streamlit reruns.
- ALWAYS use `expire_on_commit=False` in `sessionmaker` when reading model attributes after `session.commit()` without reopening the session.
- ALWAYS pass the active `Session` into helper functions that perform DB queries, so they share the caller's transaction.
- NEVER define a link table without composite `primary_key=True` on both foreign keys — missing it allows duplicate many-to-many associations.
- ALWAYS use `pool_pre_ping=True` on long-lived engines that connect to a database that may restart.
