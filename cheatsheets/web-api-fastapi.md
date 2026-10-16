# Web API servers with FastAPI

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from official FastAPI docs (context7 `/fastapi/fastapi`, v0.128.x)._

## Reference snippet

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request
from pydantic import BaseModel


# --- shared resource: lifespan sets it, Depends reads it ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()      # startup: get the resource
    yield                               # the app serves requests
    app.state.model = None              # shutdown: release the resource


def get_model(request: Request) -> Model:
    return request.app.state.model


ModelDep = Annotated[Model, Depends(get_model)]  # reusable dependency alias


class SpeakRequest(BaseModel):          # pydantic v2 schema
    text: str
    voice: str = "default"


router = APIRouter(prefix="/v1", tags=["tts"])


@router.post("/speak")
async def speak(body: SpeakRequest, model: ModelDep) -> dict[str, str]:
    return {"audio": model.run(body.text, body.voice)}


app = FastAPI(title="my-service", lifespan=lifespan)
app.include_router(router)

# run in dev: uv run fastapi dev. Run in prod: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Typical usage patterns

- An `@asynccontextmanager` lifespan loads a large model or client at startup and releases it after `yield`. If the pre-load fails, the service loads the model on the first request.
- The endpoints are in `routers/` as an `APIRouter`, and a small `main.py` mounts them with `include_router(prefix=..., tags=...)`. This keeps the OpenAI-compatible API separate from the app setup.
- Use `async def` handlers for I/O-bound work. An `asyncio.Semaphore` limits concurrent GPU generations, so requests do not use all the VRAM.

## Learnings

- **`@app.on_event("startup")` sets a module-level `global` resource** → **A lifespan context manager owns the resource.** One scope gets and releases the resource. There are no globals and no partly initialized state, and the lifespan replaces the deprecated `on_event` hooks.
- **Handlers read shared state from module globals or imports** → **Handlers receive shared state through `Depends` injection.** The provider reads `app.state` or a cached factory. You can then override the dependencies for each request and test the handler.
- **Any handler can call `requests` or sync DB code** → **Match the handler mode to the work.** Blocking I/O in `async def` stops the event loop. Use an awaited `async` client in `async def`, or a plain `def` handler that FastAPI runs in the threadpool.

## Agent rules

- ALWAYS manage startup and shutdown with an `@asynccontextmanager` function that you pass to `FastAPI(lifespan=...)`.
- NEVER use `@app.on_event("startup")` / `@app.on_event("shutdown")`.
- ALWAYS store shared resources on `app.state`.
- ALWAYS read shared resources through a `Depends` provider.
- NEVER use module-level `global` singletons or import-time state to share resources across handlers.
- ALWAYS make a blocking-I/O handler either `async def` with an awaited async client or plain `def` for the threadpool.
- NEVER call blocking I/O, for example `requests` or sync DB drivers, directly inside an `async def` route.
- ALWAYS define request and response shapes as pydantic v2 `BaseModel`s with `Field(...)`.
- ALWAYS annotate handler return types.
- NEVER use pydantic v1 `class Config:`.
- ALWAYS use `model_config` / `SettingsConfigDict` for model configuration.
- ALWAYS group routes in an `APIRouter`.
- ALWAYS attach each router with `app.include_router(prefix=..., tags=...)`.
- ALWAYS move repeated dependencies into a reusable `Annotated[T, Depends(dep)]` alias.
- ALWAYS limit resources with a small supply, for example GPU, with `asyncio.Semaphore` in async handlers.
- ALWAYS run development with `fastapi dev`.
- ALWAYS run production with `uvicorn <module>:app`.
- ALWAYS enter `TestClient` as a context manager so the lifespan runs in tests.
