"""
STUDENT CHALLENGE 1B: COMPLETED REFERENCE SOLUTION

This solution demonstrates how to refactor the flawed starter agent:
1. Replaced weak instructions with clear enterprise system instructions & safety guardrails.
2. Eliminated overlapping tools, consolidating into 3 clean, well-described tools.
3. Added explicit type hints, Google-style docstrings, and parameter descriptions.
4. Handled missing symbols (e.g. INVALID123) with controlled error dictionaries instead of raw exceptions.
"""

from google.adk.agents import Agent
from ..instructor_demo.data import PRODUCTS


# ==============================================================================
# REFACTORED & IMPROVED TOOLS
# ==============================================================================

def get_product_details(symbol: str) -> dict:
    """Retrieves full descriptive metadata and contract specification for a futures product using its ticker symbol.

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, GC, 6E, or ZC.

    Returns:
        Dictionary containing contract metadata if found, or an error status dictionary if not found.
    """
    clean_symbol = symbol.strip().upper()
    if clean_symbol in PRODUCTS:
        result = dict(PRODUCTS[clean_symbol])
        result["found"] = True
        return result

    return {
        "found": False,
        "symbol": clean_symbol,
        "message": f"Product '{clean_symbol}' was not found in the training dataset."
    }


def get_market_status(symbol: str) -> dict:
    """Retrieves the current simulated trading status (OPEN or CLOSED) for a CME market product.

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, GC, 6E, or ZC.

    Returns:
        Dictionary containing the symbol and current trading status.
    """
    clean_symbol = symbol.strip().upper()
    if clean_symbol in PRODUCTS:
        return {
            "found": True,
            "symbol": clean_symbol,
            "name": PRODUCTS[clean_symbol]["name"],
            "status": PRODUCTS[clean_symbol]["trading_status"]
        }

    return {
        "found": False,
        "symbol": clean_symbol,
        "message": f"Product '{clean_symbol}' was not found in the training dataset."
    }


def list_products_by_asset_class(asset_class: str) -> list:
    """Lists all available CME market products belonging to a specified asset class.

    Args:
        asset_class: Asset class category such as 'Equity Index', 'Energy', 'Metals', 'FX', or 'Agriculture'.

    Returns:
        List of matching product metadata dictionaries.
    """
    clean_ac = asset_class.strip().lower()
    matching = []
    for item in PRODUCTS.values():
        if item["asset_class"].lower() == clean_ac or clean_ac in item["asset_class"].lower():
            matching.append(dict(item))
    return matching


# ==============================================================================
# REFACTORED SYSTEM INSTRUCTIONS & AGENT DEFINITION
# ==============================================================================

SOLUTION_SYSTEM_INSTRUCTION = """
You are an internal CME Market Product Support Agent.

RESPONSIBILITIES:
- Retrieve factual product specifications, contract sizes, and asset classes using tools.
- Retrieve simulated market trading status (OPEN / CLOSED).
- List products belonging to a specified asset class.

TOOL POLICY:
- Use available tools for factual product queries. Do not invent product details or statuses.
- Rely on tool execution output for factual responses.

SAFETY & BOUNDARIES:
- Strictly READ-ONLY informational agent.
- NEVER execute, place, modify, or cancel trades under any circumstances.
- NEVER provide personalized investment advice.

FAILURE HANDLING:
- If a product is not found, state clearly what the tool returned.
"""

solution_agent = Agent(
    name="solution_product_support_agent",
    model="gemini-2.5-flash",
    description="Refactored CME Product Support Agent for Challenge 1B solution.",
    instruction=SOLUTION_SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
        list_products_by_asset_class,
    ],
)
