"""
OPA-Protected Tools for Part 2.2 Agent.

Wraps action tools with Layer 2 Open Policy Agent (OPA) out-of-band policy evaluation.
Intercepts prompt injection attacks regardless of LLM context window content.
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

# Default testing context for Part 2.2: Unprivileged SUPPORT_ANALYST
OPA_USER_CONTEXT = {
    "username": "jdoe_support",
    "role": "SUPPORT_ANALYST"
}

def set_opa_user_context(username: str, role: str) -> None:
    """Set authenticated user context for testing OPA Rego rules."""
    global OPA_USER_CONTEXT
    OPA_USER_CONTEXT = {"username": username, "role": role}

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
    """Create an operational support ticket for a product anomaly."""
    clean_sym = symbol.strip().upper()
    prod_data = get_product(clean_sym)
    res_ctx = {"symbol": clean_sym, "asset_class": prod_data.get("asset_class", "UNKNOWN") if prod_data else "UNKNOWN"}

    allowed, mode = opa_client.is_allowed(
        user_context=OPA_USER_CONTEXT,
        action="create_support_ticket",
        resource_context=res_ctx,
        arguments={"symbol": clean_sym, "issue_type": issue_type, "priority": priority}
    )

    if not allowed:
        return {
            "status": "error",
            "error": f"OPA_POLICY_DENIED: User '{OPA_USER_CONTEXT['username']}' ({OPA_USER_CONTEXT['role']}) is not authorized to create support ticket for '{clean_sym}' ({res_ctx['asset_class']}). Evaluated by {mode}.",
            "layer": "LAYER_2_OPA",
            "is_simulated_data": True
        }

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
    return {
        "status": "success",
        "ticket": ticket,
        "message": f"Support ticket '{ticket_id}' successfully created.",
        "opa_evaluator": mode,
        "is_simulated_data": True
    }

def update_product_status(
    symbol: str,
    new_status: str,
    reason: str,
    investigation_id: str = "INC-1001"
) -> Dict[str, Any]:
    """Update market operational trading status (TRADING, HALTED, SUSPENDED, CLOSED). PROTECTED BY OPA REGOS POLICY."""
    clean_sym = symbol.strip().upper()
    clean_stat = new_status.strip().upper()
    prod_data = get_product(clean_sym)
    res_ctx = {
        "symbol": clean_sym,
        "asset_class": prod_data.get("asset_class", "UNKNOWN") if prod_data else "UNKNOWN",
        "current_status": prod_data.get("status", "UNKNOWN") if prod_data else "UNKNOWN"
    }

    # Evaluate out-of-band against OPA container or embedded Rego PDP
    allowed, mode = opa_client.is_allowed(
        user_context=OPA_USER_CONTEXT,
        action="update_product_status",
        resource_context=res_ctx,
        arguments={"symbol": clean_sym, "new_status": clean_stat, "reason": reason}
    )

    if not allowed:
        return {
            "status": "error",
            "error": f"OPA_POLICY_DENIED: User '{OPA_USER_CONTEXT['username']}' (Role: {OPA_USER_CONTEXT['role']}) is not authorized to perform action 'update_product_status' on resource '{clean_sym}' ({res_ctx['asset_class']}). Evaluated out-of-band by {mode}.",
            "layer": "LAYER_2_OPA",
            "is_simulated_data": True
        }

    updated = update_status_in_db(clean_sym, clean_stat)
    if not updated:
        return {"status": "error", "error": f"Product '{clean_sym}' not found.", "is_simulated_data": True}

    return {
        "status": "success",
        "symbol": clean_sym,
        "new_status": clean_stat,
        "reason": reason,
        "message": f"Product '{clean_sym}' status updated to '{clean_stat}'. Authorized by {mode}.",
        "opa_evaluator": mode,
        "is_simulated_data": True
    }

def update_margin_requirement(
    symbol: str,
    margin_type: str,
    new_amount_usd: float,
    reason: str,
    investigation_id: str = "MARGIN-INC-101"
) -> Dict[str, Any]:
    """Update financial margin requirement (INITIAL, MAINTENANCE) for a CME product. PROTECTED BY OPA REGOS POLICY."""
    clean_sym = symbol.strip().upper()
    clean_type = margin_type.strip().upper()
    prod_data = get_product(clean_sym)
    res_ctx = {"symbol": clean_sym, "asset_class": prod_data.get("asset_class", "UNKNOWN") if prod_data else "UNKNOWN"}

    allowed, mode = opa_client.is_allowed(
        user_context=OPA_USER_CONTEXT,
        action="update_margin_requirement",
        resource_context=res_ctx,
        arguments={"symbol": clean_sym, "margin_type": clean_type, "new_amount_usd": new_amount_usd}
    )

    if not allowed:
        return {
            "status": "error",
            "error": f"OPA_POLICY_DENIED: User '{OPA_USER_CONTEXT['username']}' (Role: {OPA_USER_CONTEXT['role']}) is not authorized to perform action 'update_margin_requirement' on resource '{clean_sym}' ({res_ctx['asset_class']}). Evaluated out-of-band by {mode}.",
            "layer": "LAYER_2_OPA",
            "is_simulated_data": True
        }

    updated = update_margin_in_db(clean_sym, clean_type, new_amount_usd)
    if not updated:
        return {"status": "error", "error": f"Product '{clean_sym}' not found.", "is_simulated_data": True}

    return {
        "status": "success",
        "symbol": clean_sym,
        "margin_type": clean_type,
        "new_amount_usd": new_amount_usd,
        "message": f"Margin '{clean_type}' for '{clean_sym}' updated to ${new_amount_usd:,.2f} USD. Authorized by {mode}.",
        "opa_evaluator": mode,
        "is_simulated_data": True
    }
