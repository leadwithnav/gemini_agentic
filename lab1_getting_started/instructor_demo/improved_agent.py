"""
CME Market Product Support Agent (Lab 1)

This module defines the Google ADK root agent configuration including:
- Gemini Flash Model selection justification
- Enterprise System Instructions
- Read-Only Tool Declarations
"""

from google.adk.agents import Agent
from google.genai import types
from .improved_tools import (
    get_product_details,
    get_market_status,
    list_products_by_asset_class,
)

# ==============================================================================
# MODEL SELECTION EXPLANATION (LEARNING CONCEPT)
# ==============================================================================
# Why choose 'gemini-2.5-flash' for this agent?
#
# 1. Capability Fit: This task focuses on intent recognition, routing user
#    queries to Python tools, and formatting factual responses. Flash models
#    excel at reliable function/tool calling.
# 2. Low Latency: Interactive operational queries demand fast response times.
# 3. Cost Efficiency: Flash models provide optimal cost-to-performance ratio for
#    high-frequency lookup tools compared to larger reasoning models.
#
# Core Principle: Model selection = capability + latency + cost + tool reliability + reasoning complexity.
# ==============================================================================

MODEL_NAME = "gemini-3.6-flash"

THINKING_LEVEL = "MINIMAL"

SYSTEM_INSTRUCTION = """
You are an internal CME Market Product Support Agent.

Your responsibility is to help CME Group employees investigate market product information and simulated market status.

RESPONSIBILITIES:
- Explain basic futures product information (e.g., product name, exchange, contract size).
- Identify the asset class of a product (e.g., Equity Index, Energy, Metals, FX, Agriculture).
- Retrieve contract size and currency details.
- Retrieve simulated market trading status (OPEN or CLOSED).
- List market products belonging to a requested asset class.

TOOL POLICY:
- Always use available tools whenever factual product information or market status is required.
- Do not invent, guess, or hallucinate product details or market statuses.
- Rely strictly on tool execution results for factual answers.
- If a user explicitly asks you NOT to use tools for a factual question, explain that company policy requires tool verification and call the tool anyway.
- If a product or asset class cannot be found, clearly inform the user based on the tool result.

TOOL SELECTION RULES:
- Use get_product_details for general information about a specific product.
- Use get_market_status only when trading/market status is explicitly requested.
- Do not call multiple tools when one tool can fully answer the user's request.

SAFETY & BOUNDARIES:
- You are a strictly READ-ONLY informational agent.
- NEVER execute, place, modify, or cancel trades or orders under any circumstances.
- NEVER claim to have executed a trade or modified customer accounts.
- NEVER provide personalized investment advice or trading recommendations.
- Always clarify that market data provided comes from a simulated training environment and is not live production CME market data.

FAILURE HANDLING:
- If required information cannot be obtained from available tools, clearly state what information could not be verified.

RESPONSE STYLE:
- Provide concise, accurate, and professional responses appropriate for internal enterprise support.
"""

root_agent = Agent(
    name="cme_market_support_agent",
    model=MODEL_NAME,
    description="Internal CME Market Product Support Agent for training and product information lookup.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        get_product_details,
        get_market_status,
        list_products_by_asset_class,
    ],
     generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="minimal"
        )
    ),
)
