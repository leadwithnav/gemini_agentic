"""
CME Incident Management MCP Server

Exposes business-level MCP tools for inspecting CME Incident data.
Translates MCP tool calls into HTTP requests to the underlying REST API.
"""

import httpx
from mcp.server.fastmcp import FastMCP

REST_API_BASE_URL = "http://127.0.0.1:8001"
HTTP_TIMEOUT = 5.0

# Initialize FastMCP Server configured for Streamable HTTP transport on port 8002
mcp = FastMCP(
    "CME Incident Management MCP Server",
    host="127.0.0.1",
    port=8002,
    streamable_http_path="/mcp"
)

@mcp.tool()
def get_incident_by_id(incident_id: str) -> dict:
    """
    Retrieve details for a specific CME incident by its unique ID (e.g., 'INC-101').
    """
    normalized_id = incident_id.strip().upper()
    print(f"[MCP] get_incident_by_id called incident_id={normalized_id}", flush=True)
    print("[MCP] Calling Incident REST API", flush=True)

    url = f"{REST_API_BASE_URL}/incidents/{normalized_id}"

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"found": False, "error": f"Incident '{normalized_id}' not found"}
            else:
                return {"found": False, "error": "Incident service unavailable"}
    except (httpx.RequestError, httpx.TimeoutException, Exception):
        return {"found": False, "error": "Incident service unavailable"}


@mcp.tool()
def get_incidents_by_symbol(symbol: str) -> dict:
    """
    Retrieve all CME incidents associated with a specific trading product symbol (e.g., 'NQ', 'ES', 'CL', 'GC').
    """
    normalized_symbol = symbol.strip().upper()
    print(f"[MCP] get_incidents_by_symbol called symbol={normalized_symbol}", flush=True)
    print("[MCP] Calling Incident REST API", flush=True)

    url = f"{REST_API_BASE_URL}/incidents"
    params = {"symbol": normalized_symbol}

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"found": False, "error": f"No incidents found for symbol '{normalized_symbol}'"}
            else:
                return {"found": False, "error": "Incident service unavailable"}
    except (httpx.RequestError, httpx.TimeoutException, Exception):
        return {"found": False, "error": "Incident service unavailable"}


if __name__ == "__main__":
    print("[MCP] Starting CME Incident Management MCP Server on http://127.0.0.1:8002/mcp ...", flush=True)
    mcp.run(transport="streamable-http")
