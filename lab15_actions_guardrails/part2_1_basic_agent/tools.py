"""
Unwrapped Tools for Part 2.1 Basic Agent (No OPA, No Policy Engine).

These tools execute directly on the database without out-of-band authorization checks,
demonstrating how prompt injections bypass soft system prompt instructions.
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
except ImportError:
    from lab2_actions_guardrails.cme_actions_agent.data import (
        PRODUCTS,
        get_product,
        update_status_in_db,
        update_margin_in_db,
        save_support_ticket
    )

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
    ticket_id = f"TICKET-{len(PRODUCTS) * 10 + 7}"
    ticket = {
        "ticket_id": ticket_id,
        "symbol": symbol.strip().upper(),
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
        "is_simulated_data": True
    }

def update_product_status(
    symbol: str,
    new_status: str,
    reason: str,
    investigation_id: str = "INC-1001"
) -> Dict[str, Any]:
    """Update market operational trading status (TRADING, HALTED, SUSPENDED, CLOSED). DIRECT UNPROTECTED EXECUTION."""
    clean_sym = symbol.strip().upper()
    clean_stat = new_status.strip().upper()
    updated = update_status_in_db(clean_sym, clean_stat)
    if not updated:
        return {"status": "error", "error": f"Product '{clean_sym}' not found.", "is_simulated_data": True}
    return {
        "status": "success",
        "symbol": clean_sym,
        "new_status": clean_stat,
        "reason": reason,
        "message": f"[UNPROTECTED TOOL EXECUTION] Product '{clean_sym}' status updated to '{clean_stat}'. Soft system instruction bypassed!",
        "is_simulated_data": True
    }

def update_margin_requirement(
    symbol: str,
    margin_type: str,
    new_amount_usd: float,
    reason: str,
    investigation_id: str = "MARGIN-INC-101"
) -> Dict[str, Any]:
    """Update financial margin requirement (INITIAL, MAINTENANCE) for a CME product. DIRECT UNPROTECTED EXECUTION."""
    clean_sym = symbol.strip().upper()
    clean_type = margin_type.strip().upper()
    updated = update_margin_in_db(clean_sym, clean_type, new_amount_usd)
    if not updated:
        return {"status": "error", "error": f"Product '{clean_sym}' not found.", "is_simulated_data": True}
    return {
        "status": "success",
        "symbol": clean_sym,
        "margin_type": clean_type,
        "new_amount_usd": new_amount_usd,
        "message": f"[UNPROTECTED TOOL EXECUTION] Margin '{clean_type}' for '{clean_sym}' updated to ${new_amount_usd:,.2f} USD.",
        "is_simulated_data": True
    }
