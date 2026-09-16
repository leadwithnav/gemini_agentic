from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv
from .tools import get_market_status

load_dotenv()


MODEL = "gemini-2.5-flash"


# ============================================================
# MARKET AGENT
# ============================================================

root_agent = Agent(

    name="market_agent",

    model=MODEL,

    description="""
    Independent CME Market specialist agent that provides
    simulated market status information for CME products.
    """,

    instruction="""
    You are a CME Market Support Agent.

    Your responsibility is to answer questions about
    simulated market status for CME products.

    AVAILABLE TOOL:
    - get_market_status

    RULES:
    - Always use get_market_status when market status is requested.
    - Do not guess or invent market status.
    - The market status is simulated training data, not live CME data.
    - Keep answers clear and concise.
""",

    tools=[
        get_market_status,
    ],
)


# ============================================================
# EXPOSE AGENT THROUGH A2A
# ============================================================

a2a_app = to_a2a(
    root_agent,
    port=8001,
)