"""
Lab 6 Student Challenge:
Security Governance & Observability with ADK Callbacks

Use Case:

Exchange information comes from:
MCP Server -> REST API

Product information comes from:
BigQuery

NEW CONCEPT:
Students will add before-tool and after-tool callbacks
for security governance and observability.

Flow:

User
 ↓
Classifier
 ↓
Router
 ├───────────────────────────┐
 ↓                           ↓
EXCHANGE_INFO              PRODUCT_INFO
 ↓                           ↓
MCP                        BigQuery
 ↓                           ↓
REST API                   exchange_products

Before Tool:
- Input validation
- Permission check
- Business guardrails

After Tool:
- Latency
- Logging
- Observability state
"""

from google.adk import (
    Agent,
    Workflow,
    Event,
    Context,
)

from .tools import exchange_mcp_toolset

from .bigquery_tools import (
    MODEL,
    PROJECT_ID,
    DATASET_ID,
    bigquery_toolset,
)


# ============================================================
# TODO 1: IMPORT CALLBACKS
# ============================================================

# Import the following callbacks from callback_tools:
#
# - before_tool_callback
# - after_tool_callback
#
# TODO:
# Add the required import here.



# ============================================================
# 1. SAVE REQUEST + INFRASTRUCTURE CONTEXT
# ============================================================

def save_original_request(
    ctx: Context,
    node_input: str,
) -> str:

    ctx.state["original_request"] = node_input
    ctx.state["project_id"] = PROJECT_ID
    ctx.state["dataset_id"] = DATASET_ID

    # Context used by callbacks
    ctx.state["request_id"] = "REQ-1001"
    ctx.state["user_id"] = "alice"
    ctx.state["user_authorized"] = True

    return node_input


# ============================================================
# 2. REQUEST CLASSIFIER
# ============================================================

request_classifier = Agent(
    name="exchange_request_classifier",
    model=MODEL,

    instruction="""
Classify the incoming request into exactly ONE category.


EXCHANGE_INFO

Use when the user asks about:

- exchange name
- exchange location
- exchange description
- general information about an exchange

Examples:

"Tell me about NYMEX."
"Where is COMEX located?"
"What is CBOT?"


PRODUCT_INFO

Use when the user asks about:

- products belonging to an exchange
- product symbols associated with an exchange
- products available on an exchange

Examples:

"Which products belong to COMEX?"
"List products available on NYMEX."
"What product symbols belong to CME?"


Return ONLY one of:

EXCHANGE_INFO
PRODUCT_INFO
""",

    output_schema=str,
)


# ============================================================
# 3. ROUTER
# ============================================================

def route_request(
    node_input: str,
    ctx: Context = None,
) -> Event:

    category = node_input.strip().upper()

    allowed_routes = {
        "EXCHANGE_INFO",
        "PRODUCT_INFO",
    }

    if category not in allowed_routes:
        raise ValueError(
            f"Unexpected classifier output: {category}"
        )

    # Store selected route for observability
    if ctx and hasattr(ctx, "state"):
        ctx.state["route"] = category

    return Event(
        route=[category]
    )


# ============================================================
# 4A. EXCHANGE INFORMATION AGENT
# MCP -> REST API
# ============================================================

exchange_info_agent = Agent(
    name="exchange_info_agent",
    model=MODEL,

    instruction="""
You are the CME Exchange Information Specialist.

ORIGINAL USER REQUEST:

{original_request}


Use the MCP tools to retrieve factual exchange information.


Use get_exchange_details when the user asks about:

- exchange name
- exchange location
- exchange description
- general exchange information


Supported exchange codes include:

- CME
- CBOT
- NYMEX
- COMEX


TOOL POLICY:

- Always use the MCP tool for factual exchange information.
- Do not invent exchange details.
- Rely strictly on the MCP tool response.


Return:

EXCHANGE INFORMATION

- Exchange Code
- Exchange Name
- Location
- Description


If the exchange cannot be found, clearly state that.
""",

    tools=[
        exchange_mcp_toolset
    ],

    # ========================================================
    # TODO 2: ADD CALLBACKS
    # ========================================================
    #
    # Add:
    #
    # - before_tool_callback
    # - after_tool_callback
    #
    # These callbacks should intercept MCP tool execution.
    #

)


# ============================================================
# 4B. PRODUCT INFORMATION AGENT
# BIGQUERY
# ============================================================

product_info_agent = Agent(
    name="product_info_agent",
    model=MODEL,

    instruction="""
You are the CME Exchange Product Specialist.

ORIGINAL USER REQUEST:

{original_request}


Google Cloud Project:

{project_id}


BigQuery Dataset:

{dataset_id}


Use the BigQuery tools to retrieve product information.


You may query ONLY:

`{project_id}.{dataset_id}.exchange_products`


IMPORTANT:

- Always use the fully qualified table name.
- Never guess or invent the project ID.
- Never query another project.
- Never query another dataset.
- Use SELECT queries only.
- Never INSERT, UPDATE, DELETE, MERGE, CREATE, DROP or ALTER data.


Steps:

1. Read the original user request.

2. Identify the requested exchange code.

3. Query:

`{project_id}.{dataset_id}.exchange_products`

4. Retrieve:

- exchange_code
- symbol
- product_name
- asset_class

5. Filter using the requested exchange code.

6. Order results by symbol.

7. Return all matching products.


Return:

EXCHANGE PRODUCTS

- Exchange
- Product Symbol
- Product Name
- Asset Class


If no products are found, clearly state that no
matching products were found.

Do not invent information that was not returned by BigQuery.
""",

    tools=[
        bigquery_toolset
    ],

    # ========================================================
    # TODO 3: ADD CALLBACKS
    # ========================================================
    #
    # Add:
    #
    # - before_tool_callback
    # - after_tool_callback
    #
    # These callbacks should intercept BigQuery tool execution.
    #

)


# ============================================================
# 5. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="cme_hybrid_exchange_support",

    edges=[

        (
            "START",
            save_original_request,
            request_classifier,
            route_request,
        ),

        (
            route_request,
            {
                "EXCHANGE_INFO":
                    exchange_info_agent,

                "PRODUCT_INFO":
                    product_info_agent,
            },
        ),
    ],
)