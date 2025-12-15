"""
Entry point for the Client & Invoice Management MCP Server.
"""

from src.server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=5000)
