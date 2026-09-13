"""
Read-Only Market Data Tools for CME Product Support Agent (Lab 1).

Design Principles:
- One clear business capability per tool.
- Minimal overlap between tools.
- Explicit guidance for when a tool SHOULD and SHOULD NOT be used.
- Full type annotations and clear docstrings for LLM tool selection.
- Structured responses for predictable model interpretation.
- Controlled not-found responses.
- Completely read-only access to simulated training data.
"""

from .data import PRODUCTS


def get_product_details(symbol: str) -> dict:
    """
    Retrieve static reference information for a CME futures product.

    Use this tool when the user asks about:
    - product name
    - asset class
    - exchange
    - contract size
    - currency
    - product description
    - general information about a specific product symbol

    Do NOT use this tool to determine whether a market is currently
    OPEN or CLOSED.

    For current simulated market/trading status, use get_market_status.

    Args:
        symbol:
            CME futures product ticker symbol.
            Examples: ES, NQ, CL, GC, 6E, ZC.

    Returns:
        A dictionary containing static product reference information
        when the product exists.

        If the product is not found, returns a structured not-found
        response instead of raising an exception.
    """

    clean_symbol = symbol.strip().upper()

    product = PRODUCTS.get(clean_symbol)

    if product is None:
        return {
            "found": False,
            "symbol": clean_symbol,
            "message": (
                f"Product '{clean_symbol}' was not found "
                "in the simulated training dataset."
            ),
            "is_simulated_data": True,
        }

    return {
        "found": True,
        "symbol": clean_symbol,
        "name": product["name"],
        "asset_class": product["asset_class"],
        "exchange": product["exchange"],
        "contract_size": product["contract_size"],
        "currency": product["currency"],
        "description": product["description"],
        "is_simulated_data": True,
    }


def get_market_status(symbol: str) -> dict:
    """
    Retrieve the current simulated trading status of a CME futures product.

    Use this tool ONLY when the user explicitly asks whether a product is:
    - OPEN
    - CLOSED
    - currently trading
    - available for trading
    - or asks for its market/trading status

    Do NOT call this tool for general product-information questions.

    For product name, exchange, contract size, currency, asset class,
    or description, use get_product_details instead.

    Args:
        symbol:
            CME futures product ticker symbol.
            Examples: ES, NQ, CL, GC.

    Returns:
        A dictionary containing the simulated OPEN/CLOSED trading status.

        If the product is not found, returns a structured not-found response.
    """

    clean_symbol = symbol.strip().upper()

    product = PRODUCTS.get(clean_symbol)

    if product is None:
        return {
            "found": False,
            "symbol": clean_symbol,
            "message": (
                f"Product '{clean_symbol}' was not found "
                "in the simulated training dataset."
            ),
            "is_simulated_data": True,
        }

    return {
        "found": True,
        "symbol": clean_symbol,
        "name": product["name"],
        "status": product["trading_status"],
        "is_simulated_data": True,
    }


def list_products_by_asset_class(asset_class: str) -> list:
    """
    List simulated CME futures products belonging to a requested asset class.

    Use this tool ONLY when the user asks for products within an asset class.

    Example requests:
    - "Which Energy products are available?"
    - "Show me Metals products."
    - "List Equity Index futures."
    - "What FX products are available?"

    Do NOT use this tool when the user is asking about one specific
    product symbol such as ES, CL, GC, or NQ.

    Args:
        asset_class:
            Asset class name.

            Supported examples:
            - Equity Index
            - Energy
            - Metals
            - FX
            - Agriculture

    Returns:
        A list of matching simulated product records.

        Returns an empty list when no matching asset class is found.
    """

    clean_asset_class = asset_class.strip().lower()

    matching_products = []

    for product in PRODUCTS.values():
        product_asset_class = product["asset_class"].strip().lower()

        if (
            product_asset_class == clean_asset_class
            or clean_asset_class in product_asset_class
        ):
            matching_products.append(
                {
                    "symbol": product["symbol"],
                    "name": product["name"],
                    "asset_class": product["asset_class"],
                    "exchange": product["exchange"],
                    "contract_size": product["contract_size"],
                    "currency": product["currency"],
                    "description": product["description"],
                    "is_simulated_data": True,
                }
            )

    return matching_products