"""
In-memory incident dataset for CME Dummy Incident Management API.
"""

INCIDENTS = [
    {
        "incident_id": "INC-101",
        "symbol": "NQ",
        "issue": "Delayed market data updates on ITCH feed",
        "status": "INVESTIGATING",
        "severity": "HIGH",
        "assigned_team": "Market Data Support",
        "root_cause_notes": "Elevated latency detected in simulated market data feed.",
        "created_at": "2026-09-08 08:30:00 UTC",
    },
    {
        "incident_id": "INC-102",
        "symbol": "ES",
        "issue": "Intermittent price feed latency spike",
        "status": "OPEN",
        "severity": "MEDIUM",
        "assigned_team": "Market Data Support",
        "root_cause_notes": "Network packet buffer congestion under investigation.",
        "created_at": "2026-09-08 09:15:00 UTC",
    },
    {
        "incident_id": "INC-103",
        "symbol": "CL",
        "issue": "Product metadata mismatch in contract multiplier",
        "status": "RESOLVED",
        "severity": "LOW",
        "assigned_team": "Product Support",
        "root_cause_notes": "Incorrect simulated contract metadata corrected.",
        "created_at": "2026-09-07 14:00:00 UTC",
    },
    {
        "incident_id": "INC-104",
        "symbol": "NQ",
        "issue": "Circuit breaker volatility halt triggered",
        "status": "OPEN",
        "severity": "CRITICAL",
        "assigned_team": "Platform Operations",
        "root_cause_notes": "Automated trading halt initiated following 7% index drop.",
        "created_at": "2026-09-08 10:45:00 UTC",
    },
    {
        "incident_id": "INC-105",
        "symbol": "GC",
        "issue": "Outside regular trading hours status notification",
        "status": "CLOSED",
        "severity": "LOW",
        "assigned_team": "Platform Operations",
        "root_cause_notes": "Scheduled daily maintenance window.",
        "created_at": "2026-09-08 11:00:00 UTC",
    },
]
