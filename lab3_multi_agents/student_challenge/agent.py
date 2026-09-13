"""
Student Challenge: CME Exchange Support Graph Assistant (ADK V2)

Architectural Flow:
User Request -> Save Original Request in State -> Request Classifier -> Router -> 
  ├─> EXCHANGE_INFO   -> exchange_info_agent (tools: [get_exchange_details])
  ├─> PRODUCT_LIST    -> product_list_agent (tools: [list_products_by_exchange])
  └─> GENERAL_EXCHANGE-> general_exchange_agent (no tools)
"""

from google.adk import Agent, Workflow

try:
    from tools import get_exchange_details, list_products_by_exchange
except ImportError:
    from lab3_multi_agents.student_challenge.tools import (
        get_exchange_details,
        list_products_by_exchange,
    )


# ============================================================================
# TASK 1: Save Original Request into State
# ============================================================================
def save_original_request(ctx):
    """
    TODO: Extract the user request from ctx and save it into state under 'original_request'.
    
    Hint:
    - Get user input string from ctx
    - Set ctx.state["original_request"] = prompt
    """
    # TODO: Implement state saving
    pass


# ============================================================================
# TASK 2: Request Classifier Agent
# ============================================================================
# TODO: Complete the request_classifier Agent configuration
request_classifier = Agent(
    name="request_classifier",
    model="gemini-2.5-flash",
    instruction="""
    Analyze the user inquiry and classify it into EXACTLY ONE category:
    - EXCHANGE_INFO: Asking about exchange name, location, or description (e.g. CME, CBOT, NYMEX, COMEX).
    - PRODUCT_LIST: Asking for products or symbols listed on a specific exchange.
    - GENERAL_EXCHANGE: General exchange greetings, broad questions, or general help.
    
    Output ONLY the category string name.
    """,
    # TODO: Set the output key so state stores the classification result under 'classified_intent'
    output_key="???",
)


# ============================================================================
# TASK 3: Router Function
# ============================================================================
def route_request(ctx):
    """
    TODO: Retrieve 'classified_intent' from ctx.state and return the target specialist node name:
    - EXCHANGE_INFO -> "exchange_info_agent"
    - PRODUCT_LIST -> "product_list_agent"
    - GENERAL_EXCHANGE -> "general_exchange_agent"
    """
    # TODO: Implement routing logic based on ctx.state.get("classified_intent")
    pass


# ============================================================================
# TASK 4 & 5: Specialist Agents with State Injection & Tool Registration
# ============================================================================

# Exchange Information Specialist
exchange_info_agent = Agent(
    name="exchange_info_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Exchange Information Specialist.
Original Query: {original_request}

Use the `get_exchange_details` tool to look up details for the exchange requested by the user.""",
    # TODO: Register the correct tool for exchange details
    tools=[],
)

# Product List Specialist
product_list_agent = Agent(
    name="product_list_agent",
    model="gemini-2.5-flash",
    instruction="""You are the Product Catalog Specialist.
Original Query: {original_request}

Use the `list_products_by_exchange` tool to retrieve the list of products for the requested exchange.""",
    # TODO: Register the correct tool for listing products
    tools=[],
)

# General Exchange Support Specialist
general_exchange_agent = Agent(
    name="general_exchange_agent",
    model="gemini-2.5-flash",
    instruction="""You are the CME Group General Exchange Specialist.
Original Query: {original_request}

Provide a helpful, professional response to general exchange questions.""",
    tools=[],
)


# ============================================================================
# TASK 6: Workflow Graph Definition & Edges
# ============================================================================
# TODO: Connect all nodes to form the complete graph execution flow
root_agent = Workflow(
    name="student_challenge",
    edges=[
        # TODO: Add edge from START to save_original_request
        # TODO: Add edge from save_original_request to request_classifier
        # TODO: Add edge from request_classifier to route_request
        # TODO: Add edges from route_request to specialist agents (or END)
        # TODO: Add edges from specialists to END
    ],
)
