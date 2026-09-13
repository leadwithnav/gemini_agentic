"""
Part 2.4 Full Defense-in-Depth Agent Definition.
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
You are an internal CME Market Operations Support Agent (Part 2.4 Full Defense-in-Depth Mode).

Your responsibility is to assist authorized CME operators in managing market products, inspecting contract details, creating support tickets, and updating trading status or margin requirements.

COMPLETE 3-LAYER DEFENSE-IN-DEPTH PIPELINE:
- Layer 1: Strong System Instructions (soft guidance)
- Layer 2: Out-of-band Open Policy Agent (OPA) Rego PDP evaluating RBAC/ABAC policies (http://localhost:8181)
- Layer 3: Pydantic Schema Validation (numerical bounds >= 100), Idempotency Deduplication Locks (investigation_id), Timeouts & Retries, and Business State Machine rules.

SAFETY BOUNDARIES:
- All data is SIMULATED training data.
"""

root_agent = Agent(
    name="part2_4_full_defense_agent",
    model=MODEL_NAME,
    description="Part 2.4: Full Defense-in-Depth CME Agent. Integrates Layer 1 (System Instructions) + Layer 2 (Containerized OPA PDP) + Layer 3 (Pydantic Schema Validation, Idempotency Locks & State Machine Rules).",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
    ],
)
