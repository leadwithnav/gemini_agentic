"""
CME Exchange Information Assistant - Tools

Provides deterministic Python tools for:
1. Retrieving CME Group exchange information
2. Listing products associated with an exchange
"""


# ============================================================
# SIMULATED EXCHANGE DATA
# ============================================================

EXCHANGES = {
    "CME": {
        "name": "Chicago Mercantile Exchange",
        "location": "Chicago",
        "description": "Offers products across multiple asset classes."
    },
    "CBOT": {
        "name": "Chicago Board of Trade",
        "location": "Chicago",
        "description": "Known for agricultural and financial products."
    },
    "NYMEX": {
        "name": "New York Mercantile Exchange",
        "location": "New York",
        "description": "Known primarily for energy products."
    },
    "COMEX": {
        "name": "Commodity Exchange",
        "location": "New York",
        "description": "Known primarily for metals products."
    }
}


# ============================================================
# SIMULATED PRODUCT DATA
# ============================================================

PRODUCTS = {
    "CME": ["ES", "NQ"],
    "CBOT": ["ZC", "ZW"],
    "NYMEX": ["CL", "NG"],
    "COMEX": ["GC", "SI"]
}


# ============================================================
# TOOL 1: GET EXCHANGE DETAILS
# ============================================================

def get_exchange_details(exchange: str) -> dict:
    """
    Retrieve information about a CME Group exchange.

    Use this tool when the user asks for details about an exchange,
    such as its name, location, or description.

    Args:
        exchange: Exchange code such as CME, CBOT, NYMEX, or COMEX.

    Returns:
        A dictionary containing the exchange name, location,
        and description. Returns an error if the exchange
        is not supported.
    """

    exchange = exchange.strip().upper()

    if exchange not in EXCHANGES:
        return {
            "error": f"Exchange {exchange} not found"
        }

    return {
        "exchange": exchange,
        **EXCHANGES[exchange]
    }


# ============================================================
# TOOL 2: LIST PRODUCTS BY EXCHANGE
# ============================================================

def list_products_by_exchange(exchange: str) -> dict:
    """
    List the simulated futures products associated with a CME Group exchange.

    Use this tool when the user asks which products belong to,
    are available on, or are associated with a particular exchange.

    Args:
        exchange: Exchange code such as CME, CBOT, NYMEX, or COMEX.

    Returns:
        A dictionary containing the exchange code and its associated
        product symbols. Returns an error if the exchange is not supported.
    """

    exchange = exchange.strip().upper()

    if exchange not in PRODUCTS:
        return {
            "error": f"Exchange {exchange} not found"
        }

    return {
        "exchange": exchange,
        "products": PRODUCTS[exchange]
    }