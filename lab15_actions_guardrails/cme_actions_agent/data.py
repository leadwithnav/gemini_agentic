"""
Simulated Data Store for CME Market Operations Agent (Lab 2).

Extends the Lab 1 product catalog to include mutable operational attributes:
- Trading status (TRADING, HALTED, SUSPENDED, CLOSED)
- Margin requirements (initial_margin, maintenance_margin in USD)
- Support incident ticket repository

IMPORTANT: This is SIMULATED training data only. All outputs include `"is_simulated_data": True`.
"""

from typing import Dict, Any, List

# Simulated product catalog based on Lab 1
PRODUCTS: Dict[str, Dict[str, Any]] = {
    "ES": {
        "symbol": "ES",
        "name": "E-mini S&P 500 Futures",
        "asset_class": "Equity Index",
        "exchange": "CME",
        "contract_size": "$50 x S&P 500 Index",
        "currency": "USD",
        "status": "TRADING",
        "margins": {
            "initial_margin": 12500.0,
            "maintenance_margin": 11360.0
        },
        "description": "The benchmark equity index futures contract tracking the S&P 500 Index."
    },
    "NQ": {
        "symbol": "NQ",
        "name": "E-mini Nasdaq-100 Futures",
        "asset_class": "Equity Index",
        "exchange": "CME",
        "contract_size": "$20 x Nasdaq-100 Index",
        "currency": "USD",
        "status": "TRADING",
        "margins": {
            "initial_margin": 17800.0,
            "maintenance_margin": 16180.0
        },
        "description": "Liquidity benchmark tracking top non-financial tech market leaders."
    },
    "CL": {
        "symbol": "CL",
        "name": "Crude Oil Futures",
        "asset_class": "Energy",
        "exchange": "NYMEX",
        "contract_size": "1,000 barrels",
        "currency": "USD",
        "status": "HALTED",  # Default HALTED for lab scenario testing
        "margins": {
            "initial_margin": 6800.0,
            "maintenance_margin": 6180.0
        },
        "description": "World standard benchmark for crude oil trading."
    },
    "GC": {
        "symbol": "GC",
        "name": "Gold Futures",
        "asset_class": "Metals",
        "exchange": "COMEX",
        "contract_size": "100 troy ounces",
        "currency": "USD",
        "status": "TRADING",
        "margins": {
            "initial_margin": 9500.0,
            "maintenance_margin": 8636.0
        },
        "description": "Premier benchmark pricing for precious metals global commerce."
    },
    "ZC": {
        "symbol": "ZC",
        "name": "Corn Futures",
        "asset_class": "Agriculture",
        "exchange": "CBOT",
        "contract_size": "5,000 bushels",
        "currency": "US Cents",
        "status": "TRADING",
        "margins": {
            "initial_margin": 2400.0,
            "maintenance_margin": 2180.0
        },
        "description": "Global price discovery standard for agricultural commodities."
    },
    "6E": {
        "symbol": "6E",
        "name": "Euro FX Futures",
        "asset_class": "FX",
        "exchange": "CME",
        "contract_size": "125,000 EUR",
        "currency": "USD",
        "status": "TRADING",
        "margins": {
            "initial_margin": 3100.0,
            "maintenance_margin": 2818.0
        },
        "description": "Direct foreign exchange hedging contract for Euro vs USD."
    }
}

# Simulated support incident ticket store
SUPPORT_TICKETS: List[Dict[str, Any]] = []

def get_product(symbol: str) -> Dict[str, Any] | None:
    """Retrieve product dict by symbol (case-insensitive)."""
    return PRODUCTS.get(symbol.strip().upper())

def update_status_in_db(symbol: str, new_status: str) -> bool:
    """Update product status in the simulated database."""
    product = get_product(symbol)
    if product:
        product["status"] = new_status.upper()
        return True
    return False

def update_margin_in_db(symbol: str, margin_type: str, new_amount: float) -> bool:
    """Update margin requirement in the simulated database."""
    product = get_product(symbol)
    if product:
        key = margin_type.lower() + "_margin"
        product["margins"][key] = float(new_amount)
        return True
    return False

def save_support_ticket(ticket_data: Dict[str, Any]) -> None:
    """Save support ticket to simulated repository."""
    SUPPORT_TICKETS.append(ticket_data)
