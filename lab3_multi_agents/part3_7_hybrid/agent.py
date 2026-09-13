"""
                         User
                          │
                          ▼
                   Intent / Planner
                          │
              ┌───────────┴────────────┐
              │                        │
        Simple request           Investigation
              │                        │
              ▼                ┌───────┼───────┐
        One specialist          ▼       ▼       ▼
                            Product   Market  Incident
                               │       │       │
                               └───────┼───────┘
                                       ▼
                                     JOIN
                                       │
                                       ▼
                                  Supervisor
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                  Incident exists            No incident +
                          │                    real issue
                          ▼                         │
                   Reference ticket               
                                                  │
                                                  ▼
                                           Create Ticket

Patterns demonstrated:

1. Conditional routing
2. Parallel evidence gathering
3. Join / synchronization
4. Supervisor reasoning
5. Dynamic escalation
6. Deterministic duplicate-ticket guard

Example request:

"Users are reporting problems with NQ.
Investigate the product, current market status and existing incidents,
then recommend what we should do."
"""

from google.adk import Agent, Workflow, Context, Event
from google.adk.workflow import node, JoinNode


try:
    from tools import (
        get_product_details,
        get_market_status,
        list_incidents_by_product,
        get_ticket_details,
        create_support_ticket,
        update_ticket_status,
    )
except ImportError:
    from lab3_multi_agents.tools import (
        get_product_details,
        get_market_status,
        list_incidents_by_product,
        get_ticket_details,
        create_support_ticket,
        update_ticket_status,
    )


MODEL = "gemini-3.8-flash"


# ============================================================
# 1. REQUEST CLASSIFIER / PLANNER
# ============================================================

request_planner = Agent(
    name="request_planner",
    model=MODEL,

    instruction="""
    Classify the CME internal support request into exactly ONE route.

    PRODUCT_ONLY
    Use when the user only wants product information or contract details.

    MARKET_ONLY
    Use when the user only asks whether a product is
    TRADING, HALTED, or CLOSED.

    TICKET_ONLY
    Use when the user gives a specific ticket ID and wants its details.

    INVESTIGATION
    Use when the user reports or suspects a problem and the request
    requires investigation across multiple sources such as:
    - product context
    - market status
    - incidents
    - support ownership
    - recommendation

    Return ONLY one exact route:

    PRODUCT_ONLY
    MARKET_ONLY
    TICKET_ONLY
    INVESTIGATION
""",

    output_schema=str,
)


# ============================================================
# 2. PRESERVE ORIGINAL REQUEST
# ============================================================

def save_original_request(ctx: Context, node_input: str) -> str:

    ctx.state["original_request"] = node_input

    return node_input


# ============================================================
# 3. ROUTER
# ============================================================

def route_request(node_input: str) -> Event:

    route = str(node_input).strip().upper()

    return Event(route=[route])


# ============================================================
# 4. SIMPLE REQUEST AGENTS
# ============================================================

product_only_agent = Agent(
    name="product_only_agent",
    model=MODEL,

    instruction="""
    Original user request:

    {original_request}

    You are the CME Product Specialist.

    Identify the product symbol and call get_product_details.

    Answer only the product question asked by the user.
    """,

        tools=[get_product_details],
)


market_only_agent = Agent(
    name="market_only_agent",
    model=MODEL,

    instruction="""
    Original user request:

    {original_request}

    You are the CME Market Status Specialist.

    Identify the product symbol and call get_market_status.

    Clearly report whether the product is:
    - TRADING
    - HALTED
    - CLOSED
""",

    tools=[get_market_status],
)


ticket_only_agent = Agent(
    name="ticket_only_agent",
    model=MODEL,

    instruction="""
    Original user request:

    {original_request}

    You are the CME Incident Ticket Specialist.

    Identify the ticket ID and call get_ticket_details.

    Return:
    - Ticket ID
    - Product
    - Issue
    - Status
    - Assigned Team
    - Root Cause Notes, if available
""",

    tools=[get_ticket_details],
)


# ============================================================
# 5. INVESTIGATION SPECIALISTS
# ============================================================

product_investigator = Agent(
    name="product_investigator",
    model=MODEL,

    instruction="""
    Original request:

    {original_request}

    You are the Product Investigation Specialist.

    Use get_product_details.

    Return concise evidence:

    PRODUCT FINDINGS
    - Symbol
    - Product Name
    - Asset Class
    - Relevant Product Details
    - Primary Support Team

    Do not investigate incidents.
    Do not make the final decision.
""",

    tools=[get_product_details],

    output_key="product_findings",
)


market_investigator = Agent(
    name="market_investigator",
    model=MODEL,

    instruction="""
    Original request:

    {original_request}

    You are the Market Status Investigation Specialist.

    Use get_market_status.

    Return:

    MARKET FINDINGS
    - Product
    - Current Status
    - Operational Observation

    Do not investigate incidents.
    Do not make the final recommendation.
""",

    tools=[get_market_status],

    output_key="market_findings",
)


