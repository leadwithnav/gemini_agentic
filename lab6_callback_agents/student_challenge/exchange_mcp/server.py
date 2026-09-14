"""
CME Exchange Information MCP Server.

Exposes exchange metadata through MCP.

The MCP Server translates MCP tool calls into
HTTP calls to the Exchange REST API.
"""

import httpx

from mcp.server.mcpserver import MCPServer


REST_API_BASE_URL = "http://127.0.0.1:8001"

HTTP_TIMEOUT = 5.0


mcp = MCPServer(
    "CME Exchange Information MCP Server"
)


@mcp.tool()
def get_exchange_details(
    exchange_code: str,
) -> dict:

    """
    Retrieve information about a CME Group exchange.

    Use this tool when the user asks about:

    - exchange name
    - exchange location
    - exchange description
    - general exchange information

    Args:
        exchange_code:
            Exchange code such as CME, CBOT,
            NYMEX or COMEX.

    Returns:
        Exchange metadata returned by the
        underlying REST API.
    """

    code = exchange_code.strip().upper()

    print(
        f"[MCP] get_exchange_details({code})",
        flush=True,
    )

    url = (
        f"{REST_API_BASE_URL}"
        f"/exchanges/{code}"
    )

    try:

        with httpx.Client(
            timeout=HTTP_TIMEOUT
        ) as client:

            response = client.get(url)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 404:
                return {
                    "found": False,
                    "error":
                        f"Exchange '{code}' not found",
                }

            return {
                "found": False,
                "error":
                    "Exchange service unavailable",
            }

    except (
        httpx.RequestError,
        httpx.TimeoutException,
        Exception,
    ):

        return {
            "found": False,
            "error":
                "Exchange service unavailable",
        }


if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8002,
        streamable_http_path="/mcp",
    )