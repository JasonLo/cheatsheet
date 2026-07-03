# MCP server development with fastmcp

_Grounded in JasonLo's repos as of 2026-07-03; current practice per [gofastmcp.com](https://gofastmcp.com) (v3.4.2)._

## Reference snippet

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers. Docstring is the LLM-visible description."""
    return a + b

@mcp.resource("memo://{topic}")
def get_memo(topic: str) -> str:
    return f"Notes on {topic}"

if __name__ == "__main__":
    mcp.run()  # stdio (default); swap for mcp.run(transport="http", host="0.0.0.0", port=8000)
```

## Typical usage patterns

- Server construction: `FastMCP("name")` + bare `@mcp.tool` / `@mcp.resource("uri://{param}")` decorators; type annotations drive the JSON schema; docstring is the LLM-visible prompt — keep it precise (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/example/`)
- In-memory test client: `async with Client(mcp) as client: result = await client.call_tool("name", {args})` — no network, no subprocess; read resources with `await client.read_resource("uri")`; `asyncio_mode = "auto"` in `pyproject.toml` removes the `@pytest.mark.asyncio` decorator requirement (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/example/tests/`)
- Transport selection: `mcp.run()` (stdio, local/Claude Desktop); `mcp.run(transport="http", host="0.0.0.0", port=8000)` for hosted/multi-client; register via `claude mcp add <name> --command <binary>` (stdio) or `--transport http --url http://host:port/mcp` (HTTP)

## Learnings

- **`@mcp.tool` rebinds the symbol to a Tool object, not the original function** → tests and callers must go through `Client.call_tool()`, never the decorated name directly; the original callable is gone after decoration (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/README.md`)
- **`print()` to stdout corrupts the stdio protocol** → the MCP wire format is JSON-RPC over stdin/stdout; route all logging to a file (`logging.basicConfig(filename="server.log", ...)`) or stderr; never `print()` when the stdio transport is active (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/README.md`)
- **SSE transport is now legacy** → Streamable HTTP replaced SSE as the non-stdio standard in fastmcp 2.3.0; use `transport="http"` for hosted deployments; SSE is retained for backward compatibility only, not for new projects

## Agent rules

- ALWAYS route all logging to a file or stderr when using stdio transport; NEVER use `print()` to stdout.
- ALWAYS test tool calls through `async with Client(mcp) as client`; NEVER call a `@mcp.tool`-decorated name directly (it is a Tool object, not the original function).
- ALWAYS use `@mcp.tool` (bare) for simple tools; use `@mcp.tool(name=..., timeout=..., run_in_thread=False)` only when the defaults need overriding.
- ALWAYS use `transport="http"` for hosted or multi-client deployments; NEVER start a new project on SSE transport.
- NEVER store state in module-level globals; persist state via Resources or an external store — each tool call is independent.
