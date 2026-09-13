"""
Student Challenge 2B — Starter Agent Code (Lab 2).

OBJECTIVE:
Add a second SENSITIVE action tool: `update_margin_requirement`.

YOUR TASKS:
1. Complete the `update_margin_requirement` function definition below:
   - Accept symbol, margin_type ('INITIAL' or 'MAINTENANCE'), new_amount_usd, reason, investigation_id.
   - Use `student_policy_engine.evaluate_and_execute(...)` with `RiskTier.SENSITIVE`.
2. Add guardrail rules in `starter_policy.py`.
3. Add `update_margin_requirement` to `student_agent` tools list.
4. Run this script to test policy gating and HITL approval workflow!
"""

from typing import Dict, Any
from google.adk.agents import Agent
try:
    from cme_actions_agent.data import update_margin_in_db
    from cme_actions_agent.tools import (
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
    )
except ImportError:
    from lab2_actions_guardrails.cme_actions_agent.data import update_margin_in_db
    from lab2_actions_guardrails.cme_actions_agent.tools import (
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
    )
from .starter_policy import student_policy_engine, RiskTier


# =====================================================================
# TODO (STUDENT TASK): Implement `update_margin_requirement`
# =====================================================================
def update_margin_requirement(
    symbol: str,
    margin_type: str,
    new_amount_usd: float,
    reason: str,
    investigation_id: str = "MARGIN-INCIDENT-001"
) -> Dict[str, Any]:
    """
    Update financial margin requirement for a CME product.
    CLASSIFICATION: SENSITIVE (Requires Human Approval).

    Args:
        symbol: CME product symbol (e.g., CL, ES).
        margin_type: Margin level ('INITIAL' or 'MAINTENANCE').
        new_amount_usd: Target margin amount in USD.
        reason: Operational justification.
        investigation_id: Unique correlation ID for idempotency deduplication.
    """
    clean_symbol = symbol.strip().upper()
    clean_type = margin_type.strip().upper()
    args = {
        "symbol": clean_symbol,
        "margin_type": clean_type,
        "new_amount_usd": new_amount_usd,
        "reason": reason,
        "investigation_id": investigation_id
    }

    def _execute():
        updated = update_margin_in_db(clean_symbol, clean_type, new_amount_usd)
        if not updated:
            return {"status": "error", "error": f"Product '{clean_symbol}' not found.", "is_simulated_data": True}
        return {
            "status": "success",
            "symbol": clean_symbol,
            "margin_type": clean_type,
            "new_amount_usd": new_amount_usd,
            "message": f"Margin {clean_type} for '{clean_symbol}' updated to ${new_amount_usd:,.2f} USD.",
            "is_simulated_data": True
        }

    # TODO: Wrap execution in student_policy_engine.evaluate_and_execute(...)
    # Pass action_name="update_margin_requirement", risk_tier=RiskTier.SENSITIVE, etc.
    return {"status": "error", "error": "Not implemented yet. Complete TODO in starter_agent.py!"}


student_agent = Agent(
    name="student_cme_actions_agent",
    model="gemini-2.5-flash",
    description="Student CME Operations Agent with Policy Guardrails.",
    instruction="Assist CME operators while adhering strictly to policy guardrails for sensitive operations.",
    tools=[
        get_product_details,
        get_market_status,
        create_support_ticket,
        update_product_status,
        # TODO: Add update_margin_requirement here after implementing
    ]
)

if __name__ == "__main__":
    print("Lab 2 Student Challenge — Starter Agent initialized.")
    print("Complete the TODO items in starter_policy.py and starter_agent.py then re-run.")
