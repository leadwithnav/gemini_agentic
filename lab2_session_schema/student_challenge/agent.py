"""
Lab 2 Student Challenge
CME Exchange Information Assistant

Goal:
Extend the Exchange Information Assistant to use:

1. Session State
2. save_request_context()
3. output_key
4. SequentialAgent
5. State placeholder injection

Flow:

User Request
     ↓
save_request_context()
     ↓
Exchange Resolver Agent
     ↓
output_key="exchange_code"
     ↓
Session State
     ↓
Exchange Support Agent
     ↓
Tools:
- get_exchange_details()
- list_products_by_exchange()
"""

from google.adk import Workflow, Context
from google.adk.agents import Agent, SequentialAgent

from .tools import (
    get_exchange_details,
    list_products_by_exchange,
)


MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# 1. SAVE REQUEST CONTEXT
# ============================================================

def save_request_context(
    ctx: Context,
    node_input: str,
) -> str:
    """
    Save the current user request in session state.
    """

    # TODO 1:
    # Save the current user request in session state
    # using the key "current_request"

    _________________________________

    return node_input


# ============================================================
# 2. EXCHANGE RESOLVER AGENT
# ============================================================

exchange_resolver = Agent(

    name="exchange_resolver",

    model=MODEL_NAME,

    description="""
    Identifies which CME Group exchange the user
    is currently asking about.
    """,

    instruction="""
You are a CME Group exchange context resolver.

CURRENT USER REQUEST:

{current_request}


Your responsibility is to identify the exchange
being discussed.

Supported exchanges:

- CME
- CBOT
- NYMEX
- COMEX


Examples:

"Tell me about NYMEX"
→ NYMEX

"Which products belong to COMEX?"
→ COMEX

"Tell me about CBOT"
→ CBOT


TODO:
Add instructions so that:

1. If the user explicitly mentions an exchange,
   return that exchange code.

2. If the user does not mention a new exchange,
   reuse the exchange already stored in session state.

3. If the user changes the exchange,
   return the new exchange.

4. Return ONLY the exchange code.

Do not return explanations.
""",

    # TODO 2:
    # Store the resolver agent's final output in
    # session state using the key "exchange_code"

    output_key="________________",
)


# ============================================================
# 3. EXCHANGE SUPPORT AGENT
# ============================================================

SYSTEM_INSTRUCTION = """
You are an internal CME Group Exchange Information Assistant.

Your responsibility is to help employees find information
about CME Group exchanges and the products associated with them.


CURRENT REQUEST:

{current_request}


RESOLVED EXCHANGE:

{________________}


RESPONSIBILITIES:

- Explain basic exchange information.
- Retrieve exchange name and location.
- Explain the exchange description.
- List products associated with an exchange.


TOOL POLICY:

TODO:
Complete the tool policy.

Consider:

- Which tool should be used for exchange information?
- Which tool should be used for products?
- What should happen if the user asks for both?
- Should the agent invent exchange information?


CONTEXT POLICY:

TODO:
Use the resolved exchange from session state.

If the user asks a follow-up question such as:

"What products are available there?"

the agent should use the exchange already stored
in session state.


FAILURE HANDLING:

- If an exchange cannot be found, clearly state
  what was returned by the tool.

- Do not invent unsupported exchanges.


RESPONSE STYLE:

- Provide concise, clear, professional responses.
"""


exchange_support_agent = Agent(

    name="exchange_support_agent",

    model=MODEL_NAME,

    description="""
    Provides information about CME Group exchanges
    and their associated products.
    """,

    instruction=SYSTEM_INSTRUCTION,

    tools=[
        # TODO 3:
        # Register both exchange tools

        _________________________________
    ],
)


# ============================================================
# 4. SEQUENTIAL WORKFLOW
# ============================================================

exchange_sequence = SequentialAgent(

    name="exchange_support_sequence",

    sub_agents=[

        # TODO 4:
        # Run the exchange resolver first
        # and the exchange support agent second

        _________________________________
    ],
)


# ============================================================
# 5. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(

    name="cme_exchange_assistant",

    edges=[

        (
            "START",

            # TODO 5:
            # First save the request context

            _________________________________,

            # TODO 6:
            # Then execute the sequential workflow

            _________________________________,
        )
    ],
)