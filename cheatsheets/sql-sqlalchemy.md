# SQL & relational access with SQLAlchemy

_Grounded in JasonLo's repos as of 2026-06-05; current practice per SQLAlchemy 2.0 docs (context7 `/sqlalchemy/sqlalchemy`: What's New in 2.0, ORM Querying tutorial)._

## Reference snippet

```python
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass


class Endpoint(Base):
    __tablename__ = "endpoint"

    id: Mapped[str] = mapped_column(primary_key=True)
    pmh_url: Mapped[str | None]
    ready_to_run: Mapped[bool] = mapped_column(default=False)


engine = create_engine("postgresql+psycopg://user:pw@host/db")  # one engine per process

# Session scoped to a unit of work; context manager handles close/rollback.
with Session(engine) as session, session.begin():
    stmt = select(Endpoint).where(Endpoint.ready_to_run.is_(True))
    ready = session.execute(stmt).scalars().all()
    # mutate ORM objects; commit happens on block exit
```

## Typical usage patterns

- Postgres via `create_engine` from a `DATABASE_URL` env var; normalize a `postgres://` scheme to `postgresql://` before passing it. One module-level engine reused process-wide. (`JasonLo/openalex-ingest:openalex_ingest/common.py`)
- A `@contextmanager get_db()` wrapper around a `sessionmaker`-built `Session`, yielding the session and closing it in `finally` — manual session lifecycle for batch/worker code. (`JasonLo/openalex-ingest:openalex_ingest/common.py`)
- ORM model as the durable state record (harvest checkpoints: timestamps, retry intervals, flags), read/updated rather than a transient query result. (`JasonLo/openalex-ingest:openalex_ingest/repositories.py`)

## Learnings

- **`session.query(Model).filter(...).all()` as the way to read** → **`select(Model)` statements executed via `session.execute(...).scalars()`.** The Query object is legacy in 2.0; a single `select()` construct now drives both ORM and Core, so query-building is uniform and composable instead of a separate ORM-only API. (seen in `JasonLo/openalex-ingest:openalex_ingest/repositories.py`)
- **`declarative_base()` factory + untyped `Column(Text)` attributes** → **subclass `DeclarativeBase` with `Mapped[...]` / `mapped_column(...)`.** The model's Python types now *are* the schema declaration: type checkers and IDEs see column types, nullability comes from `Optional`/`| None`, and the base is a real class, not a generated one. (seen in `JasonLo/openalex-ingest:openalex_ingest/repositories.py`)
- **Hand-rolled `@contextmanager` around a bare `Session`** → **use `with Session(engine) as s:` (and `s.begin()` for the transaction).** The Session is itself a context manager that guarantees close + rollback-on-error, so the wrapper re-implements what the library already provides. (seen in `JasonLo/openalex-ingest:openalex_ingest/common.py`)

## Agent rules

- ALWAYS build reads with `select(Model)` and run them via `session.execute(stmt).scalars()`.
- NEVER use `session.query(...)` / `.filter(...).all()` — the legacy Query API.
- ALWAYS define models by subclassing `DeclarativeBase` with `Mapped[...]` annotations and `mapped_column(...)`.
- NEVER use `declarative_base()` or untyped `Column(...)` attributes for new models.
- ALWAYS express column nullability through `Mapped[T | None]` rather than untyped columns.
- ALWAYS use `col.is_(None)` / `col.is_(True)` for NULL and boolean identity tests.
- NEVER write `col == None` or `col == True` in filter clauses.
- ALWAYS manage sessions with `with Session(engine) as session:` and scope transactions with `session.begin()`.
- NEVER hand-roll a `@contextmanager` to open/close a `Session`.
- ALWAYS create one `Engine` per process and reuse it; let it own connection pooling.
- ALWAYS treat a `>=2.0` pin as a mandate to use 2.0-style APIs, not 1.x idioms on a new version.
