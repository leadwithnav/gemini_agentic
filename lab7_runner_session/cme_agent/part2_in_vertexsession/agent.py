from google.adk.agents import Agent

from .tools import (
    get_product_details,
    get_market_status,
)
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

MODEL_NAME = "gemini-3.6-flash"


SYSTEM_INSTRUCTION = """
You are a CME Market Product Support Agent.

RESPONSIBILITY:
Help users find CME futures product information and simulated market status.

TOOLS:
- Use get_product_details for product information.
- Use get_market_status for market trading status.
- Use tools whenever factual information is required.
- Never guess or invent tool results.

BOUNDARIES:
- You are a read-only support agent.
- Do not place, modify, or cancel trades.
- Do not provide investment advice.
- Market status is simulated training data, not live CME data.

RESPONSE:
Keep answers clear, concise, and professional.
If information is unavailable, say so clearly.
"""


root_agent = Agent(
    name="cme_market_support_agent",
    model=MODEL_NAME,

    description=(
        "CME support agent for product information "
        "and simulated market status."
    ),

    instruction=SYSTEM_INSTRUCTION,

    tools=[
        get_product_details,
        get_market_status,
    ],
)