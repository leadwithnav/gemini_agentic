"""
Lab 6 Part 1:
ADK Callback Agents with Security Governance,
Session Context & Observability

Use Case:
Route CME support requests to specialist agents while:
- resolving conversational follow-up context
- persisting product symbol in session state
- validating tool calls with before_tool_callback
- logging/sanitizing tool results with after_tool_callback

Flow:

User Request
     ↓
Save Current Request + Infrastructure Context
     ↓
Request Classifier / Context Resolver
     │
     ├── Resolve Route
     └── Resolve Product Symbol
     ↓
Save Resolved Context in Session State
     ↓
Router
     ↓
 ┌──────────────────┬──────────────────────┬──────────────────┐
 ↓                  ↓                      ↓
INCIDENT_SUPPORT   MARKET_STATUS_SUPPORT  PRODUCT_SUPPORT
 ↓                  ↓                      ↓
MCP Server         BigQuery               BigQuery
     │                  │                      │
     └──────────────────┴──────────────────────┘
                        ↓
               BEFORE TOOL CALLBACK
        Pydantic / Permission / Guardrail checks
                        ↓
                  TOOL EXECUTES
                        ↓
                AFTER TOOL CALLBACK
          Logging / Latency / Sanitization
"""


from typing import Optional, Literal
from pydantic import BaseModel

from google.adk import Agent, Workflow, Event, Context


# ============================================================
# IMPORTS
# ===========================================================
from ...tools.mcp_tools import incident_mcp_toolset
from ...tools.bigquery_tools import (
        MODEL,
        PROJECT_ID,
        DATASET_ID,
        bigquery_toolset,
    )

from ...callbacks.callback_tools import (
        before_tool_callback,
        after_tool_callback,
    )


# ============================================================
# 1. STRUCTURED CLASSIFIER OUTPUT
# ============================================================

class RequestClassification(BaseModel):

    route: Literal[
        "INCIDENT_SUPPORT",
        "MARKET_STATUS_SUPPORT",
        "PRODUCT_SUPPORT",
    ]

    symbol: Optional[str] = None


# ============================================================
# 2. SAVE CURRENT USER REQUEST
# ============================================================

def save_request_context(
    ctx: Context,
    node_input: str,
) -> str:
    """
    Save current request and preserve previous conversational context.
    """

    # --------------------------------------------------------
    # Preserve previous request
    # --------------------------------------------------------

    current_request = ctx.state.get("current_request")

    if current_request:
        ctx.state["previous_request"] = current_request

    # --------------------------------------------------------
    # Preserve previous route
    # --------------------------------------------------------

    current_route = ctx.state.get("route")

    if current_route:
        ctx.state["previous_route"] = current_route

    # --------------------------------------------------------
    # Preserve previous symbol
    # --------------------------------------------------------

    current_symbol = ctx.state.get("current_symbol")

    if current_symbol:
        ctx.state["previous_symbol"] = current_symbol

    # --------------------------------------------------------
    # Current request
    # --------------------------------------------------------

    ctx.state["current_request"] = node_input

    # --------------------------------------------------------
    # Deterministic infrastructure context
    # --------------------------------------------------------

    ctx.state["project_id"] = PROJECT_ID
    ctx.state["dataset_id"] = DATASET_ID

    # Demo identity
    ctx.state["user_id"] = "alice"
    ctx.state["user_authorized"] = True

    return node_input


# ============================================================
# 3. REQUEST CLASSIFIER + CONTEXT RESOLVER
# ============================================================

request_classifier = Agent(

    name="request_classifier",

    model=MODEL,

    instruction="""
You are the CME support request classifier and context resolver.

Your job is to determine:

1. The support route
2. The CME product symbol relevant to the request

--------------------------------------------------
ROUTES
--------------------------------------------------

INCIDENT_SUPPORT

Use when the request is about:

- existing incidents
- reported issues
- support tickets
- incident status
- issues affecting a CME product


MARKET_STATUS_SUPPORT

Use when the request is about:

- whether a product is currently trading
- trading status
- halted markets
- closed markets
- market availability


PRODUCT_SUPPORT

Use when the request is about:

- contract size
- product information
- asset class
- currency
- product specifications
- general futures product details


--------------------------------------------------
SYMBOL RESOLUTION
--------------------------------------------------

Extract the CME product symbol explicitly mentioned by the user.

Examples:

"What is the contract size of NQ?"
→ symbol = NQ

"Is ES currently trading?"
→ symbol = ES

"Any incidents affecting CL?"
→ symbol = CL


--------------------------------------------------
FOLLOW-UP CONTEXT
--------------------------------------------------

The current request may be a follow-up to an earlier request.

Use conversation/session context when necessary.

Examples:

Previous request:
"What is the contract size of NQ?"

Current request:
"Is it currently trading?"

Resolve:

route = MARKET_STATUS_SUPPORT
symbol = NQ


Previous request:
"Is NQ currently trading?"

Current request:
"What about ES?"

Resolve:

route = MARKET_STATUS_SUPPORT
symbol = ES


Previous request:
"Tell me about GC"

Current request:
"Are there any incidents affecting it?"

Resolve:

route = INCIDENT_SUPPORT
symbol = GC


--------------------------------------------------
IMPORTANT RULES
--------------------------------------------------

- If the user explicitly provides a new symbol, use the new symbol.

- If the current request refers to:
  "it",
  "that product",
  "this contract",
  or otherwise omits the symbol,
  use previous conversation context when it is clear.

- Do NOT blindly preserve the previous route.

Example:

Previous:
"What is the contract size of NQ?"

Current:
"Is it currently trading?"

Previous route = PRODUCT_SUPPORT

But current route MUST be:

MARKET_STATUS_SUPPORT


- Preserve previous intent only when the current message changes
  only the product.

Example:

Previous:
"Is NQ currently trading?"

Current:
"What about ES?"

Result:

route = MARKET_STATUS_SUPPORT
symbol = ES


- Never invent a product symbol.

- If no product symbol can be confidently resolved,
  return symbol = null.
""",

    output_schema=RequestClassification,
)


