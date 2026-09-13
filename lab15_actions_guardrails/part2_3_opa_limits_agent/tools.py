"""
Tools for Part 2.3 Agent (Demonstrating OPA Limitations).

OPA evaluates authorization (WHO can call WHAT), but DOES NOT validate data bounds
(e.g., negative margin -$10,000) or block duplicate retry execution.
"""

from typing import Dict, Any

try:
    from cme_actions_agent.data import (
        PRODUCTS,
        get_product,
        update_status_in_db,
        update_margin_in_db,
        save_support_ticket
    )
    from cme_actions_agent.opa_client import opa_client
except ImportError:
    from lab2_actions_guardrails.cme_actions_agent.data import (
        PRODUCTS,
        get_product,
        update_status_in_db,
        update_margin_in_db,
        save_support_ticket
    )
    from lab2_actions_guardrails.cme_actions_agent.opa_client import opa_client

# Default user for Part 2.3: Authorized RISK_OFFICER
OPA_LIMITS_USER_CONTEXT = {
    "username": "mwilson_risk",
    "role": "RISK_OFFICER"
}

def set_limits_user_context(username: str, role: str) -> None:
    """Set user context for Part 2.3 testing."""
    global OPA_LIMITS_USER_CONTEXT
    OPA_LIMITS_USER_CONTEXT = {"username": username, "role": role}

def get_product_details(symbol: str) -> Dict[str, Any]:
    """Retrieve product specifications for a CME futures product."""
    clean_symbol = symbol.strip().upper()
    prod = get_product(clean_symbol)
    if not prod:
        return {"status": "error", "error": f"Product '{clean_symbol}' not found.", "is_simulated_data": True}
    return {"status": "success", "data": prod, "is_simulated_data": True}

def get_market_status(symbol: str) -> Dict[str, Any]:
    """Check current operational trading status (TRADING, HALTED, SUSPENDED, CLOSED)."""
    clean_symbol = symbol.strip().upper()
    prod = get_product(clean_symbol)
    if not prod:
        return {"status": "error", "error": f"Product '{clean_symbol}' not found.", "is_simulated_data": True}
    return {
        "status": "success",
        "data": {"symbol": clean_symbol, "name": prod["name"], "status": prod["status"]},
        "is_simulated_data": True
    }

def create_support_ticket(
    symbol: str,
    issue_type: str,
    description: str,
    priority: str = "MEDIUM",
    investigation_id: str = "INC-1001"
) -> Dict[str, Any]:
    """Create an operational support ticket."""
    clean_sym = symbol.strip().upper()
    prod_data = get_product(clean_sym)
    res_ctx = {"symbol": clean_sym, "asset_class": prod_data.get("asset_class", "UNKNOWN") if prod_data else "UNKNOWN"}

    allowed, mode = opa_client.is_allowed(
        user_context=OPA_LIMITS_USER_CONTEXT,
        action="create_support_ticket",
        resource_context=res_ctx,
        arguments={"symbol": clean_sym, "issue_type": issue_type, "priority": priority}
    )

    if not allowed:
        return {"status": "error", "error": f"OPA_POLICY_DENIED by {mode}.", "layer": "LAYER_2_OPA"}

    ticket_id = f"TICKET-{len(PRODUCTS) * 10 + 7}"
    ticket = {
        "ticket_id": ticket_id,
        "symbol": clean_sym,
        "issue_type": issue_type,
        "description": description,
        "priority": priority,
        "investigation_id": investigation_id
    }
    save_support_ticket(ticket)
    return {"status": "success", "ticket": ticket, "is_simulated_data": True}

def update_product_status(
    symbol: str,
    new_status: str,
    reason: str,
    investigation_id: str = "INC-1001"
) -> Dict[str, Any]:
    """Update market operational status (OPA checks role, but no business state rule checks)."""
    clean_sym = symbol.strip().upper()
    clean_stat = new_status.strip().upper()
    prod_data = get_product(clean_sym)
    res_ctx = {
        "symbol": clean_sym,
        "asset_class": prod_data.get("asset_class", "UNKNOWN") if prod_data else "UNKNOWN",
        "current_status": prod_data.get("status", "UNKNOWN") if prod_data else "UNKNOWN"
    }

    allowed, mode = opa_client.is_allowed(
        user_context=OPA_LIMITS_USER_CONTEXT,
        action="update_product_status",
        resource_context=res_ctx,
        arguments={"symbol": clean_sym, "new_status": clean_stat, "reason": reason}
    )

    if not allowed:
        return {"status": "error", "error": f"OPA_POLICY_DENIED by {mode}.", "layer": "LAYER_2_OPA"}

    # NO Layer 3 Business State Machine Check -> Allows direct CLOSED -> TRADING transition!
    update_status_in_db(clean_sym, clean_stat)
    return {
        "status": "success",
        "symbol": clean_sym,
        "new_status": clean_stat,
        "message": f"[OPA LIMITATION DEMO] OPA checked role '{OPA_LIMITS_USER_CONTEXT['role']}' -> ALLOWED. State updated without application state clearance validation!",
        "is_simulated_data": True
    }

def update_margin_requirement(
    symbol: str,
    margin_type: str,
    new_amount_usd: float,
    reason: str,
    investigation_id: str = "MARGIN-INC-101"
) -> Dict[str, Any]:
    """Update financial margin requirement (OPA checks role, but NO Pydantic schema or Idempotency lock)."""
    clean_sym = symbol.strip().upper()
    clean_type = margin_type.strip().upper()
    prod_data = get_product(clean_sym)
    res_ctx = {"symbol": clean_sym, "asset_class": prod_data.get("asset_class", "UNKNOWN") if prod_data else "UNKNOWN"}

    allowed, mode = opa_client.is_allowed(
        user_context=OPA_LIMITS_USER_CONTEXT,
        action="update_margin_requirement",
        resource_context=res_ctx,
        arguments={"symbol": clean_sym, "margin_type": clean_type, "new_amount_usd": new_amount_usd}
    )

    if not allowed:
        return {"status": "error", "error": f"OPA_POLICY_DENIED by {mode}.", "layer": "LAYER_2_OPA"}

    # NO Layer 3 Pydantic validation -> Allows negative amounts (-$10,000) into database!
    # NO Layer 3 Idempotency lock -> Allows duplicate retry mutations!
    update_margin_in_db(clean_sym, clean_type, new_amount_usd)

    warning_flag = ""
    if new_amount_usd < 0:
        warning_flag = " ⚠️ WARNING: NEGATIVE MARGIN ENTERED INTO DATABASE (-$10,000 USD)! OPA ALLOWED THIS BECAUSE OPA ONLY CHECKS USER PERMISSIONS, NOT DATA BOUNDS."

    return {
        "status": "success",
        "symbol": clean_sym,
        "margin_type": clean_type,
        "new_amount_usd": new_amount_usd,
        "message": f"[OPA LIMITATION DEMO] Margin '{clean_type}' updated to ${new_amount_usd:,.2f} USD.{warning_flag}",
        "opa_evaluator": mode,
        "is_simulated_data": True
    }
