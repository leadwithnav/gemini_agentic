import os
import requests

from fastmcp import FastMCP
import google.auth.transport.requests
import google.oauth2.id_token


mcp = FastMCP("CME Incident MCP")

INCIDENT_API_URL = os.getenv(
    "INCIDENT_API_URL",
    "https://cme-incident-api-1064748107249.us-central1.run.app",
)

HTTP_TIMEOUT = 10


def auth_headers() -> dict:
    """Generate an ID token for the private Cloud Run REST API."""

    auth_request = google.auth.transport.requests.Request()

    token = google.oauth2.id_token.fetch_id_token(
        auth_request,
        INCIDENT_API_URL,
    )

    return {
        "Authorization": f"Bearer {token}"
    }


@mcp.tool()
def get_incident_by_id(incident_id: str) -> dict:
    """
    Retrieve details for a specific CME incident by its unique ID
    (e.g., INC-101).

    Use this tool when incident details such as status, severity,
    affected symbol, issue description, or root cause are required.

    Args:
        incident_id: Unique incident identifier such as INC-101.

    Returns:
        Incident details or structured error information.
    """

    normalized_id = incident_id.strip().upper()

    try:
        response = requests.get(
            f"{INCIDENT_API_URL}/incidents/{normalized_id}",
            headers=auth_headers(),
            timeout=HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            return {
                "found": False,
                "error": f"Incident '{normalized_id}' not found",
            }

        return {
            "found": False,
            "error": "Incident service unavailable",
            "status_code": response.status_code,
        }

    except requests.Timeout:
        return {
            "found": False,
            "error": "Incident service timeout",
        }

    except requests.RequestException:
        return {
            "found": False,
            "error": "Incident service unavailable",
        }

    except Exception:
        return {
            "found": False,
            "error": "Unexpected MCP error",
        }


@mcp.tool()
def get_incidents_by_symbol(symbol: str) -> dict:
    """
    Retrieve CME incidents associated with a trading product symbol
    such as NQ, ES, CL, or GC.

    Use this tool when a user asks about incidents, outages,
    or operational issues affecting a CME product.

    Args:
        symbol: CME product symbol such as NQ, ES, CL, or GC.

    Returns:
        Matching incidents or structured error information.
    """

    normalized_symbol = symbol.strip().upper()

    try:
        response = requests.get(
            f"{INCIDENT_API_URL}/incidents",
            params={"symbol": normalized_symbol},
            headers=auth_headers(),
            timeout=HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            return {
                "found": False,
                "error": f"No incidents found for symbol '{normalized_symbol}'",
            }

        return {
            "found": False,
            "error": "Incident service unavailable",
            "status_code": response.status_code,
        }

    except requests.Timeout:
        return {
            "found": False,
            "error": "Incident service timeout",
        }

    except requests.RequestException:
        return {
            "found": False,
            "error": "Incident service unavailable",
        }

    except Exception:
        return {
            "found": False,
            "error": "Unexpected MCP error",
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
    )