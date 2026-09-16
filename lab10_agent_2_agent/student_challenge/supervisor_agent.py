from google.adk import Agent

from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

from google.adk.tools.agent_tool import AgentTool

from dotenv import load_dotenv

load_dotenv()


MODEL = "gemini-2.5-flash"



# TODO ADD Remote EXCHANGE AGENT

# TODO ADD REMOTE PRODUCT AGENT

# TODO EXPOSE REMOTE Exchange AGENT AS TOOL
# TODO EXPOSE REMOTE Product AGENT AS TOOL



root_agent = Agent(
    name="exchange_support_supervisor",
    model=MODEL,

    description="""
    Supervisor for CME exchange and product questions.
    """,

    instruction="""
You are the CME Exchange Support Supervisor.

You have two specialist agents.


EXCHANGE INFO AGENT

Use exchange_info_agent for:
- exchange name
- exchange location
- exchange description


PRODUCT INFO AGENT

Use product_info_agent for:
- products belonging to an exchange
- product symbols
- product names
- asset classes


RULES

- Delegate factual questions to the appropriate specialist.
- If the question needs exchange information, use exchange_info_agent.
- If the question needs product information, use product_info_agent.
- If the question needs both, use both agents.
- Do not invent exchange or product information.
- Combine the results into one clear answer.
""",

    tools=[
       # Add tools here
    ],
)