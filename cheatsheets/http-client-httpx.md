# Outbound HTTP clients with httpx

_Grounded in JasonLo's repos as of 2026-06-05; current practice per encode/httpx official docs (context7 `/encode/httpx`)._

## Reference snippet

```python
import httpx

# Sync — reuse one Client (connection pool + shared config), close via context manager.
with httpx.Client(base_url="https://api.example.com", timeout=10.0) as client:
    r = client.get("/users", params={"limit": 50})
    r.raise_for_status()
    data = r.json()

# Async — same lifecycle, awaited.
async def fetch() -> dict:
    async with httpx.AsyncClient(base_url="https://api.example.com", timeout=10.0) as client:
        r = await client.get("/users")
        r.raise_for_status()
        return r.json()
```

## Typical usage patterns

- Reusable fetch helper takes an injected `httpx.Client` and wraps it in tenacity retry (`retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))`), then `raise_for_status()` → `.json()` — for flaky upstream JSON APIs (`JasonLo/best-in-slot:slots/python-web/httpx/example/httpx_example/client.py`).
- Canonical sync/async/FastAPI-shared-client/respx-mock recipes kept as a reference slot (`JasonLo/best-in-slot:slots/python-web/httpx/CHEATSHEET.md`).
- One-shot POSTs to push sensor data to HTTP APIs via module-level `httpx.post(url, headers=..., json=...)` / `content=...`, then `raise_for_status()` — note: no Client reuse and no explicit timeout (`JasonLo/dazzo-monitor:server/push.py`).
- Long-lived `httpx.Client(base_url=..., headers={"Authorization": ...})` for an authenticated REST API, posting then reading `.json()` — pattern seen, but built without an explicit timeout and not used as a context manager.
- Per-call `httpx.Client(timeout=...)` opened inside a `with` for a single request, with a configurable timeout env var — correct lifecycle but a fresh client per call; for slow generation endpoints a large timeout is set deliberately.
- `httpx.get(..., follow_redirects=True)` for endpoints that 30x to the real resource.

## Learnings

- **Reach for module-level `httpx.get`/`httpx.post` per request** → **reuse one `Client`/`AsyncClient` across requests.** The request-level API opens and tears down a fresh connection (and TLS handshake) every call; a shared client keeps a connection pool and shared headers/base_url, which is the real win for repeated outbound calls.
- **Treat a `Client` as a fire-and-forget object** → **a `Client` owns a connection pool that must be released.** Use it as a context manager (or `close()`/`aclose()`); a long-lived client that is never closed leaks connections — especially an async client whose lifecycle should bind to the app (FastAPI lifespan), not a request.
- **Rely on the implicit default timeout** → **set the timeout explicitly per client/use case.** httpx defaults to 5s, but `timeout=None` disables it entirely; leaving it implicit means a hung upstream can stall the caller. Pick a value that fits the endpoint (short for APIs, long for generation), don't inherit it by accident.
- **Build retry/error handling around request semantics ad hoc** → **let `raise_for_status()` be the single failure gate and retry on the httpx exception hierarchy.** Catch `HTTPStatusError` (4xx/5xx) vs `TimeoutException`/`HTTPError` (transport) deliberately, and retry only the transient ones with backoff rather than blanket-retrying everything.
- **Assume redirects are followed** → **opt in with `follow_redirects=True` when needed.** httpx does not follow redirects by default (unlike requests); silent empty/302 responses come from forgetting this.

## Agent rules

- ALWAYS reuse a single `httpx.Client` / `httpx.AsyncClient` across multiple requests instead of module-level `httpx.get`/`httpx.post`.
- ALWAYS manage a client's lifecycle: use it as a context manager, or pair construction with `close()`/`aclose()`.
- ALWAYS bind an `AsyncClient`'s lifecycle to the application (e.g. FastAPI lifespan/startup-shutdown), not to a single request.
- ALWAYS pass an explicit `timeout=` to the client or call; never leave it implicit for production calls.
- ALWAYS call `response.raise_for_status()` before reading `.json()`/`.content`.
- ALWAYS retry only transient errors (`httpx.TimeoutException`, transport `httpx.HTTPError`) with backoff; handle `httpx.HTTPStatusError` separately.
- ALWAYS set `follow_redirects=True` explicitly when an endpoint redirects.
- NEVER create a new `Client` per request when the calls share a host/config.
- NEVER set `timeout=None` (disables all timeouts) unless a single specific call genuinely needs unbounded waiting.