# ============================================================
# 4. STORE RESOLVED CONTEXT + ROUTE
# ============================================================

def route_request(
    node_input: RequestClassification,
    ctx: Context,
) -> Event:
    """
    Store classifier result in session state and route
    to the appropriate specialist agent.
    """

    route = node_input.route
    symbol = node_input.symbol

    # --------------------------------------------------------
    # Store resolved route
    # --------------------------------------------------------

    ctx.state["route"] = route

    # --------------------------------------------------------
    # Store resolved symbol
    # --------------------------------------------------------

    if symbol:

        normalized_symbol = symbol.strip().upper()

        ctx.state["current_symbol"] = normalized_symbol

    # --------------------------------------------------------
    # Route workflow
    # --------------------------------------------------------

    return Event(
        route=[route]
    )


# ============================================================
# 5A. INCIDENT SUPPORT AGENT
# ============================================================

incident_support_agent = Agent(

    name="incident_support_agent",

    model=MODEL,

    instruction="""
You are the CME Incident Support specialist.

CURRENT USER REQUEST:

{current_request}

RESOLVED PRODUCT SYMBOL:

{current_symbol}

Your job is to check incidents affecting the resolved product.

Use the resolved product symbol from session state.

Do NOT independently guess another symbol.

Steps:

1. Use the resolved product symbol.

2. Call the appropriate MCP tool:

   - get_incidents_by_symbol

   OR

   - get_incident_by_id
     if the user explicitly supplied an incident ID.

3. Summarize the tool result.

Return:

- Product
- Incident ID
- Issue
- Status
- Assigned Team

If no incidents exist, clearly state that.

Do not invent incident information.
""",

    tools=[
        incident_mcp_toolset,
    ],

    before_tool_callback=before_tool_callback,

    after_tool_callback=after_tool_callback,
)


# ============================================================
# 5B. MARKET STATUS SUPPORT AGENT
# ============================================================

market_status_support_agent = Agent(

    name="market_status_support_agent",

    model=MODEL,

    instruction="""
You are the CME Market Status Support specialist.

CURRENT USER REQUEST:

{current_request}

RESOLVED PRODUCT SYMBOL:

{current_symbol}

GOOGLE CLOUD PROJECT:

{project_id}

BIGQUERY DATASET:

{dataset_id}


Use the resolved product symbol from session state.

You may query ONLY:

`{project_id}.{dataset_id}.market_status`


IMPORTANT:

- Always use the fully qualified table name.
- Never guess the project ID.
- Never guess the dataset.
- Never query another project.
- Never query another dataset.
- Use SELECT queries only.
- Never use:
  INSERT
  UPDATE
  DELETE
  MERGE
  CREATE
  DROP
  ALTER


Steps:

1. Use:

   symbol = {current_symbol}

2. Query:

   `{project_id}.{dataset_id}.market_status`

3. Retrieve:

   - symbol
   - trading_status
   - status_reason
   - last_updated

4. Filter by the resolved symbol.

5. Retrieve the latest record:

   ORDER BY last_updated DESC
   LIMIT 1

6. Report the result clearly.


Return:

- Product Symbol
- Trading Status
- Status Reason
- Last Updated


Do not invent information not returned by BigQuery.
""",

    tools=[
        bigquery_toolset,
    ],

    before_tool_callback=before_tool_callback,

    after_tool_callback=after_tool_callback,
)


# ============================================================
# 5C. PRODUCT SUPPORT AGENT
# ============================================================

product_support_agent = Agent(

    name="product_support_agent",

    model=MODEL,

    instruction="""
You are the CME Product Support specialist.

CURRENT USER REQUEST:

{current_request}

RESOLVED PRODUCT SYMBOL:

{current_symbol}

GOOGLE CLOUD PROJECT:

{project_id}

BIGQUERY DATASET:

{dataset_id}


Use the resolved product symbol from session state.

You may query ONLY:

`{project_id}.{dataset_id}.products`


IMPORTANT:

- Always use the fully qualified table name.
- Never guess the project ID.
- Never guess the dataset.
- Never query another project.
- Never query another dataset.
- Use SELECT queries only.

Never use:

INSERT
UPDATE
DELETE
MERGE
CREATE
DROP
ALTER


Steps:

1. Use:

   symbol = {current_symbol}

2. Query:

   `{project_id}.{dataset_id}.products`

3. Retrieve only the columns needed to answer
   the user's question.

Available columns:

- symbol
- product_name
- asset_class
- contract_size
- currency
- primary_support_team

4. Filter by the resolved symbol.

5. For a single product lookup use:

   LIMIT 1

6. Answer the user's current request using
   only the BigQuery result.

Do not invent information.
""",

    tools=[
        bigquery_toolset,
    ],

    before_tool_callback=before_tool_callback,

    after_tool_callback=after_tool_callback,
)


# ============================================================
# 6. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(

    name="cme_support_session_router",

    edges=[

        # ----------------------------------------------------
        # Request → State → Classification → Routing
        # ----------------------------------------------------

        (
            "START",

            save_request_context,

            request_classifier,

            route_request,
        ),

        # ----------------------------------------------------
        # Route to specialist
        # ----------------------------------------------------

        (
            route_request,

            {
                "INCIDENT_SUPPORT":
                    incident_support_agent,

                "MARKET_STATUS_SUPPORT":
                    market_status_support_agent,

                "PRODUCT_SUPPORT":
                    product_support_agent,
            },
        ),
    ],
)