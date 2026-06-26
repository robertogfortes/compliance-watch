"""
ComplianceWatch MCP server entry point.

Run for development inspection:
    mcp dev mcp_server/server.py

Register in Claude Code:
    claude mcp add compliance uv run mcp_server/server.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ComplianceWatchMCP", log_level="ERROR")

# Side-effect imports register tools, resources, and prompts onto the mcp instance
import mcp_server.tools       # noqa: E402, F401
import mcp_server.resources   # noqa: E402, F401
import mcp_server.prompts     # noqa: E402, F401

if __name__ == "__main__":
    mcp.run(transport="stdio")
