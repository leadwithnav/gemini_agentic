"""
Lab 6: Collaborative Multi-Agent CME Support

Patterns demonstrated:

1. Product Support Agent
   - Dynamic schema discovery
   - Agent decides when/how to use get_table_info and execute_sql

2. Market Status Agent
   - Static schema
   - Schema is supplied in the system instruction

3. Supervisor
   - Delegates to the appropriate specialist(s)
   - Synthesizes multi-agent results
"""

from google.adk import Agent,Workflow,Context

from .tools.bigquery_tools import (
    bigquery_toolset,
    DATASET_ID,
    PROJECT_ID,
)

from .callbacks.callback_tools import (
    before_tool_callback,
    after_tool_callback,
)

from .callbacks.callback_agents import (
    before_agent_callback,
    after_agent_callback,
)


MODEL = "gemini-2.5-flash"


# ============================================================
# 1. PRODUCT SUPPORT SPECIALIST
#    Pattern: Dynamic Schema Discovery
# ============================================================

product_support_agent = Agent(
    name="product_support_agent",
    model=MODEL,
    mode="single_turn",

    description=(
        "CME specialist for product details, contract specifications, "
        "contract size, asset class, currency and support ownership."
    ),

    instruction="""
    ROLE
    You are the CME Product Support Specialist.
    User has requested {original_request}

    DATA SOURCE
    You may access only:
    `{PROJECT_ID}.{DATASET_ID}.products`

    AVAILABLE CAPABILITIES
    - get_table_info: inspect table metadata and schema.
    - execute_sql: retrieve data using SQL.

    POLICY
    - Use available tools as needed to answer factual product questions.
    - Do not guess schema information.
    - Query only the approved table.
    - Read-only operations only.
    - Retrieve only information relevant to the request.
    - Base factual answers only on tool results.

    RESPONSE
    Return the requested product information clearly and concisely.
    If information cannot be retrieved, state that explicitly.
    Never invent information.
""",

    tools=[
        bigquery_toolset,
    ],

     # Agent callbacks
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,

    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


# ============================================================
# 2. MARKET STATUS SPECIALIST
#    Pattern: Static Schema
# ============================================================

market_status_support_agent = Agent(
    name="market_status_support_agent",
    model=MODEL,
    mode="single_turn",

    description=(
        "CME specialist for current trading status, market closures, "
        "halts, status reasons and latest market-status information."
    ),

    instruction="""
    ROLE
    You are the CME Market Status Support Specialist.
    User has requested {original_request}

    DATA SOURCE
    You may access only:
    `{PROJECT_ID}.{DATASET_ID}.market_status`

    SCHEMA
    - symbol
    - trading_status
    - status_reason
    - last_updated

    AVAILABLE CAPABILITY
    - execute_sql: retrieve data using SQL.

    POLICY
    - Use available tools as needed to answer factual market-status questions.
    - Query only the approved table.
    - Read-only operations only.
    - Retrieve only information relevant to the request.
    - For current status, use the most recent available record.
    - Base factual answers only on tool results.

    RESPONSE
    Return the requested market-status information clearly and concisely.
    If information cannot be retrieved, state that explicitly.
    Never invent information.
""",

    tools=[
        bigquery_toolset,
    ],

    # Agent callbacks
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,

    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


# ============================================================
# 3. CME SUPPORT SUPERVISOR
#    Pattern: Collaborative Supervisor
# ============================================================

supervisor_agent = Agent(
    name="cme_support_supervisor",
    model=MODEL,

    description=(
        "Supervisor coordinating CME product and "
        "market-status support specialists."
    ),

    instruction="""
    ROLE
    You are the CME Support Supervisor.

    Your responsibility is to understand the user's request,
    delegate to the appropriate specialist(s),
    and synthesize their findings.

    SPECIALISTS

    product_support_agent
    Use for:
    - product information
    - contract specifications
    - contract size
    - asset class
    - currency
    - product metadata

    market_status_support_agent
    Use for:
    - current trading status
    - market closures
    - halts
    - status reasons
    - latest market-status information

    DELEGATION
    - Delegate factual investigation to the relevant specialist(s).
    - Use only specialists required by the request.
    - For requests spanning multiple domains, gather findings from all
    relevant specialists before responding.
    - Do not perform specialist tool work yourself.
    - Do not answer retrievable factual questions from your own knowledge.


    SYNTHESIS
    Combine specialist findings into one concise and coherent response.

    Do not invent unsupported facts.
    Clearly identify missing or conflicting information.
""",

    sub_agents=[
        product_support_agent,
        market_status_support_agent,
    ],
)

def save_original_request(ctx: Context, node_input: str) -> str:

    ctx.state["original_request"] = node_input
    ctx.state["PROJECT_ID"]=PROJECT_ID
    ctx.state["DATASET_ID"]=DATASET_ID
     # Simulate authenticated user
    ctx.state["user_id"] = "guest"
    return node_input

root_agent = Workflow(
    name="part3_4_support_routing",
    edges=[

        # Preserve the original request first and delegate to supervisor agent
        (
            "START",
            save_original_request,
            supervisor_agent

        ),
    ],
)
