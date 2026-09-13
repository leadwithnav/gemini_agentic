"""
STUDENT CHALLENGE 1B: STARTER PROJECT (FIX THE PRODUCT SUPPORT AGENT)

TIMEBOX: 25 Minutes

PROBLEMS WITH THIS STARTER AGENT:
---------------------------------
1. Weak System Instructions ("You are a helpful assistant") - missing safety guardrails.
2. 4 Overlapping & Vague Tools:
   - get_product(query) -> Vague name, unclear docstring.
   - get_status(p) -> Missing type hints, vague parameter 'p'.
   - get_products(category) -> Generic docstring, returns raw unformatted list.
   - get_contract(symbol) -> Overlaps with get_product(), raises raw KeyError on INVALID123!
3. Inconsistent error responses (raw unhandled exceptions throw errors to the LLM).

STUDENT GOAL:
--------------
Refactor this code into clean, well-described, non-overlapping tools with rich docstrings,
strengthen the system instructions, and handle invalid symbols like 'INVALID123' cleanly.
"""

from google.adk.agents import Agent
from ..instructor_demo.data import PRODUCTS


# ==============================================================================
# FLAWED TOOLS (FOR STUDENTS TO REFACTOR)
# ==============================================================================

def get_product(query):
    """Gets product info."""
    # PROBLEM: Vague docstring, generic parameter 'query', overlaps with get_contract()
    clean_sym = str(query).strip().upper()
    return PRODUCTS.get(clean_sym)


def get_status(p):
    """Get status."""
    # PROBLEM: Missing type hint, vague description, vague parameter 'p'
    clean_sym = str(p).strip().upper()
    if clean_sym in PRODUCTS:
        return {"status": PRODUCTS[clean_sym]["trading_status"]}
    return None


def get_products(category):
    """Get products."""
    # PROBLEM: Vague docstring, parameter name 'category' doesn't specify Asset Class
    results = []
    for item in PRODUCTS.values():
        if category.lower() in item["asset_class"].lower():
            results.append(item)
    return results


def get_contract(symbol):
    """Fetch contract details."""
    # PROBLEM: Overlaps with get_product(), raises raw KeyError if symbol isn't found!
    clean_sym = symbol.strip().upper()
    # Throws KeyError if symbol does not exist in PRODUCTS!
    return PRODUCTS[clean_sym]["contract_size"]


# ==============================================================================
# FLAWED AGENT DEFINITION (WEAK SYSTEM INSTRUCTIONS)
# ==============================================================================

starter_agent = Agent(
    name="flawed_support_agent",
    model="gemini-2.5-flash",
    description="Flawed starter agent for Student Challenge 1B.",
    instruction="You are a helpful assistant.",  # PROBLEM: Weak, generic instructions!
    tools=[
        get_product,
        get_status,
        get_products,
        get_contract,
    ],
)
