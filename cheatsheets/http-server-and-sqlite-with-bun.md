# HTTP server and SQLite with bun

_Grounded in JasonLo's repos as of 2026-10-22. Current practice is from bun.sh docs._

## Reference snippet

```typescript
// Bun.serve with routes object (Bun v1.2.3+) and bun:sqlite singleton.
import homepage from "./index.html";
import { Database } from "bun:sqlite";

let _db: Database | null = null;
function db(): Database {
  if (!_db) {
    _db = new Database(process.env.DATABASE_PATH ?? "data/app.db", {
      create: true,
      strict: true,
    });
    _db.run("PRAGMA journal_mode = WAL");
    _db.run("PRAGMA foreign_keys = ON");
  }
  return _db;
}

Bun.serve({
  routes: {
    "/": homepage,
    "/api/health": { GET: () => Response.json({ ok: true }) },
    "/api/items": {
      GET: () => Response.json(db().query("SELECT * FROM items").all()),
      POST: async (req) => {
        const { name } = await req.json();
        db().query("INSERT INTO items (name) VALUES (?)").run(name);
        return Response.json({ created: true }, { status: 201 });
      },
    },
  },
  fetch() {
    return new Response("Not found", { status: 404 });
  },
  development: process.env.NODE_ENV !== "production" && { hmr: true },
});
```

## Typical usage patterns

- **`Bun.serve` with the `routes` object.** Declare every route in the `routes` map. Use a method-keyed object for routes that accept more than one HTTP method.

- **HTML file imports as routes.** Import an `.html` file and pass it as a route value. Bun bundles the page and its assets, and HMR updates the browser in development mode.

- **`bun:sqlite` with a module-level singleton.** Open the database one time in the process, and apply WAL mode and `PRAGMA foreign_keys = ON` right after creation. Return the shared instance from a function so that all modules share one connection.

## Learnings

- **`fetch(req)` handler for all routes** → **`routes` object (Bun v1.2.3+).** The `routes` map separates route declarations from the 404 fallback. The `fetch` function handles only unmatched requests.

- **`db.prepare()` on every request** → **`db.query()` for hot paths.** `db.query()` caches the compiled statement up to 20 entries. Calling `db.prepare()` inside a request handler compiles the statement on every call.

- **`ALTER TABLE` without a column check** → **check `PRAGMA table_info` first.** SQLite throws an error if you add a column that already exists. Read `PRAGMA table_info(table)` before running `ALTER TABLE` in a startup migration.

## Agent rules

- ALWAYS use the `routes` object in `Bun.serve` and reserve `fetch` for the 404 fallback only.
- ALWAYS open `bun:sqlite` with `{ strict: true }` to catch parameter name typos at runtime.
- ALWAYS run `PRAGMA journal_mode = WAL` and `PRAGMA foreign_keys = ON` after opening the database.
- NEVER call `db.prepare()` inside a request handler.
- ALWAYS wrap multi-step writes in `db.transaction()` to keep the database consistent.
- ALWAYS check `PRAGMA table_info` before running `ALTER TABLE` in a startup migration.
