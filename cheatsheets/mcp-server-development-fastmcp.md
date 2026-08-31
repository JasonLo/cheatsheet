# MCP server development with fastmcp

_Grounded in JasonLo's repos as of 2026-08-31; current practice per [gofastmcp.com](https://gofastmcp.com) (v4.0)._

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
- In-memory test client for MCP protocol-layer tests: `async with Client(mcp) as client: result = await client.call_tool("name", {args})` — no network, no subprocess; direct function calls also work for pure logic unit tests since `@mcp.tool` preserves the decorated symbol as the original callable in fastmcp v3+/v4 (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/example/tests/`)
- Transport selection: `mcp.run()` (stdio, local/Claude Desktop); `mcp.run(transport="http", host="0.0.0.0", port=8000)` for hosted/multi-client; register via `claude mcp add <name> --command <binary>` (stdio) or `--transport http --url http://host:port/mcp` (HTTP)

## Learnings

- **`@mcp.tool` preserves the decorated symbol as the original callable** → in fastmcp v3+/v4, `@mcp.tool` no longer rebinds the name to a FunctionTool; the decorated function remains directly callable for pure unit tests; the `FASTMCP_DECORATOR_MODE="object"` backward-compat flag was eliminated in v4.0; use `Client.call_tool()` when testing full MCP protocol-layer behavior (schema validation, transport)
- **`print()` to stdout corrupts the stdio protocol** → the MCP wire format is JSON-RPC over stdin/stdout; route all logging to a file (`logging.basicConfig(filename="server.log", ...)`) or stderr; never `print()` when the stdio transport is active (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/README.md`)
- **SSE transport is now legacy** → Streamable HTTP replaced SSE as the non-stdio standard; use `transport="http"` for hosted deployments; SSE is retained for backward compatibility only, not for new projects

## Agent rules

- ALWAYS route all logging to a file or stderr when using stdio transport; NEVER use `print()` to stdout.
- ALWAYS use `async with Client(mcp) as client` for MCP integration tests (protocol-layer behavior, schema validation); for pure function-logic unit tests, calling the decorated function directly is also valid — `@mcp.tool` preserves the original callable in fastmcp v3+/v4.
- ALWAYS use `@mcp.tool` (bare) for simple tools; use `@mcp.tool(name=..., timeout=..., run_in_thread=False)` only when the defaults need overriding.
- ALWAYS use `transport="http"` for hosted or multi-client deployments; NEVER start a new project on SSE transport.
- NEVER store state in module-level globals; persist state via Resources or an external store — each tool call is independent.
