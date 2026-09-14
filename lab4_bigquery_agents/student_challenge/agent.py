"""
Lab 4 Student Challenge:
BigQuery Exchange Information Assistant

Use Case:
Route CME exchange questions to the correct specialist.
Both specialists query real BigQuery tables using Google ADK's built-in BigQueryToolset.

Flow:
User Request -> Save Request + BigQuery Context -> Request Classifier -> Router -> 
  ├─> EXCHANGE_INFO -> BigQuery exchanges table
  └─> PRODUCT_LIST  -> BigQuery exchange_products table
"""

from google.adk import Agent, Workflow, Event, Context

try:
    from bigquery_tools import (
        MODEL,
        PROJECT_ID,
        DATASET_ID,
        bigquery_toolset,
    )
except ImportError:
    from lab4_bigquery_agents.student_challenge.bigquery_tools import (
        MODEL,
        PROJECT_ID,
        DATASET_ID,
        bigquery_toolset,
    )


# ============================================================
# 1. SAVE REQUEST + BIGQUERY CONTEXT
# ============================================================

def save_original_request(
    ctx: Context,
    node_input: str,
) -> str:
    """
    Save the user request and deterministic BigQuery
    configuration into shared workflow state.
    """
    ctx.state["original_request"] = node_input

    # TODO 1: Store the Google Cloud PROJECT_ID in workflow state under 'project_id'
    ctx.state["project_id"] = ""  # TODO: Set PROJECT_ID

    # TODO 2: Store the BigQuery DATASET_ID in workflow state under 'dataset_id'
    ctx.state["dataset_id"] = ""  # TODO: Set DATASET_ID

    return node_input


# ============================================================
# 2. REQUEST CLASSIFIER
# ============================================================

request_classifier = Agent(
    name="exchange_request_classifier",
    model=MODEL,
    instruction="""
    Classify the incoming CME exchange request into exactly ONE category.

    EXCHANGE_INFO
    Use when the user asks about exchange name, location, or description.
    Examples: "Tell me about NYMEX.", "Where is COMEX located?"

    PRODUCT_LIST
    Use when the user asks about products or symbols available on an exchange.
    Examples: "Which products belong to COMEX?", "List products available on NYMEX."

    Return ONLY one of: EXCHANGE_INFO or PRODUCT_LIST
    """,
    output_schema=str,
)


# ============================================================
# 3. ROUTER
# ============================================================

def route_request(node_input: str) -> Event:
    """
    Convert classifier output into an ADK workflow route.
    """
    category = node_input.strip().upper()
    allowed_routes = {"EXCHANGE_INFO", "PRODUCT_LIST"}

    if category not in allowed_routes:
        raise ValueError(f"Unexpected classifier output: {category}")

    return Event(route=[category])


# ============================================================
# 4A. EXCHANGE INFORMATION SPECIALIST
# ============================================================

exchange_info_agent = Agent(
    name="exchange_info_agent",
    model=MODEL,
    instruction="""
        You are the CME Exchange Information Specialist.
        ORIGINAL USER REQUEST: {original_request}
        Google Cloud Project: {project_id}
        BigQuery Dataset: {dataset_id}

        Use BigQuery tools to query `{project_id}.{dataset_id}.exchanges`.
        Retrieve exchange_code, exchange_name, location, and description.
        Filter by requested exchange code using SELECT queries only.
        """,
    tools=[
        # TODO 3: Register the ADK BigQuery toolset here
        # bigquery_toolset
    ],
)


# ============================================================
# 4B. PRODUCT LIST SPECIALIST
# ============================================================

product_list_agent = Agent(
    name="product_list_agent",
    model=MODEL,
    instruction="""
        You are the CME Exchange Product Specialist.
        ORIGINAL USER REQUEST: {original_request}
        Google Cloud Project: {project_id}
        BigQuery Dataset: {dataset_id}

        Use BigQuery tools to query `{project_id}.{dataset_id}.exchange_products`.
        Retrieve exchange_code, symbol, product_name, and asset_class.
        Filter by requested exchange code using SELECT queries only.
        """,
    tools=[
        # TODO 4: Register the ADK BigQuery toolset here
        # bigquery_toolset
    ],
)


# ============================================================
# 5. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="cme_bigquery_exchange_assistant",
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
                "EXCHANGE_INFO": exchange_info_agent,
                "PRODUCT_LIST": product_list_agent,
            },
        ),
    ],
)