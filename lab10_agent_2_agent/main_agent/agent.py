from google.adk import Agent

from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

from google.adk.tools.agent_tool import AgentTool


MODEL = "gemini-2.5-flash"


# ============================================================
# REMOTE MARKET AGENT
# ============================================================

MARKET_AGENT_URL = "http://localhost:8001"

MARKET_AGENT_CARD_URL = (
    f"{MARKET_AGENT_URL}"
    f"{AGENT_CARD_WELL_KNOWN_PATH}"
)


remote_market_agent = RemoteA2aAgent(

    name="remote_market_agent",

    description="""
    Remote CME Market specialist agent.

    Provides market-related information such as
    market status and product market information.
    """,

    agent_card=MARKET_AGENT_CARD_URL,
)


# ============================================================
# EXPOSE REMOTE AGENT AS TOOL
# ============================================================

market_agent_tool = AgentTool(
    agent=remote_market_agent
)


# ============================================================
# SUPERVISOR AGENT
# ============================================================

root_agent = Agent(

    name="cme_support_supervisor",

    model=MODEL,

    description="""
    Supervisor agent for CME support requests.

    Delegates market-related questions to a
    remote Market Agent through A2A.
    """,

    instruction="""
    You are a CME Support Supervisor.

    Your responsibility is to understand the user's request
    and delegate market-related questions to the remote Market Agent.

    DELEGATION:

    For questions about:
    - current market status
    - whether a product is trading
    - market information
    - market-related product questions

    you MUST delegate to remote_market_agent.

    Examples:
    - Is NQ currently trading?
    - What is the market status of ES?
    - Is CL open or closed?
    - Check the current market status for GC.

    Do not invent market information yourself.

    Use the remote_market_agent for market-related factual information.

    For greetings and general conversation,
    you may answer directly.

    After receiving the response from the Market Agent,
    present the result clearly and concisely to the user.
""",

    tools=[
        market_agent_tool,
    ],
)