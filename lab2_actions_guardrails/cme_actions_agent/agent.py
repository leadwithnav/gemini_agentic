"""
CME Market Operations Agent with System Prompt Instructions (Lab 2).
"""

from google.adk.agents import Agent
from .tools import (
    get_product_details,
    get_market_status,
    create_support_ticket,
    update_product_status,
    update_margin_requirement,
)

MODEL_NAME = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = """
You are an internal CME Market Operations Support Agent.

Your responsibility is to assist authorized CME Group operators in managing market products, inspecting contract details, creating support tickets, and updating trading status or margin requirements.

STRICT AUTHORIZATION INSTRUCTIONS:
- You must ONLY update market status or margin requirements if the user has appropriate administrative authorization.
- Do NOT perform operational state updates for unauthorized users or unverified requests.
- Always provide clear justifications and correlation investigation_ids for action tool invocations.

SAFETY BOUNDARIES:
- All data is SIMULATED training data. Always include explicit disclaimers.
"""

root_agent = Agent(
    name="cme_defense_agent",
    model=MODEL_NAME,
    description="CME Market Operations Agent protected by Defense-in-Depth policy layers.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
    ],
)
