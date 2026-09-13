"""
MCP Tools Configuration for CME Incident Management (Lab 5).

Connects Google ADK agents to the CME Incident Management MCP Server
running on Streamable HTTP transport at cloud run.
"""

from google.auth.transport.requests import Request

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from google.oauth2.id_token import fetch_id_token
import os

MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://cme-incident-mcp-1064748107249.us-central1.run.app",
)

def get_mcp_auth_headers(ctx):
    """
    Generate a fresh Google-signed ID token for the private
    MCP Cloud Run service.
    """

    token = fetch_id_token(
        Request(),
        MCP_SERVER_URL,
    )

    return {
        "Authorization": f"Bearer {token}"
    }

mcp_connection_params = StreamableHTTPConnectionParams(
    url=f"{MCP_SERVER_URL}/mcp",
    timeout=15.0,
)

# Instantiate ADK McpToolset wrapping the remote MCP Server
incident_mcp_toolset = McpToolset(
    connection_params=mcp_connection_params,
     header_provider=get_mcp_auth_headers,
)

# Alias for agent imports
incident_tools = incident_mcp_toolset