incident_investigator = Agent(
    name="incident_investigator",
    model=MODEL,

    instruction="""
    Original request:

    {original_request}

    You are the Incident Investigation Specialist.

    If the request contains a ticket ID:
    use get_ticket_details.

    Otherwise identify the product symbol and use
    list_incidents_by_product.

    Return:

    INCIDENT FINDINGS
    - Existing Incident(s)
    - Ticket ID
    - Issue
    - Status
    - Assigned Team
    - Root Cause Notes

    If nothing relevant exists, clearly return:

    NO EXISTING INCIDENT FOUND

    Do not create a ticket.
    Do not make the final recommendation.
""",

    tools=[
        get_ticket_details,
        list_incidents_by_product,
    ],

    output_key="incident_findings",
)


# ============================================================
# 6. JOIN PARALLEL RESULTS
# ============================================================

investigation_join = JoinNode(
    name="investigation_join"
)


# ============================================================
# 7. SUPERVISOR / EVIDENCE CORRELATION
# ============================================================

investigation_supervisor = Agent(
    name="investigation_supervisor",
    model=MODEL,

    instruction="""
    You are the CME Service Investigation Supervisor.

    Original request:

    {original_request}

    Evidence gathered:

    PRODUCT FINDINGS:
    {product_findings}

    MARKET FINDINGS:
    {market_findings}

    INCIDENT FINDINGS:
    {incident_findings}

    Analyze the evidence together.

    Determine:

    1. What appears to be happening?
    2. Is there already a relevant incident?
    3. Which support team is the best owner?
    4. Is escalation necessary?

    IMPORTANT:

    Do not create a ticket yourself.

    Your output MUST end with exactly one escalation decision:

    ESCALATION_DECISION: NO_ACTION

    or

    ESCALATION_DECISION: USE_EXISTING_INCIDENT

    or

    ESCALATION_DECISION: CREATE_TICKET

    Also return:

    SERVICE INVESTIGATION

    Product:
    ...

    Market Status:
    ...

    Incident:
    ...

    Assessment:
    ...

    Recommended Team:
    ...

    Recommended Action:
    ...
""",

    output_key="supervisor_result",
)


# ============================================================
# 8. DYNAMIC ESCALATION STEP
# ============================================================

ticket_creation_agent = Agent(
    name="ticket_creation_agent",
    model=MODEL,

    instruction="""
    You are the CME Ticket Creation Specialist.

    Original request:

    {original_request}

    Supervisor investigation:

    {supervisor_result}

    Create a ticket only because the supervisor explicitly determined:

    ESCALATION_DECISION: CREATE_TICKET

    Use create_support_ticket.

    Choose the most appropriate support team based on the investigation.

    Return:

    NEW TICKET
    - Ticket ID
    - Product
    - Issue Type
    - Assigned Team
    - Status
""",

    tools=[create_support_ticket],
)


@node(rerun_on_resume=True)
async def handle_escalation(
    ctx: Context,
    node_input: str
) -> str:

    supervisor_result = str(
        ctx.state.get("supervisor_result", node_input)
    )

    normalized = supervisor_result.upper()


    # --------------------------------------------------------
    # Existing incident:
    # never create a duplicate
    # --------------------------------------------------------

    if "ESCALATION_DECISION: USE_EXISTING_INCIDENT" in normalized:

        return supervisor_result


    # --------------------------------------------------------
    # No escalation required
    # --------------------------------------------------------

    if "ESCALATION_DECISION: NO_ACTION" in normalized:

        return supervisor_result


    # --------------------------------------------------------
    # Create ticket only when supervisor explicitly requests it
    # --------------------------------------------------------

    if "ESCALATION_DECISION: CREATE_TICKET" in normalized:

        ticket_result = await ctx.run_node(
            ticket_creation_agent,
            node_input=supervisor_result,
        )

        return f"""
{supervisor_result}

{ticket_result}
"""


    # --------------------------------------------------------
    # Safe fallback
    # --------------------------------------------------------

    return f"""
{supervisor_result}

Escalation could not be determined safely.
No ticket was created.
"""


# ============================================================
# 9. INVESTIGATION WORKFLOW
# ============================================================

investigation_workflow = Workflow(
    name="investigation_workflow",

    edges=[
        (
            "START",
            (
                product_investigator,
                market_investigator,
                incident_investigator,
            ),
            investigation_join,
            investigation_supervisor,
            handle_escalation,
        )
    ],
)


# ============================================================
# 10. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="cme_intelligent_service_investigation",

    edges=[

        # Save the original request first
        (
            "START",
            save_original_request,
            request_planner,
            route_request,
        ),

        # Route to efficient execution path
        (
            route_request,
            {
                "PRODUCT_ONLY": product_only_agent,
                "MARKET_ONLY": market_only_agent,
                "TICKET_ONLY": ticket_only_agent,
                "INVESTIGATION": investigation_workflow,
            },
        ),
    ],
)