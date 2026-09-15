"""
Lab 6 Student Challenge: Collaborative Agents with Custom Tools

Security Governance & Observability with ADK Callbacks

Architecture

                    User
                      │
                      ▼
          CME Exchange Support Supervisor
              /                  \
             /                    \
            ▼                      ▼
 Exchange Info Agent        Product Info Agent
        │                         │
        ▼                         ▼
get_exchange_details     list_products_by_exchange


Concepts:
- Supervisor delegates work to specialist agents.
- Specialist agents use custom Python tools.
- Before-tool callback applies security checks.
- After-tool callback captures observability information.
"""

from google.adk import Agent, Workflow, Context

from .tools.custom_tools import (
    get_exchange_details,
    list_products_by_exchange,
)


MODEL = "gemini-2.5-flash"


# ============================================================
# SAVE ORIGINAL REQUEST
# ============================================================

def save_original_request(ctx: Context, node_input: str) -> str:

    # Preserve original user request
    ctx.state["original_request"] = node_input

    # Simulate authenticated user for local demo
    ctx.state["user_id"] = "alice"

    return node_input


# ============================================================
# 1. EXCHANGE INFORMATION SPECIALIST
# ============================================================

exchange_info_agent = Agent(
    name="exchange_info_agent",
    model=MODEL,
    mode="single_turn",

    description=(
        "Specialist for exchange details such as exchange name, "
        "location and description."
    ),

    instruction="""
    ROLE
    You are the CME Exchange Information Specialist.

    ORIGINAL USER REQUEST
    {original_request}

    AVAILABLE TOOL
    get_exchange_details

    Use this tool to retrieve factual information about an exchange.

    SUPPORTED EXCHANGES
    - CME
    - CBOT
    - NYMEX
    - COMEX

    TOOL POLICY
    - Use get_exchange_details when exchange information is required.
    - Pass the exchange code requested by the user.
    - Base factual answers only on tool results.
    - Never invent exchange information.

    RESPONSE
    Return relevant information such as:
    - Exchange Code
    - Exchange Name
    - Location
    - Description

    If the exchange cannot be found, clearly state that.
""",

    tools=[
        get_exchange_details,
    ],
)


# ============================================================
# 2. PRODUCT INFORMATION SPECIALIST
# ============================================================

product_info_agent = Agent(
    name="product_info_agent",
    model=MODEL,
    mode="single_turn",

    description=(
        "Specialist for products belonging to CME exchanges, "
        "including product symbols, names and asset classes."
    ),

    instruction="""
    ROLE
    You are the CME Exchange Product Specialist.

    ORIGINAL USER REQUEST
    {original_request}

    AVAILABLE TOOL
    list_products_by_exchange

    Use this tool to retrieve products belonging to an exchange.

    SUPPORTED EXCHANGES
    - CME
    - CBOT
    - NYMEX
    - COMEX

    TOOL POLICY
    - Use list_products_by_exchange when product information is required.
    - Pass the exchange code requested by the user.
    - Base factual answers only on tool results.
    - Never invent product information.

    RESPONSE
    Return relevant information such as:
    - Exchange Code
    - Product Symbol
    - Product Name
    - Asset Class

    If no matching products are found, clearly state that.
""",

    tools=[
        list_products_by_exchange,
    ],
)


# ============================================================
# 3. COLLABORATIVE SUPERVISOR
# ============================================================

supervisor_agent = Agent(
    name="exchange_support_supervisor",
    model=MODEL,

    description=(
        "Supervisor coordinating CME exchange and "
        "product information specialists."
    ),

    instruction="""
    ROLE
    You are the CME Exchange Support Supervisor.

    Your responsibility is to understand the user's request,
    delegate work to the appropriate specialist agent,
    and combine the results into a final response.


    SPECIALISTS

    exchange_info_agent

    Use for questions about:
    - Exchange name
    - Exchange location
    - Exchange description
    - General exchange information


    product_info_agent

    Use for questions about:
    - Products belonging to an exchange
    - Product symbols
    - Product names
    - Product asset classes


    DELEGATION
    - Delegate factual investigation to the appropriate specialist.
    - Use only the specialist needed for the request.
    - If the request requires both exchange information and product
    information, use both specialists.
    - Preserve the user's intent when delegating.
    - Do not perform specialist tool work yourself.


    SYNTHESIS
    Combine specialist findings into one clear response.
    Base factual information only on specialist results.
    Never invent unsupported information.
""",

    sub_agents=[
        exchange_info_agent,
        product_info_agent,
    ],
)


# ============================================================
# ROOT
# ============================================================

root_agent = Workflow(
    name="cme_exchange_support",

    edges=[
        (
            "START",
            save_original_request,
            supervisor_agent,
        ),
    ],
)