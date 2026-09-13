"""
Part 2.2 OPA-Protected Agent Definition.
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
You are an internal CME Market Operations Support Agent (Part 2.2 OPA Mode).

Your responsibility is to assist CME Group operators in managing market products, inspecting contract details, creating support tickets, and updating trading status or margin requirements.

OUT-OF-BAND OPA AUTHORIZATION:
- All action tools are intercepted by Open Policy Agent (OPA) running in Docker.
- Authorization decisions are evaluated completely outside your LLM context window based on authenticated user roles and Rego policy rules.

SAFETY BOUNDARIES:
- All data is SIMULATED training data.
"""

root_agent = Agent(
    name="part2_2_opa_agent",
    model=MODEL_NAME,
    description="Part 2.2: OPA-Protected CME Agent. Tool calls are evaluated out-of-band by containerized OPA Rego policies (http://localhost:8181), stopping prompt injection attacks.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
    ],
)
