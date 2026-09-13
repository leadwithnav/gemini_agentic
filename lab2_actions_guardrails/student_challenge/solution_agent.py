"""
Student Challenge 2B — Solution Agent Code (Defense-in-Depth).

Fully integrates Layer 2 OPA (RBAC/ABAC) and Layer 3 Pydantic validation + Idempotency locks.
"""

from typing import Dict, Any
from google.adk.agents import Agent
try:
    from cme_actions_agent.tools import (
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
        set_user_context
    )
except ImportError:
    from lab2_actions_guardrails.cme_actions_agent.tools import (
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
        set_user_context
    )

solution_agent = Agent(
    name="solution_defense_agent",
    model="gemini-2.5-flash",
    description="Solution CME Operations Agent with 3-Layer Defense-in-Depth Architecture.",
    instruction="Assist CME operators while enforcing strict OPA RBAC/ABAC policies, Pydantic bounds, and idempotency locks.",
    tools=[
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        update_margin_requirement,
    ]
)

if __name__ == "__main__":
    print("=== Student Challenge Reference Solution Execution ===")
    
    # 1. Test SAFE Tool
    print("\n1. Testing SAFE Tool (get_product_details):")
    res1 = get_product_details("CL")
    print("Result:", res1)

    # 2. Test Layer 2 OPA ABAC Protection (SUPPORT_ANALYST modifying ES -> BLOCKED)
    print("\n2. Testing Layer 2 OPA ABAC Protection (Analyst updating ES):")
    set_user_context("jdoe_analyst", "SUPPORT_ANALYST")
    res2 = update_product_status("ES", "HALTED", "Routine halt check", investigation_id="INV-201")
    print("Result:", res2)

    # 3. Test Layer 3 Pydantic Boundary Validation (RISK_OFFICER negative margin -> BLOCKED)
    print("\n3. Testing Layer 3 Pydantic Schema Validation (Negative Margin):")
    set_user_context("mwilson_risk", "RISK_OFFICER")
    res3 = update_margin_requirement("CL", "INITIAL", -100.0, "Invalid negative margin request", investigation_id="INV-202")
    print("Result:", res3)

    # 4. Test Valid Action (RISK_OFFICER valid margin update -> SUCCESS)
    print("\n4. Testing Valid Margin Update (RISK_OFFICER):")
    res4 = update_margin_requirement("CL", "INITIAL", 8500.0, "Increased volatility requirement in crude oil", investigation_id="INV-203")
    print("Result:", res4)

    # 5. Test Layer 3 Idempotency Lock
    print("\n5. Testing Layer 3 Idempotency Deduplication Lock (Duplicate Retry):")
    res5 = update_margin_requirement("CL", "INITIAL", 8500.0, "Increased volatility requirement in crude oil", investigation_id="INV-203")
    print("Result:", res5)
