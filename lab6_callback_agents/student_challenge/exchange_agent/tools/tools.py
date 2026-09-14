"""
Lab 5 Student Challenge:
MCP Tool Configuration

Goal:
Connect the ADK agent to the Exchange MCP Server
using Streamable HTTP.
"""

from google.adk.tools.mcp_tool import (
    McpToolset,
    StreamableHTTPConnectionParams,
)


# ============================================================
# 1. CONFIGURE MCP CONNECTION
# ============================================================

mcp_connection_params = StreamableHTTPConnectionParams(
    url="http://127.0.0.1:8002/mcp"
)


# ============================================================
# 2. CREATE MCP TOOLSET
# ============================================================

exchange_mcp_toolset = McpToolset(
    connection_params=mcp_connection_params
)