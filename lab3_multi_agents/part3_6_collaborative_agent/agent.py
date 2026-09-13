"""
Part 3.6: Collaborative Multi-Agent Team (ADK V2)

Use Case:
Collaboratively investigate a CME service issue.

Example:
"NQ appears to be having a problem.
Check the product, current market status, existing incidents,
and recommend what our support team should do."

Collaboration:

                    Supervisor
               /        |         \
              /         |          \
     Product Agent   Incident Agent  Market Status Agent
              \         |          /
               \        |         /
                  Supervisor
                       |
                       v
                Recommendation
                       |
              optional escalation
                       |
                       v
               Ticket Creation Agent
"""

from google.adk.agents import LlmAgent

try:
    from tools import (
        get_product_details,
        get_ticket_details,
        get_market_status,
        list_incidents_by_product,
        create_support_ticket,
    )
except ImportError:
    from lab3_multi_agents.tools import (
        get_product_details,
        get_ticket_details,
        get_market_status,
        list_incidents_by_product,
        create_support_ticket,
    )


# ============================================================
# PEER 1: PRODUCT SPECIALIST
# ============================================================

product_agent = LlmAgent(
    name="product_agent",
    model="gemini-3.8-flash",
    mode="single_turn",

    description=(
        "Investigates CME product information including product name, "
        "contract details, asset class, trading status metadata, "
        "and primary support team."
    ),

    instruction="""
    You are the CME Product Specialist.

    You are one member of a collaborative investigation team.
    Your responsibility is ONLY product context.
    When asked to investigate a CME product:

    1. Identify the product symbol such as ES, NQ, CL, or GC.
    2. Call get_product_details.
    3. Return relevant product information.
    4. Highlight the primary support team if available.

    Your response should include:

    PRODUCT FINDINGS
    - Symbol
    - Product Name
    - Asset Class
    - Relevant Product Details
    - Primary Support Team

    Do not investigate incidents.
    Do not create tickets.
    Do not make the final investigation decision.
""",

    tools=[
        get_product_details,
    ],
)


# ============================================================
# PEER 2: INCIDENT SPECIALIST
# ============================================================

incident_agent = LlmAgent(
    name="incident_agent",
    model="gemini-3.8-flash",
    mode="single_turn",

    description=(
        "Investigates existing CME incidents and support tickets "
        "using either a product symbol or incident ticket ID."
    ),

    instruction="""
    You are the CME Incident Specialist.

    You are one member of a collaborative investigation team.

    Your responsibility is ONLY incident investigation.

    Use:

    - get_ticket_details
    when a specific ticket ID such as INC-101 is provided.

    - list_incidents_by_product
    when a product symbol such as NQ or ES is provided.

    Return:

    INCIDENT FINDINGS
    - Existing Incident(s)
    - Ticket ID
    - Description
    - Status
    - Assigned Team
    - Root Cause Notes, if available

    If no existing incident exists, clearly state:

    NO EXISTING INCIDENT FOUND

    Do not create a new ticket.
    Do not investigate product specifications.
    Do not make the final recommendation.
""",

    tools=[
        get_ticket_details,
        list_incidents_by_product,
    ],
)


# ============================================================
# PEER 3: MARKET STATUS SPECIALIST
# ============================================================

market_status_agent = LlmAgent(
    name="market_status_agent",
    model="gemini-3.8-flash",
    mode="single_turn",

    description=(
        "Checks the current operational trading status of a CME "
        "product and determines whether it is TRADING, HALTED, or CLOSED."
    ),

    instruction="""
    You are the CME Market Status Specialist.

    You are one member of a collaborative investigation team.

    Your responsibility is ONLY current market operational status.

    1. Identify the CME product symbol.
    2. Call get_market_status.
    3. Return the operational status.

    Return:

    MARKET STATUS FINDINGS
    - Product
    - Current Status
    - TRADING / HALTED / CLOSED
    - Short operational observation

    Do not investigate incidents.
    Do not create tickets.
    Do not make the final investigation recommendation.

""",

    tools=[
        get_market_status,
    ],
)


# ============================================================
# PEER 4: TICKET CREATION SPECIALIST
# ============================================================

ticket_creation_agent = LlmAgent(
    name="ticket_creation_agent",
    model="gemini-3.8-flash",
    mode="single_turn",

    description=(
        "Creates a new CME support ticket when the supervisor "
        "determines that escalation is required."
    ),

    instruction="""
    You are the CME Ticket Creation Specialist.

    Only create a ticket when the supervisor explicitly asks you to do so.

    Use create_support_ticket.

    Determine the appropriate assigned team from the investigation context:

    - Market-data or latency issue
    -> Market Data Support

    - Product information/specification issue
    -> Product Support

    - Trading status/platform operational issue
    -> Platform Operations

    Return:

    TICKET CREATION RESULT
    - Ticket ID
    - Product
    - Issue Type
    - Assigned Team
    - Status

    Do not independently decide whether escalation is required.
    That decision belongs to the supervisor.
""",

    tools=[
        create_support_ticket,
    ],
)


# ============================================================
# ROOT SUPERVISOR
# ============================================================

root_agent = LlmAgent(
    name="part3_6_collaborative_support_team",
    model="gemini-3.8-flash",

    instruction="""
    You are the CME Internal Help Desk Supervisor.

    Collaborate with your specialist agents to investigate the user's service issue.

    For a comprehensive service issue:

    1. Ask product_agent for product context.
    2. Ask market_status_agent for current trading status.
    3. Ask incident_agent to check existing incidents.
    4. Compare their findings and recommend the appropriate action.

    If a relevant incident already exists:
    - reference the existing incident
    - do NOT create another ticket.

    If the user reports a genuine issue and no relevant
    incident exists:
    - ask ticket_creation_agent to create a support ticket.

    Return one consolidated investigation summary.

    Do not perform specialist work yourself.
    Do not invent information.
""",

    sub_agents=[
        product_agent,
        incident_agent,
        market_status_agent,
        ticket_creation_agent,
    ],
)