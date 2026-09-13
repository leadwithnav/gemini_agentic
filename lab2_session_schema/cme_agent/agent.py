"""
Lab 2: Session State + Sequential Workflow

Flow:
User
  ↓
save_request_context()
  ↓
Product Resolver
  ↓
output_key="product_symbol"
  ↓
Market Support Agent
  ↓
Tools
"""

from google.adk import Workflow, Context
from google.adk.agents import Agent, SequentialAgent

from .tools import (
    get_product_details,
    get_market_status,
)

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# 1. SAVE USER REQUEST IN SESSION STATE
# ============================================================

def save_request_context(ctx: Context, node_input: str) -> str:
    """Save the current user request in session state."""

    ctx.state["current_request"] = node_input

    return node_input


# ============================================================
# 2. RESOLVE PRODUCT
# ============================================================

product_resolver = Agent(
    name="product_resolver",
    model=MODEL_NAME,

    instruction="""
Identify the CME product symbol from the user's request.

Current request:
{current_request}

If the request does not mention a product, use the existing
product context if available.

Return ONLY the product symbol.

Examples:
"Tell me about NQ" -> NQ
"Is ES trading?" -> ES
""",

    # Agent output automatically goes into session state
    output_key="product_symbol",
)


# ============================================================
# 3. MARKET SUPPORT AGENT
# ============================================================

SYSTEM_INSTRUCTION = """
You are an internal CME Market Product Support Agent.

Your responsibility is to help CME Group employees investigate
futures product information, contract specifications, and
simulated market trading status.

CURRENT PRODUCT:
{product_symbol}

RESPONSIBILITIES:
- Explain basic futures product information.
- Identify the asset class of a product.
- Retrieve contract size, currency, and exchange metadata.
- Retrieve simulated market trading status.

TOOL POLICY:
- Always use available tools for factual product information.
- Use {product_symbol} as the resolved product.
- Do not invent product details or market status.
- Rely strictly on tool results.

SAFETY & BOUNDARIES:
- You are a READ-ONLY informational agent.
- NEVER execute, modify, or cancel trades.
- NEVER provide personalized investment advice.
- Market data is simulated training data, not live CME data.

RESPONSE STYLE:
- Be concise, accurate, and professional.
"""


market_support_agent = Agent(
    name="market_support_agent",
    model=MODEL_NAME,
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
    ],
)


# ============================================================
# 4. SEQUENTIAL WORKFLOW
# ============================================================

support_sequence = SequentialAgent(
    name="support_sequence",
    sub_agents=[
        product_resolver,
        market_support_agent,
    ],
)


# ============================================================
# 5. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="cme_market_support",
    edges=[
        (
            "START",
            save_request_context,
            support_sequence,
        )
    ],
)