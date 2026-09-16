from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-2.5-flash"


# ============================================================
# TOOL
# ============================================================

def get_exchange_details(exchange_code: str) -> dict:

    exchanges = {
        "CME": {
            "name": "Chicago Mercantile Exchange",
            "location": "Chicago",
            "description": "Offers futures and options across multiple asset classes.",
        },
        "CBOT": {
            "name": "Chicago Board of Trade",
            "location": "Chicago",
            "description": "Known for agricultural and interest-rate products.",
        },
        "NYMEX": {
            "name": "New York Mercantile Exchange",
            "location": "New York",
            "description": "Known for energy and commodity products.",
        },
        "COMEX": {
            "name": "Commodity Exchange",
            "location": "New York",
            "description": "Known for metals products.",
        },
    }

    code = exchange_code.upper().strip()

    return exchanges.get(
        code,
        {"error": f"Exchange {code} not found"}
    )


# ============================================================
# EXCHANGE AGENT
# ============================================================

root_agent = Agent(
    name="exchange_info_agent",
    model=MODEL,

    description="""
    Specialist agent for CME exchange information.
    """,

    instruction="""
You are the CME Exchange Information Agent.

Use get_exchange_details when the user asks about:
- exchange name
- exchange location
- exchange description

Supported exchanges:
CME, CBOT, NYMEX and COMEX.

Always use the tool for factual exchange information.
Do not invent information.
Keep the answer concise.
""",

    tools=[get_exchange_details],
)


# ============================================================
# EXPOSE THROUGH A2A
# ============================================================

a2a_app = to_a2a(
    root_agent,
    port=8001,
)