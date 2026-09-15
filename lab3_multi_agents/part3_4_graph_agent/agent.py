"""
Part 3.4: Conditional Routing + State Workflow (ADK V2)

Use Case:
Route a CME support request to the correct specialist while
preserving the original user request in workflow state.

Flow:

User Request
     ↓
Save Original Request in State
     ↓
Request Classifier
     ↓
Router
     ↓
 ┌──────────────────┬──────────────────────┬──────────────────┐
 ↓                  ↓                      ↓
INCIDENT_SUPPORT   MARKET_STATUS_SUPPORT  PRODUCT_SUPPORT
"""

from google.adk import Agent, Workflow, Event, Context

try:
    from tools import (
        get_product_details,
        get_market_status,
        list_incidents_by_product,
    )
except ImportError:
    from lab3_multi_agents.tools import (
        get_product_details,
        get_market_status,
        list_incidents_by_product,
    )


# ============================================================
# 1. SAVE ORIGINAL USER REQUEST IN STATE
# ============================================================

def save_original_request(ctx: Context, node_input: str) -> str:
    """
    Save the original user request in shared workflow state.

    Return the same request so the classifier receives it.
    """

    ctx.state["original_request"] = node_input

    return node_input


# ============================================================
# 2. REQUEST CLASSIFIER
# ============================================================

request_classifier = Agent(
    name="request_classifier",
    model="gemini-3.8-flash",

    instruction="""
Classify the incoming CME support request into exactly ONE category.

INCIDENT_SUPPORT
Use when the request is about:
- existing incidents
- reported issues
- support tickets
- incident status
- problems affecting a product

MARKET_STATUS_SUPPORT
Use when the request is about:
- current trading status
- whether a product is trading
- halted markets
- closed markets

PRODUCT_SUPPORT
Use when the request is about:
- product information
- contract specifications
- contract size
- general futures product details

Return ONLY one of these exact values:

INCIDENT_SUPPORT
MARKET_STATUS_SUPPORT
PRODUCT_SUPPORT
""",

    output_schema=str,
)


# ============================================================
# 3. ROUTER
# ============================================================

def route_request(node_input: str) -> Event:
    """
    The classifier has already made the decision.

    This node only converts that decision into a graph route.
    """

    category = node_input.strip().upper()

    return Event(route=[category])


# ============================================================
# 4A. INCIDENT SUPPORT
# ============================================================

incident_support_agent = Agent(
    name="incident_support_agent",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Incident Support specialist.

The ORIGINAL USER REQUEST was:

{original_request}

Use the original request above to identify the CME product symbol.

Your responsibility is to check incidents affecting that product.

Steps:

1. Extract the product symbol from the original request.
2. Call list_incidents_by_product using that symbol.
3. Summarize the incident information.

Return:
- Product
- Incident ID
- Issue
- Status
- Assigned Team

If no incidents exist, clearly state that.

IMPORTANT:
Do NOT ask the user for the symbol if it is already present
in the original request.
""",

    tools=[
        list_incidents_by_product,
    ],
)


# ============================================================
# 4B. MARKET STATUS SUPPORT
# ============================================================

market_status_support_agent = Agent(
    name="market_status_support_agent",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Market Status Support specialist.

The ORIGINAL USER REQUEST was:

{original_request}

Use the original request above to identify the CME product symbol.

Steps:

1. Extract the product symbol.
2. Call get_market_status.
3. Report the current trading status.

Return:
- Product
- Trading Status
- Short explanation

IMPORTANT:
Do NOT ask the user for the symbol if it is already present
in the original request.
""",

    tools=[
        get_market_status,
    ],
)


# ============================================================
# 4C. PRODUCT SUPPORT
# ============================================================

product_support_agent = Agent(
    name="product_support_agent",
    model="gemini-3.8-flash",

    instruction="""
You are the CME Product Support specialist.

The ORIGINAL USER REQUEST was:

{original_request}

Use the original request above to identify the CME product symbol
and understand what product information the user needs.

Steps:

1. Extract the product symbol.
2. Call get_product_details.
3. Answer the original product question.

Handle:
- contract size
- product information
- contract specifications
- asset class
- general product details

IMPORTANT:
Do NOT ask the user for the symbol if it is already present
in the original request.
""",

    tools=[
        get_product_details,
    ],
)


# ============================================================
# 5. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="part3_4_support_routing",

    edges=[

        # Preserve the original request first
        (
            "START",
            save_original_request,
            request_classifier,
            route_request,
        ),

        # Execute only the selected branch
        (
            route_request,
            {
                "INCIDENT_SUPPORT": incident_support_agent,
                "MARKET_STATUS_SUPPORT": market_status_support_agent,
                "PRODUCT_SUPPORT": product_support_agent,
            },
        ),
    ],
)