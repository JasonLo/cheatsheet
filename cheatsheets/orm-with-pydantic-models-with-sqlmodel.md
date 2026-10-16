# ORM with Pydantic models with sqlmodel

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from SQLModel docs (v0.0.24+) and SQLAlchemy 2.x._

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

- A class that inherits from `SQLModel, table=True` gives Pydantic validation, serialization, and a database table in one definition. Constraints, for example `Field(min_length=1)` and `Field(index=True, unique=True)`, go into the validation and into the DB schema. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

- For many-to-many, define a `SQLModel, table=True` link class with both foreign keys as `primary_key=True`. Reference it from each side with `Relationship(back_populates=…, link_model=LinkClass)`, and the composite key blocks duplicate links without a `unique_constraint`. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

- Create one pooled engine at startup with `create_engine(url, pool_pre_ping=True, pool_size=5)`. Each request then opens a new `Session(engine)` through a context manager or `get_session()`. (seen in `UW-Madison-DSI/pelican-data-loader:app/db.py`)

## Learnings

- **One shared `Session` can serve all reruns and requests** → **Each unit of work gets its own `Session`.** A `Session` holds transaction state. After one failed query, every later call fails with `InvalidRequestError`, and `with Session(engine) as session:` for each unit of work prevents this. (seen in `UW-Madison-DSI/pelican-data-loader:app/db.py`)

- **Objects stay usable after `session.commit()`** → **A commit expires every loaded object by default.** With `expire_on_commit=True`, the next attribute access runs a new query. A detached object then raises `DetachedInstanceError`, for example after a `delete`, and `expire_on_commit=False` in the `sessionmaker` prevents this. (seen in `UW-Madison-DSI/pelican-data-loader:app/db.py`)

- **A helper can open its own `Session`** → **One operation uses one transaction.** A separate `Session` hides its inserts from the caller. Reruns of a helper, for example `parse_creators`, then violate unique constraints, and an outer `session` parameter prevents this. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

## Agent rules

- ALWAYS create a new `Session` for each request or unit of work.
- NEVER share one `Session` instance across requests or Streamlit reruns.
- ALWAYS set `expire_on_commit=False` in `sessionmaker` when you read model attributes after `session.commit()` without a new session.
- ALWAYS pass the active `Session` into helper functions that query the DB.
- NEVER define a link table without composite `primary_key=True` on both foreign keys.
- ALWAYS use `pool_pre_ping=True` on long-lived engines for a database that can restart.
