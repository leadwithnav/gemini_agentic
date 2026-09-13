"""
Student Challenge: Integrated CME Internal Product Support Assistant (ADK V2)
Complete workflow: Ticket Investigation -> Parallel Product & Market Audit -> Resolution Recommendation.
"""
from google.adk import Agent
from google.adk import Workflow

try:
    from tools import (
        get_ticket_details,
        get_product_details,
        get_market_status,
        list_incidents_by_product,
        update_ticket_status,
        create_support_ticket,
    )
except ImportError:
    from lab3_multi_agents.tools import (
        get_ticket_details,
        get_product_details,
        get_market_status,
        list_incidents_by_product,
        update_ticket_status,
        create_support_ticket,
    )

# Stage 1: Ticket Triage Analyst
challenge_triage_analyst = Agent(
    name="challenge_triage_analyst",
    model="gemini-3.6-flash",
    instruction="""You are the CME Support Triage Analyst.
Analyze the employee inquiry for ticket ID (INC-101, INC-102, INC-103) or product symbol (ES, NQ, CL, GC).
Use `get_ticket_details` and `get_product_details` to look up initial incident and product specifications.""",
    tools=[get_ticket_details, get_product_details],
)

# Stage 2: Parallel Auditor 1 - Market Status Auditor
challenge_market_auditor = Agent(
    name="challenge_market_auditor",
    model="gemini-3.6-flash",
    instruction="""You are the CME Market Status Auditor.
Verify operational market state (TRADING, HALTED, CLOSED) for the product symbol.
Use `get_market_status` to verify trading availability.
Output a clear operational status evaluation.""",
    tools=[get_market_status],
)

# Stage 2: Parallel Auditor 2 - Incident History Auditor
challenge_incident_auditor = Agent(
    name="challenge_incident_auditor",
    model="gemini-3.6-flash",
    instruction="""You are the CME Incident History Auditor.
Inspect related incidents for the product symbol.
Use `list_incidents_by_product` to check active vs resolved tickets.
Output clear incident pattern analysis.""",
    tools=[list_incidents_by_product],
)

# Stage 3: Support Recommendation Synthesizer
challenge_support_synthesizer = Agent(
    name="challenge_support_synthesizer",
    model="gemini-3.6-flash",
    instruction="""You are the CME Chief Support Desk Manager.
Review triage analysis, market status audit, and incident history findings:
1. Formulate actionable resolution recommendations for internal employees.
2. If ticket status needs updating, use `update_ticket_status`. If a new issue needs logging, use `create_support_ticket`.
3. Provide a clear summary with assigned support team (Market Data Support, Product Support, Platform Operations).
Format output professionally with markdown.""",
    tools=[update_ticket_status, create_support_ticket],
)

# Integrated Challenge Workflow Graph
root_agent = Workflow(
    name="student_challenge",
    edges=[
        ("START", challenge_triage_analyst),
        (challenge_triage_analyst, challenge_market_auditor),
        (challenge_triage_analyst, challenge_incident_auditor),
        (challenge_market_auditor, challenge_support_synthesizer),
        (challenge_incident_auditor, challenge_support_synthesizer),
    ],
)
