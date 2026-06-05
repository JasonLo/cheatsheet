# Web API servers with FastAPI

_Grounded in JasonLo's repos as of 2026-06-05; current practice per official FastAPI docs (context7 `/fastapi/fastapi`, v0.128.x)._

## Reference snippet

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Request
from pydantic import BaseModel


# --- shared resource wired via lifespan, read via Depends ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()      # startup: acquire
    yield                               # serve requests
    app.state.model = None              # shutdown: release


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

# run: uv run fastapi dev   (dev)  |  uvicorn api.main:app --host 0.0.0.0 --port 8000  (prod)
```

## Typical usage patterns

- **Lifespan for model/backend warmup** — `@asynccontextmanager` loads a heavy model/client on startup, cleans up after `yield`; pre-load failures degrade to lazy-load-on-first-request. Your standard shape for any GPU/ML service.
- **`APIRouter` + `include_router(prefix=..., tags=...)`** — endpoints live in `routers/`, mounted onto a thin `main.py` app; keeps the OpenAI-compatible surface isolated from app wiring.
- **Async path operations** — `async def` handlers for I/O-bound work; `asyncio.Semaphore` caps concurrent GPU generations so requests don't starve VRAM.
- **Pydantic v2 schemas with `Field(...)`** — request/response models in a dedicated `schemas.py`, using `Field` descriptions, `Literal` enums, and `max_length` for validation + auto OpenAPI docs.
- **Typed return annotations** — handlers annotate return type (`-> dict[str, str]`) so FastAPI generates the response schema.
- **Env-driven config + `uvicorn.run` entrypoint** — `HOST`/`PORT`/`WORKERS` from `os.getenv`, a `main()` that calls `uvicorn.run("api.main:app", ...)`.
- **CORS middleware + static/sub-app mounts** — `app.add_middleware(CORSMiddleware, ...)`, `app.mount("/static", StaticFiles(...))`, optionally mounting a Gradio UI.
- **`pydantic-settings` for typed config + `@lru_cache` `get_settings` injected via `Depends`** (public: `JasonLo/best-in-slot:slots/python-web/fastapi/CHEATSHEET.md`).
- **`TestClient` as a context manager** so lifespan startup/shutdown runs during tests (public: `JasonLo/best-in-slot:slots/python-web/fastapi/CHEATSHEET.md`).
- Minimal idiomatic skeleton — typed `BaseModel` body, `/healthz`, typed returns (public: `JasonLo/best-in-slot:slots/python-web/fastapi/example/fastapi_example/main.py`).

## Learnings

- **`@app.on_event("startup")` + module-level `global` resource → lifespan context manager owning the resource.** One scope acquires *and* releases; no globals, no half-initialized state, and startup/shutdown logic that shares variables lives together. `on_event` is deprecated.
- **Module globals / direct imports for shared state → `Depends` injection (read from `app.state` or a cached factory).** Wiring becomes explicit and overridable per-request, which makes handlers testable and swappable instead of bound to import-time singletons.
- **Blocking I/O (`requests`, sync DB calls) inside a handler → either an `async` client awaited in `async def`, or keep it `def` so FastAPI offloads it to the threadpool.** A blocking call in an `async def` route stalls the whole event loop; pick the mode that matches the work.
- **`class Config:` on settings/models → pydantic v2 config (`SettingsConfigDict` / `model_config`).** FastAPI is pydantic-v2-native now; v1-style inner `Config` and `pydantic.v1` imports are the deprecated migration path, not the target.
- **Untyped handlers returning bare values → typed `BaseModel` / annotated returns.** The type *is* the contract: it drives validation, serialization, and the OpenAPI schema — not just documentation.
- **Repeated `param: T = Depends(dep)` → a reusable `Annotated[T, Depends(dep)]` alias.** Dependencies are a declared, named capability shared across routes, not boilerplate copy-pasted per signature.

## Agent rules

- ALWAYS manage startup/shutdown with an `@asynccontextmanager` `lifespan=` passed to `FastAPI(...)`.
- NEVER use `@app.on_event("startup")` / `@app.on_event("shutdown")`.
- ALWAYS store shared resources on `app.state` and read them through a `Depends` provider.
- NEVER reach for module-level `global` singletons or import-time state to share resources across handlers.
- ALWAYS make a handler that does blocking I/O either `async def` with an awaited async client, or plain `def` (let FastAPI threadpool it).
- NEVER call blocking I/O (`requests`, sync DB drivers) directly inside an `async def` route.
- ALWAYS define request/response shapes as pydantic v2 `BaseModel`s with `Field(...)` and annotate handler return types.
- NEVER use pydantic v1 `class Config:`; use `model_config` / `SettingsConfigDict`.
- ALWAYS group routes in `APIRouter` and attach via `app.include_router(prefix=..., tags=...)`.
- ALWAYS hoist repeated dependencies into a reusable `Annotated[T, Depends(dep)]` alias.
- ALWAYS gate scarce resources (e.g. GPU) with `asyncio.Semaphore` in async handlers.
- ALWAYS run dev via `fastapi dev` and prod via `uvicorn <module>:app`.
- ALWAYS enter `TestClient` as a context manager so lifespan runs in tests.
