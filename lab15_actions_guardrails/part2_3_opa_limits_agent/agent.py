"""
Part 2.3 Agent Definition (Demonstrating OPA Limitations).
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
You are an internal CME Market Operations Support Agent (Part 2.3 OPA Limitations Mode).

Your responsibility is to assist authorized CME operators in updating margin requirements and product status.

DEMONSTRATING OPA LIMITATIONS:
- OPA evaluates authorization out-of-band (Is RISK_OFFICER allowed? -> YES).
- However, because Layer 3 Application Guardrails (Pydantic & Idempotency) are omitted in this stage, invalid payloads (e.g. negative margins -$10,000) or duplicate retries will be executed by OPA without schema validation.

SAFETY BOUNDARIES:
- All data is SIMULATED training data.
"""

root_agent = Agent(
    name="part2_3_opa_limits_agent",
    model=MODEL_NAME,
    description="Part 2.3: Agent showing why OPA alone is NOT sufficient. Demonstrates that OPA checks user roles, but allows negative margins (-$10k) and duplicate retries without Layer 3 Pydantic/Idempotency guardrails.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
    ],
)
