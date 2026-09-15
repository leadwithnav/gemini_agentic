"""
Read-Only Market Data Tools for CME Product Support Agent (Lab 1).

Design Principles:
- One clear business capability per tool.
- Minimal overlap between tools (get_product_details and get_market_status).
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