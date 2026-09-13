"""
CME Exchange Information Assistant - Tools

These tools provide deterministic, simulated data for the student lab.

Available tools:
1. get_exchange_details()
2. list_products_by_exchange()
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
    Retrieve details about a CME Group exchange.

    Use this tool when the user asks for information such as:
    - exchange name
    - exchange location
    - exchange description
    - general information about an exchange

    Supported exchange codes:
    - CME
    - CBOT
    - NYMEX
    - COMEX

    Args:
        exchange:
            The exchange code, for example:
            "CME", "CBOT", "NYMEX", or "COMEX".

    Returns:
        A dictionary containing:
        - exchange
        - name
        - location
        - description

        If the exchange is not supported, an error is returned.
    """

    exchange = exchange.strip().upper()

    if exchange not in EXCHANGES:
        return {
            "error": f"Exchange {exchange} not found",
            "supported_exchanges": list(EXCHANGES.keys())
        }

    details = EXCHANGES[exchange]

    return {
        "exchange": exchange,
        "name": details["name"],
        "location": details["location"],
        "description": details["description"]
    }


# ============================================================
# TOOL 2: LIST PRODUCTS BY EXCHANGE
# ============================================================

def list_products_by_exchange(exchange: str) -> dict:
    """
    Retrieve the simulated product symbols associated with
    a CME Group exchange.

    Use this tool when the user asks questions such as:
    - Which products belong to COMEX?
    - What products are available on NYMEX?
    - List products associated with CBOT.
    - Which product symbols are available for CME?

    Supported exchange codes:
    - CME
    - CBOT
    - NYMEX
    - COMEX

    Args:
        exchange:
            The exchange code, for example:
            "CME", "CBOT", "NYMEX", or "COMEX".

    Returns:
        A dictionary containing:
        - exchange
        - products

        If the exchange is not supported, an error is returned.
    """

    exchange = exchange.strip().upper()

    if exchange not in PRODUCTS:
        return {
            "error": f"Exchange {exchange} not found",
            "supported_exchanges": list(PRODUCTS.keys())
        }

    return {
        "exchange": exchange,
        "products": PRODUCTS[exchange]
    }