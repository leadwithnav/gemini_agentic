"""
MCP Tools Configuration for CME Incident Management (Lab 6).

Connects Google ADK agents to the CME Incident Management MCP Server
running on Streamable HTTP transport at http://127.0.0.1:8002/mcp.
"""

from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# Configure Streamable HTTP connection to the CME Incident MCP Server
mcp_connection_params = StreamableHTTPConnectionParams(
    url="http://127.0.0.1:8002/mcp"
)

# Instantiate ADK McpToolset wrapping the remote MCP Server
incident_mcp_toolset = McpToolset(
    connection_params=mcp_connection_params
)

# Alias for agent imports
incident_tools = incident_mcp_toolset
