"""
Operational Support Tools for CME Internal Help Desk Agents (Lab 3).

Provides Python tool functions equipped by ADK agents to query support tickets,
product details, market operational statuses, list incidents, update ticket status, and create tickets.
"""

from typing import Dict, Any, List

try:
    from data import PRODUCTS, INCIDENTS, SUPPORT_TEAMS, SUPPORT_STATUSES, get_product, get_incident, update_incident_status_in_db, add_incident_ticket
except ImportError:
    from .data import PRODUCTS, INCIDENTS, SUPPORT_TEAMS, SUPPORT_STATUSES, get_product, get_incident, update_incident_status_in_db, add_incident_ticket

def get_ticket_details(ticket_id: str) -> Dict[str, Any]:
    """Retrieves full details for a CME support ticket by ticket ID (e.g., INC-101, INC-102, INC-103).

    Args:
        ticket_id: Incident ticket ID such as INC-101, INC-102, or INC-103.

    Returns:
        Structured dictionary containing ticket metadata, assigned team, status, and description.
    """
    clean_id = ticket_id.strip().upper()
    inc = get_incident(clean_id)
    if not inc:
        return {"status": "error", "message": f"Support ticket '{clean_id}' not found.", "is_simulated_data": True}
    return {"status": "success", "ticket": inc, "is_simulated_data": True}

def get_product_details(symbol: str) -> Dict[str, Any]:
    """Retrieves product details and assigned support team for a CME futures product (ES, NQ, CL, GC).

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, or GC.

    Returns:
        Dictionary containing product specifications, trading status, and primary support team.
    """
    clean_symbol = symbol.strip().upper()
    prod = get_product(clean_symbol)
    if not prod:
        return {"status": "error", "message": f"Product '{clean_symbol}' not found.", "is_simulated_data": True}
    return {"status": "success", "product": prod, "is_simulated_data": True}

def get_market_status(symbol: str) -> Dict[str, Any]:
    """Retrieves operational market trading status (TRADING, HALTED, CLOSED) for a CME product.

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, or GC.

    Returns:
        Dictionary containing symbol, product name, and current trading status.
    """
    clean_symbol = symbol.strip().upper()
    prod = get_product(clean_symbol)
    if not prod:
        return {"status": "error", "message": f"Product '{clean_symbol}' not found.", "is_simulated_data": True}
    return {
        "status": "success",
        "symbol": clean_symbol,
        "name": prod["name"],
        "trading_status": prod["status"],
        "is_simulated_data": True
    }

def list_incidents_by_product(symbol: str) -> List[Dict[str, Any]]:
    """Lists all support incidents associated with a specific CME product symbol (ES, NQ, CL, GC).

    Args:
        symbol: Futures ticker symbol such as ES, NQ, CL, or GC.

    Returns:
        List of incident ticket dictionaries matching the product symbol.
    """
    clean_sym = symbol.strip().upper()
    matching = []
    for inc in INCIDENTS.values():
        if inc["symbol"].upper() == clean_sym:
            inc_copy = dict(inc)
            inc_copy["is_simulated_data"] = True
            matching.append(inc_copy)
    return matching

def update_ticket_status(ticket_id: str, new_status: str, notes: str = "") -> Dict[str, Any]:
    """Updates status (OPEN, INVESTIGATING, RESOLVED) and notes for a support ticket.

    Args:
        ticket_id: Ticket ID (e.g. INC-101, INC-102, INC-103).
        new_status: New status (OPEN, INVESTIGATING, RESOLVED).
        notes: Root cause notes or investigation updates.

    Returns:
        Confirmation dict with updated ticket details.
    """
    clean_id = ticket_id.strip().upper()
    clean_stat = new_status.strip().upper()
    if clean_stat not in SUPPORT_STATUSES:
        return {"status": "error", "message": f"Invalid status '{clean_stat}'. Must be one of {SUPPORT_STATUSES}.", "is_simulated_data": True}
    
    success = update_incident_status_in_db(clean_id, clean_stat, notes)
    if not success:
        return {"status": "error", "message": f"Ticket '{clean_id}' not found.", "is_simulated_data": True}
    
    return {
        "status": "success",
        "ticket_id": clean_id,
        "new_status": clean_stat,
        "notes": notes,
        "message": f"Support ticket '{clean_id}' status updated to '{clean_stat}'.",
        "is_simulated_data": True
    }

def create_support_ticket(symbol: str, issue_type: str, description: str, assigned_team: str = "Product Support") -> Dict[str, Any]:
    """Creates a new CME internal support incident ticket.

    Args:
        symbol: Futures ticker symbol (ES, NQ, CL, GC).
        issue_type: Category of issue (e.g., 'LATENCY_SPIKE', 'HALT_INVESTIGATION', 'MARGIN_DISCREPANCY').
        description: Summary explanation of the support issue.
        assigned_team: Team to handle ticket ('Market Data Support', 'Product Support', 'Platform Operations').

    Returns:
        Confirmation dict with assigned ticket ID.
    """
    clean_sym = symbol.strip().upper()
    new_num = len(INCIDENTS) + 101
    ticket_id = f"INC-{new_num}"
    
    ticket = {
        "ticket_id": ticket_id,
        "symbol": clean_sym,
        "title": f"{issue_type.replace('_', ' ').title()} on {clean_sym}",
        "description": description,
        "status": "OPEN",
        "priority": "HIGH",
        "assigned_team": assigned_team,
        "created_at": "2026-09-07 10:00:00 UTC",
        "root_cause_notes": "Ticket created via CME AI Support Desk."
    }
    
    add_incident_ticket(ticket)
    return {
        "status": "success",
        "ticket_id": ticket_id,
        "ticket": ticket,
        "message": f"New CME support ticket '{ticket_id}' logged and assigned to '{assigned_team}'.",
        "is_simulated_data": True
    }
