"""
Read-Only Market Data Tools for CME Product Support Agent (Lab 1A Demo).

Demonstrates both:
1. POOR TOOL SEMANTICS (Instructor Demo): Vague function/docstring 'get_data'
2. GOOD TOOL SEMANTICS: Rich type hints, clear parameter descriptions, and controlled outputs.
"""

from .data import PRODUCTS


# ==============================================================================
# INSTRUCTOR DEMONSTRATION: POOR TOOL SEMANTICS (BAD EXAMPLE)
# ==============================================================================
def get_data(value: str):
    """Gets data."""
    # Vague function name ('get_data')
    # Vague docstring ('Gets data.')
    # Generic parameter name ('value')
    # No type annotations or structured return specification
    clean_val = str(value).strip().upper()
    if clean_val in PRODUCTS:
        return PRODUCTS[clean_val]
    return "Not found"


# ==============================================================================
# INSTRUCTOR DEMONSTRATION: GOOD TOOL SEMANTICS (RECOMMENDED PRODUCTION PATTERN)
# ==============================================================================
def get_product_details(symbol: str) -> dict:
    """Retrieves full descriptive information and contract specifications for a CME futures product by symbol.

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, GC, 6E, or ZC.

    Returns:
        Structured dictionary containing contract metadata if found, or error status dict if not found.
    """
    clean_symbol = symbol.strip().upper()
    if clean_symbol in PRODUCTS:
        result = dict(PRODUCTS[clean_symbol])
        result["found"] = True
        result["is_simulated_data"] = True
        return result

    return {
        "found": False,
        "symbol": clean_symbol,
        "message": f"Product '{clean_symbol}' was not found in the simulated market dataset."
    }


def get_market_status(symbol: str) -> dict:
    """Retrieves the current simulated trading status (OPEN or CLOSED) for a CME market product.

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, GC, 6E, or ZC.

    Returns:
        Dictionary containing symbol, trading status, and simulated data flag.
    """
    clean_symbol = symbol.strip().upper()
    if clean_symbol in PRODUCTS:
        product = PRODUCTS[clean_symbol]
        return {
            "found": True,
            "symbol": clean_symbol,
            "name": product["name"],
            "status": product["trading_status"],
            "is_simulated_data": True
        }

    return {
        "found": False,
        "symbol": clean_symbol,
        "message": f"Product '{clean_symbol}' was not found in the simulated market dataset."
    }


def list_products_by_asset_class(asset_class: str) -> list:
    """Lists all available CME market products belonging to a specific asset class category.

    Args:
        asset_class: Asset class category such as 'Equity Index', 'Energy', 'Metals', 'FX', or 'Agriculture'.

    Returns:
        List of product metadata dictionaries matching the requested asset class.
    """
    clean_ac = asset_class.strip().lower()
    matching_products = []

    for product in PRODUCTS.values():
        if product["asset_class"].lower() == clean_ac or clean_ac in product["asset_class"].lower():
            prod_copy = dict(product)
            prod_copy["is_simulated_data"] = True
            matching_products.append(prod_copy)

    return matching_products
