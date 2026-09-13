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


PRODUCTS = {
    "CME": ["ES", "NQ"],
    "CBOT": ["ZC", "ZW"],
    "NYMEX": ["CL", "NG"],
    "COMEX": ["GC", "SI"]
}


def get_exchange_details(exchange: str) -> dict:
    """
    TODO: Add a clear tool description.
    """

    exchange = exchange.upper()

    if exchange not in EXCHANGES:
        return {"error": f"Exchange {exchange} not found"}

    return EXCHANGES[exchange]


def list_products_by_exchange(exchange: str) -> dict:
    """
    TODO: Add a clear tool description.
    """

    exchange = exchange.upper()

    if exchange not in PRODUCTS:
        return {"error": f"Exchange {exchange} not found"}

    return {
        "exchange": exchange,
        "products": PRODUCTS[exchange]
    }
