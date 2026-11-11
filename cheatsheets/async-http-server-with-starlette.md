# Async HTTP server with starlette

_Grounded in JasonLo's repos as of 2026-11-11. Current practice is from starlette.io._

## Reference snippet

```python
# Install: pip install starlette uvicorn
import contextlib
from starlette.applications import Starlette
from starlette.concurrency import run_in_threadpool
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

@contextlib.asynccontextmanager
async def lifespan(app):
    # startup: open DB connections, set thread pool size
    yield
    # shutdown: close connections

def blocking_query(user_id: int) -> dict:
    # blocking I/O: DB, file, external service
    return {"user_id": user_id}

async def user_detail(request):
    user_id = request.path_params["user_id"]
    result = await run_in_threadpool(blocking_query, user_id)
    return JSONResponse(result)

app = Starlette(
    routes=[Route("/users/{user_id:int}", user_detail, methods=["GET"])],
    lifespan=lifespan,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Typical usage patterns

- **Sync handlers in threadpool.** Use `run_in_threadpool(sync_fn, *args)` to run blocking code from an async handler. This keeps the event loop free for other requests.
- **Custom ASGI streaming with disconnect detection.** Use raw ASGI `send()` and `receive()` to stream bytes with client disconnect detection. Race a disconnect listener against the frame producer with `anyio.create_task_group()`.
- **Middleware for cross-cutting concerns.** Subclass `BaseHTTPMiddleware` and override `dispatch()` for request correlation IDs, timing, and access logging. Register it with `middleware=[Middleware(YourMiddleware)]` on the `Starlette` constructor.

## Learnings

- **`on_startup`/`on_shutdown` lists** → **`lifespan` context manager.** The `on_startup` and `on_shutdown` parameters are deprecated. Use an `asynccontextmanager` with startup code before `yield` and teardown code after it.
- **Custom route dispatcher** → **`Route` objects with path converters.** Writing a manual dispatcher duplicates what Starlette's router already does. Use `Route("/items/{id:int}", handler, methods=["GET"])` objects, which extract path parameters and check the method automatically.
- **Blocking I/O in async handler** → **`run_in_threadpool()`.** Calling blocking functions in an `async def` handler blocks the event loop. Use `await run_in_threadpool(fn, *args)` to run them in a worker thread instead.

## Agent rules

- ALWAYS use the `lifespan` async context manager instead of `on_startup` and `on_shutdown`.
- ALWAYS wrap blocking sync functions with `run_in_threadpool()` before awaiting them in an async handler.
- NEVER call blocking I/O directly inside an `async def` handler.
- ALWAYS use `Route` objects with path converters for routing; do not write a manual dispatcher.
- ALWAYS use raw ASGI `send()`/`receive()` when streaming requires disconnect detection.
- NEVER use `--reload` in a Docker or production deployment; use it only in development.
