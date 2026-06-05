# Lightweight TS web services with Hono

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Hono official docs (context7 `/honojs/hono`, README + MIGRATION + client types)._

## Reference snippet

```ts
// app.ts — the app is just a Fetch handler; keep it free of any runtime entry code.
import { Hono } from "hono";
import { logger } from "hono/logger";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

// Type the env once: c.set/c.get -> Variables, platform env -> Bindings.
type Bindings = { DB_URL: string };
type Variables = { requestId: string };

// Chain routes off the constructor so RPC/`hc` can infer response types.
const app = new Hono<{ Bindings: Bindings; Variables: Variables }>()
  .use("*", logger())
  .get("/healthz", (c) => c.json({ status: "ok" }))
  .post(
    "/hello",
    zValidator("json", z.object({ name: z.string().min(1) })),
    (c) => {
      const { name } = c.req.valid("json"); // typed from the schema
      return c.json({ msg: `hello, ${name}` }, 201); // explicit status
    }
  );

export default app; // export the app; pick a runtime entry separately
```

```ts
// index.ts — runtime entry. Node:  import { serve } from "@hono/node-server"; serve(app)
//             Bun:   export default { port, fetch: app.fetch }
//             Workers: export default app   (app IS the fetch handler)
import app from "./app";
export default { port: 3000, fetch: app.fetch };
```

## Typical usage patterns

- Split `app.ts` (routes) from `index.ts` (runtime entry); entry only wires `fetch: app.fetch`. Lets the same app target Bun/Workers/Node unchanged. (`JasonLo/best-in-slot:slots/web-ts/hono/example/src/index.ts`, `JasonLo/md-render:src/index.ts`)
- `GET /healthz` returning `c.json({ status: "ok" })` as a liveness probe — first route on every service. (`JasonLo/best-in-slot:slots/web-ts/hono/example/src/app.ts`)
- Path params via `c.req.param("name")`, query via `c.req.query("url")`; respond with `c.json`/`c.html` and an explicit status arg on errors. (`JasonLo/md-render:src/index.ts`)
- Custom error class caught in the handler, mapped to `c.html(page, err.status)` — error-to-response mapping lives in the route, not a global handler. (`JasonLo/md-render:src/index.ts`)
- Validation through `@hono/zod-validator` `zValidator("json", schema)` + `c.req.valid("json")` for typed input. (`JasonLo/best-in-slot:slots/web-ts/hono/CHEATSHEET.md`)
- Route grouping via sub-`new Hono()` mounted with `app.route("/users", users)`. (`JasonLo/best-in-slot:slots/web-ts/hono/CHEATSHEET.md`)
- Built-in middleware composed in `app.use("*", logger(), cors())`. (`JasonLo/best-in-slot:slots/web-ts/hono/CHEATSHEET.md`)
- Tests hit `app.request("/path")` directly with `bun:test` — no server boot, asserts on the `Response`. (`JasonLo/best-in-slot:slots/web-ts/hono/example/src/app.test.ts`)
- Pinned `hono ^4.x` on `"type": "module"`, Bun dev/start scripts. (`JasonLo/md-render:package.json`)

## Learnings

- **"A web framework owns its own HTTP server" → "Hono is a Fetch handler; the runtime owns the server."** Keep the app a portable `fetch` and choose the adapter at the edge — so one codebase runs on Workers, Bun, and Node without rewrites.
- **Untyped `new Hono()` → typed `Hono<{ Bindings; Variables }>`.** Declaring env/var generics once makes `c.env`, `c.get`, and `c.set` type-safe instead of `any` — the type info is the point, not a cosmetic.
- **Defining routes as loose statements → chaining routes off the constructor.** `c.json(x, status)` literals plus chaining feed Hono's RPC (`hc`) type inference; detached `app.get(...)` statements lose the response types a typed client needs.
- **Hand-rolled body parsing/validation → schema validator middleware.** `zValidator(target, schema)` + `c.req.valid(target)` replaces manual `parseBody` + ad-hoc checks; validation becomes declarative and the validated shape is typed at the handler.
- **Booting a server (or mocking HTTP) to test → calling `app.request()`.** The app is already a request→Response function; invoke it in-process for fast, hermetic tests.
- **Returning bare bodies / implicit 200 → explicit `c.json(body, status)` with a deliberate code.** Status as a typed argument keeps error paths honest and preserves per-status types for RPC clients.

## Agent rules

- ALWAYS keep the app a portable Fetch handler; export the `Hono` instance and put runtime/server wiring in a separate entry file.
- ALWAYS pick the runtime adapter at the entry: `@hono/node-server` `serve()` for Node, `{ fetch: app.fetch }` for Bun, `export default app` for Workers.
- ALWAYS type the app as `new Hono<{ Bindings: ...; Variables: ... }>()` so `c.env`, `c.get`, and `c.set` are typed.
- ALWAYS chain routes off the constructor and call `c.json(body, status)` with explicit literals to preserve RPC/`hc` type inference.
- ALWAYS validate input with `@hono/zod-validator` `zValidator(target, schema)` and read it via `c.req.valid(target)`.
- ALWAYS test handlers with `app.request(path, init)` in-process and assert on the returned `Response`.
- ALWAYS group related routes with a sub-`new Hono()` mounted via `app.route(prefix, sub)`.
- ALWAYS expose a `GET /healthz` returning `c.json({ status: "ok" })`.
- NEVER bind Hono to a runtime-specific HTTP server inside the app module.
- NEVER hand-roll request-body parsing or ad-hoc validation when a schema validator middleware applies.
- NEVER return a response without a deliberate status on non-200 paths.
- NEVER spin up a real server or mock `fetch` just to test a route.
