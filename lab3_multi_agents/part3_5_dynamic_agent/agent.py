"""
Part 3.5: Dynamic Adaptive Workflow (ADK V2)

Use Case:
CME Internal Help Desk Assistant

Dynamic Behavior:
1. Understand the user's request.
2. Dynamically invoke the required specialist.
3. Optionally invoke additional specialists if more information is needed.
4. If an issue exists but no incident is found, optionally create a support ticket.
5. Return one consolidated response."""



from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

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
# 1. INTENT / PLAN AGENT
# ============================================================

helpdesk_planner = Agent(
    name="helpdesk_planner",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Help Desk Planner.

Analyze the user's request and decide which capabilities are required.

Available capabilities:

PRODUCT
Use when product details or contract information are required.

INCIDENT
Use when the user asks about incidents, tickets,
reported problems, or existing support cases.

MARKET_STATUS
Use when the user asks whether a product is
TRADING, HALTED, or CLOSED.

CREATE_TICKET
Use only when the user clearly wants an issue logged
or when the workflow indicates that a reported problem
has no existing incident.

You may select MORE THAN ONE capability.

Return a comma-separated list only.

Examples:

PRODUCT

INCIDENT

MARKET_STATUS

MARKET_STATUS,INCIDENT

INCIDENT,CREATE_TICKET
"""
)


# ============================================================
# 2. PRODUCT SPECIALIST
# ============================================================

product_specialist = Agent(
    name="product_specialist",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Product Specialist.

Use get_product_details when product information
is required.

Use the original user request to identify the symbol.

Return only the information relevant to the request.
""",

    tools=[get_product_details],
)


# ============================================================
# 3. INCIDENT SPECIALIST
# ============================================================

incident_specialist = Agent(
    name="incident_specialist",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Incident Specialist.

Use the original request to identify either:
- ticket ID, or
- product symbol.

Use:
- get_ticket_details when a ticket ID is given.
- list_incidents_by_product when a product symbol is given.

Return:
- incident ID
- status
- description
- assigned team

Clearly state when no incidents are found.
""",

    tools=[
        get_ticket_details,
        list_incidents_by_product,
    ],
)


# ============================================================
# 4. MARKET STATUS SPECIALIST
# ============================================================

market_status_specialist = Agent(
    name="market_status_specialist",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Market Status Specialist.

Use get_market_status to determine whether
the requested product is:

TRADING
HALTED
CLOSED

Return a concise operational status.
""",

    tools=[get_market_status],
)


# ============================================================
# 5. TICKET CREATION SPECIALIST
# ============================================================

ticket_creation_specialist = Agent(
    name="ticket_creation_specialist",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Support Ticket Creation Agent.

Create a ticket only when instructed by the workflow.

Use create_support_ticket.

Choose the assigned team based on the issue:

Market-related operational issue
-> Platform Operations

Incident/data issue
-> Market Data Support

Product-information issue
-> Product Support

Return the created ticket ID and assigned team.
""",

    tools=[create_support_ticket],
)


# ============================================================
# 6. FINAL RESPONSE AGENT
# ============================================================

response_aggregator = Agent(
    name="response_aggregator",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Help Desk Response Coordinator.

Combine the information collected by the specialists.

Provide a concise final response containing only
relevant information.

Do not invent data.
Do not call tools.
"""
)


# ============================================================
# 7. DYNAMIC WORKFLOW
# ============================================================

@node(rerun_on_resume=True)
async def dynamic_helpdesk_workflow(
    ctx: Context,
    node_input: str
) -> str:

    original_request = node_input

    # --------------------------------------------------------
    # Step 1: Decide dynamically which capabilities are needed
    # --------------------------------------------------------

    plan_raw = await ctx.run_node(
        helpdesk_planner,
        node_input=original_request
    )

    plan = str(plan_raw).upper()

    results = []


    # --------------------------------------------------------
    # Step 2: Dynamically execute selected specialists
    # --------------------------------------------------------

    if "PRODUCT" in plan:

        product_result = await ctx.run_node(
            product_specialist,
            node_input=original_request
        )

        results.append(
            f"PRODUCT RESULT:\n{product_result}"
        )


    if "MARKET_STATUS" in plan:

        status_result = await ctx.run_node(
            market_status_specialist,
            node_input=original_request
        )

        results.append(
            f"MARKET STATUS RESULT:\n{status_result}"
        )


    if "INCIDENT" in plan:

        incident_result = await ctx.run_node(
            incident_specialist,
            node_input=original_request
        )

        results.append(
            f"INCIDENT RESULT:\n{incident_result}"
        )


        # ----------------------------------------------------
        # Adaptive Behavior:
        #
        # If user is reporting a real issue AND
        # no incident exists, dynamically create a ticket.
        # ----------------------------------------------------

        incident_text = str(incident_result).lower()

        issue_words = [
            "problem",
            "issue",
            "error",
            "delay",
            "halt",
            "failure",
        ]

        user_is_reporting_issue = any(
            word in original_request.lower()
            for word in issue_words
        )

        no_incident_found = (
            "no incident" in incident_text
            or "no incidents" in incident_text
            or "not found" in incident_text
        )

        if user_is_reporting_issue and no_incident_found:

            ticket_result = await ctx.run_node(
                ticket_creation_specialist,
                node_input=f"""
Original request:

{original_request}

No existing incident was found.

Create an appropriate support ticket.
"""
            )

            results.append(
                f"TICKET CREATED:\n{ticket_result}"
            )


    # --------------------------------------------------------
    # Step 3: Explicit ticket creation request
    # --------------------------------------------------------

    elif "CREATE_TICKET" in plan:

        ticket_result = await ctx.run_node(
            ticket_creation_specialist,
            node_input=original_request
        )

        results.append(
            f"TICKET CREATED:\n{ticket_result}"
        )


    # --------------------------------------------------------
    # Step 4: Final aggregation
    # --------------------------------------------------------

    combined_results = "\n\n".join(results)

    final_response = await ctx.run_node(
        response_aggregator,
        node_input=f"""
Original user request:

{original_request}

Specialist results:

{combined_results}
"""
    )

    return final_response


# ============================================================
# 8. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="part3_5_dynamic_helpdesk",

    edges=[
        (
            "START",
            dynamic_helpdesk_workflow
        )
    ],
)