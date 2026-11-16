# Embedded relational database in Python with sqlite3

_Grounded in JasonLo's repos as of 2026-11-16. Current practice is from the Python 3 standard library docs._

## Reference snippet

```python
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")

def connect(path: str | Path) -> sqlite3.Connection:
    # Set all pragmas and run migrations in one factory function.
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    con.execute("PRAGMA foreign_keys=ON")
    _migrate(con)
    return con

def _migrate(con: sqlite3.Connection) -> None:
    v = con.execute("PRAGMA user_version").fetchone()[0]
    if v == 0:
        con.executescript(f"BEGIN;\n{SCHEMA.read_text()}\nPRAGMA user_version = 1;\nCOMMIT;")

def upsert_item(con: sqlite3.Connection, item: dict) -> None:
    # Use with con: for every write; commits on success, rolls back on exception.
    with con:
        con.execute(
            "INSERT INTO items (id, name) VALUES (:id, :name)"
            " ON CONFLICT(id) DO UPDATE SET name = excluded.name",
            item,
        )
```

## Typical usage patterns

- **Schema-versioned application store.** Use `PRAGMA user_version` and a `.sql` schema file to manage database versioning. A `migrate()` function in the connect factory detects the current version and applies the missing steps.

- **Connection injection into db functions.** Open the connection in the app layer with `closing(connect(path))`. Pass the open `sqlite3.Connection` to every db function.

- **Upsert with ON CONFLICT.** Use `INSERT ... ON CONFLICT(id) DO UPDATE SET col = excluded.col` with named placeholders (`:name`) to insert or update a row in one statement from a dict. Wrap the call in `with con:` for automatic commit and rollback.

- **Pandas integration with df.to_sql().** Call `sqlite3.connect()` to open a file-based database, then use `df.to_sql(name=table, con=conn, if_exists="replace")` to write a pandas DataFrame to a named table. (seen in `JasonLo/triangle_model:src/batch_utils.py`)

## Learnings

- **Setting each pragma in separate calls** → **Setting all pragmas in a connect factory.** `WAL` mode, `busy_timeout`, `foreign_keys`, and `row_factory` must be active on every connection. A factory function that sets them all prevents any pragma from being forgotten on a new connection path.

- **Managing schema changes with CREATE TABLE IF NOT EXISTS** → **Versioning schema with PRAGMA user_version.** `IF NOT EXISTS` cannot apply column additions from a later schema version. `PRAGMA user_version` lets a `migrate()` function detect the current version and apply only the missing steps.

- **Calling `.commit()` manually after each write** → **Using `with con:` for all writes.** The connection context manager commits the transaction on success and rolls back automatically on exception. A missing commit can leave the database in a partial state if an error occurs mid-function.

## Agent rules

- ALWAYS set `journal_mode=WAL`, `busy_timeout=5000`, `foreign_keys=ON`, and `row_factory=sqlite3.Row` inside a connect factory function.
- ALWAYS use `with con:` as the transaction context for every write.
- ALWAYS version the schema with `PRAGMA user_version`.
- ALWAYS call a `migrate()` function inside the connect factory.
- ALWAYS pass an open `sqlite3.Connection` to db functions.
- NEVER open a new connection inside a db function.
- NEVER call `con.commit()` manually in write functions when you use the `with con:` context manager.
