"""
Lab 7 Part 3
CME Support Agent with Session Context + Vertex AI Memory Bank

LLM responsibilities:
- Understand the user's request
- Select the appropriate support route
- Resolve the CME product symbol
- Identify where the symbol came from

Application responsibilities:
- Execute the selected specialist agent
- Apply deterministic security/tool guardrails
"""

from typing import Optional

from pydantic import BaseModel

from google.adk import Agent, Workflow, Event, Context
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

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
# CLASSIFIER OUTPUT
# ============================================================

class RequestClassification(BaseModel):
    route: str
    symbol: Optional[str] = None
    symbol_source: str


# ============================================================
# SAVE REQUEST CONTEXT
# ============================================================

def save_request_context(
    ctx: Context,
    node_input,
):

    ctx.state["previous_request"] = (
        ctx.state.get("current_request", "")
    )

    ctx.state["previous_symbol"] = (
        ctx.state.get("current_symbol", "")
    )

    ctx.state["current_request"] = node_input

    ctx.state["project_id"] = PROJECT_ID
    ctx.state["dataset_id"] = DATASET_ID

    if "user_authorized" not in ctx.state:
        ctx.state["user_authorized"] = False

    return node_input


# ============================================================
# LLM CLASSIFIER
# ============================================================

request_classifier = Agent(

    name="request_classifier",

    model=MODEL,

    description="""
    Understands CME support requests and routes them using
    current conversation context and long-term memory.
    """,

    instruction="""
Understand the user's request and intent, and then return:

- route
- symbol
- symbol_source

Classify the user's request by meaning, not keywords.

Available routes:

PRODUCT_SUPPORT
Use for CME product information such as contract size,
asset class, currency, or product details.

MARKET_STATUS_SUPPORT
Use for current trading status such as open, closed,
or halted.

INCIDENT_SUPPORT
Use for incidents, outages, or operational issues.

MEMORY_UPDATE
Use when the user is giving durable information or
preferences that should be useful in future conversations.


Resolve the product symbol using:

EXPLICIT
- Symbol is present in the current request.

SESSION
- The request refers to a product established earlier
  in the current conversation.

MEMORY
- The request relies on context remembered from
  previous conversations.

NONE
- No symbol can be safely determined.


Current request:
{current_request}

Previous request:
{previous_request}

Previous symbol:
{previous_symbol}


Examples:

"What is the contract size of NQ?"
→ PRODUCT_SUPPORT, NQ, EXPLICIT

"Is it currently trading?"
with previous_symbol=NQ
→ MARKET_STATUS_SUPPORT, NQ, SESSION

"Remember that NQ is my primary product."
→ MEMORY_UPDATE, NQ, EXPLICIT

"Is my preferred product currently trading?"
with remembered preference NQ
→ MARKET_STATUS_SUPPORT, NQ, MEMORY


Prefer current-session context over long-term memory.

Do not guess a symbol.
""",

    tools=[
        PreloadMemoryTool(),
    ],

    output_schema=RequestClassification,
)


# ============================================================
# ROUTER
# ============================================================

def route_request(
    node_input: RequestClassification,
    ctx: Context,
):

    route = node_input.route.strip().upper()

    symbol = (
        node_input.symbol.strip().upper()
        if node_input.symbol
        else ""
    )

    source = (
        node_input.symbol_source.strip().upper()
        if node_input.symbol_source
        else "NONE"
    )


    ctx.state["route"] = route
    ctx.state["current_symbol"] = symbol
    ctx.state["symbol_resolution_source"] = source


    print("\n[CONTEXT RESOLUTION]")
    print(f"Route              : {route}")
    print(f"Resolved Symbol    : {symbol or 'NONE'}")
    print(f"Resolution Source  : {source}")


    return Event(
        route=[route]
    )


# ============================================================
# MEMORY UPDATE AGENT
# ============================================================

memory_update_agent = Agent(

    name="memory_update_agent",

    model=MODEL,

    description="""
    Handles user information or preferences intended for
    future conversational context.
    """,

    instruction="""
The user is providing information that should be useful
in future conversations.

Current request:
{current_request}

Acknowledge it briefly and naturally.

Do not query BigQuery or MCP.

The application handles Memory Bank persistence.
""",
)


# ============================================================
# PRODUCT SUPPORT AGENT
# ============================================================

product_support_agent = Agent(

    name="product_support_agent",

    model=MODEL,

    description="""
    Retrieves CME product information from BigQuery.
    """,

    instruction="""
Answer the user's CME product question.

Current request:
{current_request}

Resolved symbol:
{current_symbol}

Use BigQuery table:

{project_id}.{dataset_id}.products

Retrieve only the information needed.

Only SELECT queries are allowed.

Return a concise answer.
""",

    tools=[
        bigquery_toolset,
    ],

    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


# ============================================================
# MARKET STATUS AGENT
# ============================================================

market_status_support_agent = Agent(

    name="market_status_support_agent",

    model=MODEL,

    description="""
    Retrieves current CME market status from BigQuery.
    """,

    instruction="""
Answer the user's market-status question.

Current request:
{current_request}

Resolved symbol:
{current_symbol}

Use BigQuery table:

{project_id}.{dataset_id}.market_status

Retrieve the latest relevant status.

Only SELECT queries are allowed.

Return a concise answer.
""",

    tools=[
        bigquery_toolset,
    ],

    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


# ============================================================
# INCIDENT SUPPORT AGENT
# ============================================================

incident_support_agent = Agent(

    name="incident_support_agent",

    model=MODEL,

    description="""
    Retrieves CME operational incident information using MCP.
    """,

    instruction="""
Answer the user's operational incident question.

Current request:
{current_request}

Resolved symbol:
{current_symbol}

Use the incident MCP tools as the source of truth.

Return a concise answer.
""",

    tools=[
        incident_mcp_toolset,
    ],

    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


# ============================================================
# ROOT WORKFLOW
# ============================================================

root_agent = Workflow(

    name="cme_support_memorybank_router",

    edges=[

        (
            "START",
            save_request_context,
            request_classifier,
            route_request,
        ),

        (
            route_request,
            {
                "PRODUCT_SUPPORT":
                    product_support_agent,

                "MARKET_STATUS_SUPPORT":
                    market_status_support_agent,

                "INCIDENT_SUPPORT":
                    incident_support_agent,

                "MEMORY_UPDATE":
                    memory_update_agent,
            },
        ),
    ],
)