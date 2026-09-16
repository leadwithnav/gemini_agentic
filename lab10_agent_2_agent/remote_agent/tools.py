# ============================================================
# MARKET TOOL
# ============================================================

def get_market_status(product_symbol: str) -> dict:
    """
    Get the simulated market status for a CME product.

    Args:
        product_symbol: CME product symbol such as NQ, ES, CL, or GC.
    """

    market_data = {
        "NQ": "OPEN",
        "ES": "OPEN",
        "CL": "CLOSED",
        "GC": "OPEN",
    }

    symbol = product_symbol.upper().strip()
    status = market_data.get(symbol)

    if status is None:
        return {
            "product_symbol": symbol,
            "status": "NOT_FOUND",
        }

    return {
        "product_symbol": symbol,
        "status": status,
    }