# MCP server development with fastmcp

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from [gofastmcp.com](https://gofastmcp.com) (v4.0)._

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
    mcp.run()  # stdio is the default. For HTTP, use mcp.run(transport="http", host="0.0.0.0", port=8000)
```

## Typical usage patterns

- **Server construction**. A server is `FastMCP("name")` with bare `@mcp.tool` and `@mcp.resource("uri://{param}")` decorators, and the type annotations produce the JSON schema. Write a precise docstring, because the LLM sees it as the prompt. (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/example/`)
- **In-memory test client**. Protocol-layer tests use `async with Client(mcp) as client: result = await client.call_tool("name", {args})` with no network and no subprocess. Unit tests of pure logic can call the decorated function directly. (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/example/tests/`)
- **Transport selection**. The stdio form `mcp.run()` serves local use and Claude Desktop, and `mcp.run(transport="http", host="0.0.0.0", port=8000)` serves hosted or multi-client servers. Register with `claude mcp add <name> --command <binary>` for stdio or `--transport http --url http://host:port/mcp` for HTTP.

## Learnings

- **`@mcp.tool` replaces the function with a framework tool object** → **`@mcp.tool` registers the function and leaves it a plain callable**. The function stays testable as plain Python. Use `Client.call_tool()` only to test the protocol layer, for example schema validation and transport.
- **A server can print to stdout** → **Stdout is the protocol channel in the stdio transport**. MCP sends JSON-RPC over stdin and stdout, so any `print()` corrupts the stream. Send logs to a file with `logging.basicConfig(filename="server.log", ...)` or to stderr. (seen in `JasonLo/best-in-slot:slots/python-ai/fastmcp/README.md`)
- **SSE is the transport for remote servers** → **Streamable HTTP is the standard transport for remote servers**. Use `transport="http"` for hosted deployments. SSE stays only for backward compatibility and not for new projects.

## Agent rules

- ALWAYS send all logs to a file or to stderr when the server uses the stdio transport.
- NEVER use `print()` to stdout in a stdio server.
- ALWAYS use `async with Client(mcp) as client` for MCP integration tests of protocol behavior and schema validation.
- ALWAYS call the decorated function directly in unit tests of pure logic.
- ALWAYS use the bare `@mcp.tool` for simple tools.
- NEVER use `@mcp.tool(name=..., timeout=..., run_in_thread=False)` unless you must change a default.
- ALWAYS use `transport="http"` for hosted or multi-client deployments.
- NEVER start a new project on the SSE transport.
- NEVER store state in module-level globals.
- ALWAYS keep state in Resources or in an external store.
