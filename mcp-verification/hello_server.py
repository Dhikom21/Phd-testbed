"""
Hello-world MCP server. Exposes one tool that echoes input.
Just to prove the dev setup works before wrapping the real verification layer.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-server")


@mcp.tool()
def echo(message: str) -> str:
    """Echo back whatever the caller sends. Useful as a sanity check."""
    return f"Hello from MCP! You said: {message}"


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


if __name__ == "__main__":
    mcp.run()
