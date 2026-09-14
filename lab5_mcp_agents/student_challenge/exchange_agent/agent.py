"""
Lab 5 Student Challenge:
Hybrid Exchange Support Agent (MCP + BigQuery)

Goal:
Connect Google ADK to the Exchange MCP Server for Exchange Information,
while using BigQuery for Product Information.

Students only need to complete TODO 3 in this file.
"""

from google.adk import Agent, Workflow, Event, Context

from .bigquery_tools import (
    MODEL,
    PROJECT_ID,
    DATASET_ID,
    bigquery_toolset,
)

# TODO 3: Import the MCP toolset from .tools after completing TODO 1 and TODO 2 in tools.py
# from .tools import exchange_mcp_toolset


# ============================================================
# 1. SAVE ORIGINAL REQUEST CONTEXT
# ============================================================

def save_original_request(
    ctx: Context,
    node_input: str,
) -> str:
    ctx.state["original_request"] = node_input
    ctx.state["project_id"] = PROJECT_ID
    ctx.state["dataset_id"] = DATASET_ID
    return node_input


# ============================================================
# 2. REQUEST CLASSIFIER
# ============================================================

request_classifier = Agent(
    name="request_classifier",
    model=MODEL,
    instruction="""
Classify the incoming CME support request into exactly ONE category.

EXCHANGE_INFO
Use when the request is about:
- exchange names
- exchange locations
- exchange descriptions
- general exchange metadata (CME, CBOT, NYMEX, COMEX)

PRODUCT_INFO
Use when the request is about:
- products available on an exchange
- contract specifications
- list of trading products

Return ONLY one of:

EXCHANGE_INFO
PRODUCT_INFO
""",
    output_schema=str,
)


# ============================================================
# 3. ROUTER
# ============================================================

def route_request(node_input: str) -> Event:
    category = node_input.strip().upper()

    allowed_routes = {
        "EXCHANGE_INFO",
        "PRODUCT_INFO",
    }

    if category not in allowed_routes:
        raise ValueError(f"Unexpected classifier output: {category}")

    return Event(
        name=category,
        body={"category": category},
    )


# ============================================================
# 4. EXCHANGE INFORMATION AGENT (MCP INTEGRATION)
# ============================================================

# TODO 3:
# Register the MCP Toolset with the Exchange Information Agent.
# Pass the toolset created in tools.py inside the tools list.

exchange_info_agent = Agent(
    name="exchange_info_agent",
    model=MODEL,
    instruction="""
You are an expert on CME Group exchanges (CME, CBOT, NYMEX, COMEX).
Answer questions about exchange names, locations, descriptions, and metadata.
Use exchange tools to query exchange details.
""",
    tools=[
        # TODO 3: Register exchange_mcp_toolset here
    ],
)


# ============================================================
# 5. PRODUCT INFORMATION AGENT (BIGQUERY INTEGRATION)
# ============================================================

# BigQuery path is fully configured and completed. Do NOT modify!
product_info_agent = Agent(
    name="product_info_agent",
    model=MODEL,
    instruction=f"""
You are a CME product support specialist.
Answer user questions using BigQuery tools against table `{DATASET_ID}.exchange_products`.
""",
    tools=[bigquery_toolset],
)


# ============================================================
# 6. ROOT WORKFLOW
# ============================================================

root_agent = (
    Workflow(name="cme_hybrid_support_workflow")
    .set_start(save_original_request)
    .then(request_classifier)
    .then(route_request)
)

root_agent.branch(
    on="EXCHANGE_INFO",
    target=exchange_info_agent,
)

root_agent.branch(
    on="PRODUCT_INFO",
    target=product_info_agent,
)
