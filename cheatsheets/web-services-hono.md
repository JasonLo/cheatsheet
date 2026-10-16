# Lightweight TS web services with Hono

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Hono official docs (context7 `/honojs/hono`, README + MIGRATION + client types)._

## Reference snippet

```ts
// src/app.ts: the app is a Fetch handler. Do not put runtime entry code here.
import { Hono } from "hono";
import { logger } from "hono/logger";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

// Type the env one time. Variables is for c.set and c.get. Bindings is for the platform env.
type Bindings = { DB_URL: string };
type Variables = { requestId: string };

// Chain routes on the constructor. Then RPC and `hc` can infer response types.
const app = new Hono<{ Bindings: Bindings; Variables: Variables }>()
  .use("*", logger())
  .get("/healthz", (c) => c.json({ status: "ok" }))
  .post("/hello", zValidator("json", z.object({ name: z.string().min(1) })), (c) => {
    const { name } = c.req.valid("json");          // the schema gives the type
    return c.json({ msg: `hello, ${name}` }, 201); // explicit status
  });

export default app;

// src/index.ts: runtime entry for Bun. Workers: export default app.
// Node: import { serve } from "@hono/node-server"; serve(app).
import app from "./app";

export default { port: 3000, fetch: app.fetch };
```

## Typical usage patterns

- The routes go in `app.ts`, and the runtime entry in `index.ts` only sets `fetch: app.fetch`. Then the same app runs on Bun, Workers, or Node without change. (seen in `JasonLo/best-in-slot:slots/web-ts/hono/example/src/index.ts`, `JasonLo/md-render:src/index.ts`)
- Validate input with `zValidator("json", schema)` from `@hono/zod-validator`. The handler then reads the typed input with `c.req.valid("json")`. (seen in `JasonLo/best-in-slot:slots/web-ts/hono/CHEATSHEET.md`)
- Tests call `app.request("/path")` directly with `bun:test` and assert on the `Response`, so no server starts. (seen in `JasonLo/best-in-slot:slots/web-ts/hono/example/src/app.test.ts`)

## Learnings

- **A web framework owns its HTTP server** → **Hono is a Fetch handler, and the runtime owns the server**. The app stays a portable `fetch` handler, and the entry file chooses the adapter. Then one codebase runs on Workers, Bun, and Node without rewrites.
- **Routes are separate statements** → **Routes chain on the constructor to keep their types**. Method chains and `c.json(x, status)` literals supply the type inference for the RPC client `hc` of Hono. Separate `app.get(...)` statements lose the response types that a typed client needs.
- **Parse and validate the body by hand** → **Declare a schema in validator middleware**. `zValidator(target, schema)` and `c.req.valid(target)` replace manual `parseBody` calls and custom checks. The handler then gets the validated shape as a typed value.

## Agent rules

- ALWAYS keep the app a portable Fetch handler.
- ALWAYS export the `Hono` instance from the app module.
- ALWAYS put the runtime and server setup in a separate entry file.
- ALWAYS pick the runtime adapter at the entry: `@hono/node-server` `serve()` for Node, `{ fetch: app.fetch }` for Bun, `export default app` for Workers.
- ALWAYS type the app as `new Hono<{ Bindings: ...; Variables: ... }>()`.
- ALWAYS chain routes on the constructor to keep the RPC/`hc` type inference.
- ALWAYS call `c.json(body, status)` with specified literals to keep the RPC/`hc` type inference.
- ALWAYS validate input with `@hono/zod-validator` `zValidator(target, schema)`.
- ALWAYS read validated input with `c.req.valid(target)`.
- ALWAYS test handlers in-process with `app.request(path, init)`.
- ALWAYS assert on the `Response` that `app.request` returns.
- ALWAYS group related routes in a sub-`new Hono()` that `app.route(prefix, sub)` mounts.
- ALWAYS expose a `GET /healthz` route that returns `c.json({ status: "ok" })`.
- NEVER bind Hono to a runtime-specific HTTP server inside the app module.
- NEVER parse or validate request bodies manually when a schema validator middleware applies.
- NEVER return a response on a non-200 path without a specified status.
- NEVER start a real server or mock `fetch` to test a route.
