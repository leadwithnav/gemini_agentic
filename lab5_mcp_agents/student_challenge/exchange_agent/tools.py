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

# TODO 1:
# Configure Streamable HTTP connection to:
#
# http://127.0.0.1:8002/mcp

mcp_connection_params = StreamableHTTPConnectionParams(
    url=____________________________________
)


# ============================================================
# 2. CREATE MCP TOOLSET
# ============================================================

# TODO 2:
# Create an ADK McpToolset using the
# connection parameters defined above.

exchange_mcp_toolset = McpToolset(
    connection_params=____________________________________
)