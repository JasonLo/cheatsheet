# Outbound HTTP clients with httpx

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from encode/httpx official docs (context7 `/encode/httpx`)._

## Reference snippet

```python
import httpx

# Sync. Use one Client again to share the connection pool and config. The context manager closes it.
with httpx.Client(base_url="https://api.example.com", timeout=10.0) as client:
    r = client.get("/users", params={"limit": 50})
    r.raise_for_status()
    data = r.json()

# Async. The lifecycle is the same, with await.
async def fetch() -> dict:
    async with httpx.AsyncClient(base_url="https://api.example.com", timeout=10.0) as client:
        r = await client.get("/users")
        r.raise_for_status()
        return r.json()
```

## Typical usage patterns

- **Retry helper with an injected client.** A fetch helper takes an `httpx.Client` and wraps it in a tenacity retry (`retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))`). Then it calls `raise_for_status()` and `.json()` for upstream JSON APIs that fail at random (`JasonLo/best-in-slot:slots/python-web/httpx/example/httpx_example/client.py`).
- **One client in a `with` block for one request.** The code opens `httpx.Client(timeout=...)` for a single call and reads the timeout from an environment variable. Slow generation endpoints get a large timeout.
- **Redirects only on request.** The code calls `httpx.get(..., follow_redirects=True)` for endpoints that send a 30x response to the real resource.

## Learnings

- **Each request is an independent call** → **Requests to the same host share one client**. The module-level `httpx.get` and `httpx.post` open a new connection and TLS handshake for each call. A shared `Client` keeps a connection pool and the shared headers and `base_url`.
- **A client is a simple object that needs no cleanup** → **A client owns a connection pool that you must release**. Release it with a context manager or with a call to `close()` or `aclose()`. Bind a long-lived `AsyncClient` to the application lifespan, not to one request.
- **The default timeout is enough** → **The timeout is a decision for each use case**. If you do not set it, an upstream server that stops responding can stop the caller. Use a short value for APIs and a long value for generation endpoints.

## Agent rules

- ALWAYS reuse one `httpx.Client` or `httpx.AsyncClient` across many requests, not module-level `httpx.get`/`httpx.post`.
- ALWAYS release a client with a context manager or with a call to `close()`/`aclose()`.
- ALWAYS bind the lifecycle of an `AsyncClient` to the application, for example the FastAPI lifespan.
- ALWAYS pass a specified `timeout=` to the client or call for production calls.
- ALWAYS call `response.raise_for_status()` before you read `.json()` or `.content`.
- ALWAYS retry only transient errors, for example `httpx.TimeoutException` and transport `httpx.HTTPError`, with backoff.
- ALWAYS handle `httpx.HTTPStatusError` separately from transient errors.
- ALWAYS set `follow_redirects=True` when an endpoint sends a redirect.
- NEVER create a new `Client` for each request when the calls share a host and configuration.
- NEVER set `timeout=None` unless one specific call must wait with no limit.
