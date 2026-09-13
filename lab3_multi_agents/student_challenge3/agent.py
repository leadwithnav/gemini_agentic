"""
Student Challenge: Collaborative Multi-Agent Exchange Assistant

Use Case:
CME Exchange Information Assistant

Goal:
Understand how a supervisor agent collaborates with specialist agents.

Example Request:
"Tell me about NYMEX and also list the products available on it."

Collaboration:

                    Supervisor
                   /          \
                  /            \
      Exchange Info Agent    Product List Agent
                  \            /
                   \          /
                    Supervisor
                        |
                        v
                 Final Response


Student Task:
Complete the collaborative agent configuration by registering specialist sub-agents.
"""

from google.adk import Agent

try:
    from tools import (
        get_exchange_details,
        list_products_by_exchange,
    )
except ImportError:
    from lab3_multi_agents.student_challenge3.tools import (
        get_exchange_details,
        list_products_by_exchange,
    )


MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# PEER 1: EXCHANGE INFORMATION SPECIALIST
# ============================================================

exchange_info_agent = Agent(
    name="exchange_info_agent",
    model=MODEL_NAME,

    description=(
        "Provides general information about CME Group exchanges "
        "including exchange name, location, and description."
    ),

    instruction="""
You are the CME Exchange Information Specialist.
You are one member of a collaborative exchange-support team.
Your responsibility is ONLY general exchange information.

When asked about an exchange:
1. Identify the exchange code: CME, CBOT, NYMEX, or COMEX.
2. Call `get_exchange_details`.
3. Return:
EXCHANGE FINDINGS:
- Exchange Code
- Exchange Name
- Location
- Description

Do not list products. Do not answer questions outside exchange information.
""",

    tools=[
        get_exchange_details,
    ],
)


# ============================================================
# PEER 2: PRODUCT LIST SPECIALIST
# ============================================================

product_list_agent = Agent(
    name="product_list_agent",
    model=MODEL_NAME,

    description=(
        "Finds the product symbols associated with a CME Group exchange."
    ),

    instruction="""
You are the CME Exchange Product Specialist.
You are one member of a collaborative exchange-support team.
Your responsibility is ONLY identifying products associated with an exchange.

When asked about exchange products:
1. Identify the exchange code: CME, CBOT, NYMEX, or COMEX.
2. Call `list_products_by_exchange`.
3. Return:
PRODUCT FINDINGS:
- Exchange
- Product Symbols

Do not provide general exchange details. Do not invent products.
""",

    tools=[
        list_products_by_exchange,
    ],
)


# ============================================================
# ROOT SUPERVISOR (STUDENT TASK: REGISTER SUB_AGENTS)
# ============================================================

root_agent = Agent(
    name="collaborative_exchange_assistant",
    model=MODEL_NAME,

    instruction="""
You are the CME Exchange Support Supervisor.

Your job is to understand the user's request and collaborate with the appropriate specialist agents.

Available specialists:
1. exchange_info_agent: Use when the user needs exchange name, location, description, or general info.
2. product_list_agent: Use when the user needs products or symbols belonging to an exchange.

COLLABORATION RULES:
- Delegate exchange-information work to `exchange_info_agent`.
- Delegate product-list work to `product_list_agent`.
- If the request requires BOTH types of information, collaborate with BOTH specialists.
- Do not perform specialist work yourself.
- Do not invent information.
- After receiving specialist findings, return one concise consolidated response.
""",

    # TODO: Complete the agent collaboration configuration by registering the specialist agents
    sub_agents=[
        # TODO 1: Add the exchange information specialist (exchange_info_agent)
        # exchange_info_agent,

        # TODO 2: Add the product list specialist (product_list_agent)
        # product_list_agent,
    ],
)