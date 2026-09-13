"""
Simulated Data Store for CME Internal Product Support Desk (Lab 3).

Contains products (ES, NQ, CL, GC), support tickets (INC-101, INC-102, INC-103),
support teams, and ticket statuses.
"""

from typing import Dict, Any, List

# Products Catalog
PRODUCTS: Dict[str, Dict[str, Any]] = {
    "ES": {
        "symbol": "ES",
        "name": "E-mini S&P 500 Futures",
        "asset_class": "Equity Index",
        "exchange": "CME",
        "contract_size": "$50 x S&P 500 Index",
        "status": "TRADING",
        "primary_support_team": "Market Data Support"
    },
    "NQ": {
        "symbol": "NQ",
        "name": "E-mini Nasdaq-100 Futures",
        "asset_class": "Equity Index",
        "exchange": "CME",
        "contract_size": "$20 x Nasdaq-100 Index",
        "status": "TRADING",
        "primary_support_team": "Market Data Support"
    },
    "CL": {
        "symbol": "CL",
        "name": "Crude Oil Futures",
        "asset_class": "Energy",
        "exchange": "NYMEX",
        "contract_size": "1,000 barrels",
        "status": "HALTED",
        "primary_support_team": "Platform Operations"
    },
    "GC": {
        "symbol": "GC",
        "name": "Gold Futures",
        "asset_class": "Metals",
        "exchange": "COMEX",
        "contract_size": "100 troy ounces",
        "status": "TRADING",
        "primary_support_team": "Product Support"
    }
}

# Support Teams
SUPPORT_TEAMS: List[str] = [
    "Market Data Support",
    "Product Support",
    "Platform Operations"
]

# Support Statuses
SUPPORT_STATUSES: List[str] = [
    "OPEN",
    "INVESTIGATING",
    "RESOLVED"
]

# Incident Tickets Database
INCIDENTS: Dict[str, Dict[str, Any]] = {
    "INC-101": {
        "ticket_id": "INC-101",
        "symbol": "ES",
        "title": "Feed Latency Spike on Globex Market Data",
        "description": "Intermittent 150ms packet delay observed on ITCH market data feeds for ES contracts.",
        "status": "OPEN",
        "priority": "HIGH",
        "assigned_team": "Market Data Support",
        "created_at": "2026-09-07 08:30:00 UTC",
        "root_cause_notes": "Under investigation by network operations team."
    },
    "INC-102": {
        "ticket_id": "INC-102",
        "symbol": "CL",
        "title": "Circuit Breaker Trading Halt Triggered",
        "description": "Automated volatility trading halt triggered on CL October contract following 7% intraday move.",
        "status": "INVESTIGATING",
        "priority": "CRITICAL",
        "assigned_team": "Platform Operations",
        "created_at": "2026-09-07 09:15:00 UTC",
        "root_cause_notes": "Evaluating price limit band reset parameters before reopening."
    },
    "INC-103": {
        "ticket_id": "INC-103",
        "symbol": "GC",
        "title": "Margin Buffer Calculation Discrepancy",
        "description": "Clearing firm inquiry regarding maintenance margin variance on GC multi-leg positions.",
        "status": "RESOLVED",
        "priority": "MEDIUM",
        "assigned_team": "Product Support",
        "created_at": "2026-09-06 14:00:00 UTC",
        "root_cause_notes": "SPAN margin algorithm updated and verified with clearing firm."
    }
}

def get_product(symbol: str) -> Dict[str, Any] | None:
    """Retrieve product details by symbol."""
    return PRODUCTS.get(symbol.strip().upper())

def get_incident(ticket_id: str) -> Dict[str, Any] | None:
    """Retrieve incident ticket by ID."""
    return INCIDENTS.get(ticket_id.strip().upper())

def update_incident_status_in_db(ticket_id: str, new_status: str, notes: str = "") -> bool:
    """Update incident status in database."""
    inc = get_incident(ticket_id)
    if inc:
        inc["status"] = new_status.upper()
        if notes:
            inc["root_cause_notes"] = notes
        return True
    return False

def add_incident_ticket(ticket_data: Dict[str, Any]) -> None:
    """Add a new incident ticket."""
    INCIDENTS[ticket_data["ticket_id"]] = ticket_data
