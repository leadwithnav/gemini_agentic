from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-2.5-flash"


# ============================================================
# TOOL
# ============================================================

def list_products_by_exchange(exchange_code: str) -> list:

    products = {
        "CME": [
            {
                "symbol": "NQ",
                "name": "E-mini Nasdaq-100 Futures",
                "asset_class": "Equity Index",
            },
            {
                "symbol": "ES",
                "name": "E-mini S&P 500 Futures",
                "asset_class": "Equity Index",
            },
        ],

        "NYMEX": [
            {
                "symbol": "CL",
                "name": "Crude Oil Futures",
                "asset_class": "Energy",
            },
        ],

        "COMEX": [
            {
                "symbol": "GC",
                "name": "Gold Futures",
                "asset_class": "Metals",
            },
        ],

        "CBOT": [
            {
                "symbol": "ZC",
                "name": "Corn Futures",
                "asset_class": "Agriculture",
            },
        ],
    }

    code = exchange_code.upper().strip()

    return products.get(code, [])


# ============================================================
# PRODUCT AGENT
# ============================================================

root_agent = Agent(
    name="product_info_agent",
    model=MODEL,

    description="""
    Specialist agent for CME product information.
    """,

    instruction="""
You are the CME Product Information Agent.

Use list_products_by_exchange when the user asks about:
- products belonging to an exchange
- product symbols
- product names
- product asset classes

Supported exchanges:
CME, CBOT, NYMEX and COMEX.

Always use the tool for factual product information.
Do not invent information.
Keep the answer concise.
""",

    tools=[list_products_by_exchange],
)


# ============================================================
# EXPOSE THROUGH A2A
# ============================================================

a2a_app = to_a2a(
    root_agent,
    port=8002,
)