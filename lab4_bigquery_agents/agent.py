"""
Lab 4 Part 1: BigQuery Multi-Agent Router (ADK V2)

Use Case:
Route a CME support request to the correct specialist agent.
Each specialist uses Google ADK's built-in BigQueryToolset
to query simulated CME support data.

Flow:

User Request
     ↓
Save Original Request + Project ID in State
     ↓
Request Classifier
     ↓
Router
     ↓
 ┌──────────────────┬──────────────────────┬──────────────────┐
 ↓                  ↓                      ↓
INCIDENT_SUPPORT   MARKET_STATUS_SUPPORT  PRODUCT_SUPPORT
 ↓                  ↓                      ↓
BigQuery           BigQuery               BigQuery
incidents          market_status          products
"""

from google.adk import Agent, Workflow, Event, Context
from .bigquery_tools import MODEL, PROJECT_ID, DATASET_ID, bigquery_toolset


# ============================================================
# 1. SAVE ORIGINAL REQUEST + INFRASTRUCTURE CONTEXT
# ============================================================

def save_original_request(
    ctx: Context,
    node_input: str,
) -> str:
    """
    Preserve the original user request and deterministic
    infrastructure configuration in workflow state.
    """

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

INCIDENT_SUPPORT
Use when the request is about:
- existing incidents
- reported issues
- support tickets
- incident status
- problems affecting a product

MARKET_STATUS_SUPPORT
Use when the request is about:
- current trading status
- whether a product is trading
- halted markets
- closed markets

PRODUCT_SUPPORT
Use when the request is about:
- product information
- contract specifications
- contract size
- asset class
- general futures product details

Return ONLY one of:

INCIDENT_SUPPORT
MARKET_STATUS_SUPPORT
PRODUCT_SUPPORT
""",

    output_schema=str,
)


# ============================================================
# 3. ROUTER
# ============================================================

def route_request(node_input: str) -> Event:
    """
    Convert classifier output into a workflow route.
    """

    category = node_input.strip().upper()

    allowed_routes = {
        "INCIDENT_SUPPORT",
        "MARKET_STATUS_SUPPORT",
        "PRODUCT_SUPPORT",
    }

    if category not in allowed_routes:
        raise ValueError(
            f"Unexpected classifier output: {category}"
        )

    return Event(route=[category])


# ============================================================
# 4A. INCIDENT SUPPORT AGENT
# ============================================================

incident_support_agent = Agent(
    name="incident_support_agent",
    model=MODEL,

    instruction="""
You are the CME Incident Support specialist.

ORIGINAL USER REQUEST:

{original_request}

Google Cloud Project:
{project_id}

BigQuery Dataset:
{dataset_id}

Use the BigQuery tools to answer the request.

You may query ONLY this table:

`{project_id}.{dataset_id}.incidents`

IMPORTANT:

- Always use the fully qualified table name.
- Never guess or invent a project ID.
- Never query another project.
- Never query another dataset.
- Use SELECT queries only.
- Never INSERT, UPDATE, DELETE, MERGE, CREATE, DROP or ALTER data.

Steps:

1. Read the original user request.

2. Identify either:
   - product symbol such as NQ, ES, CL or GC
   OR
   - incident ID such as INC-101.

3. Query:

`{project_id}.{dataset_id}.incidents`

4. Retrieve only relevant fields such as:

- incident_id
- symbol
- issue
- status
- assigned_team
- root_cause_notes
- created_at

5. For product-based searches, order recent incidents first.

6. Use LIMIT 10 unless more rows are genuinely required.

7. Summarize the BigQuery result.

Return:

- Product Symbol
- Incident ID
- Issue
- Status
- Assigned Team
- Root Cause Notes

If no matching incident exists, clearly state that no
matching incident was found.

Do not invent information that was not returned by BigQuery.
""",

    tools=[
        bigquery_toolset,
    ],
)


# ============================================================
# 4B. MARKET STATUS SUPPORT AGENT
# ============================================================

market_status_support_agent = Agent(
    name="market_status_support_agent",
    model=MODEL,

    instruction="""
You are the CME Market Status Support specialist.

ORIGINAL USER REQUEST:

{original_request}

Google Cloud Project:
{project_id}

BigQuery Dataset:
{dataset_id}

Use the BigQuery tools to answer the request.

You may query ONLY:

`{project_id}.{dataset_id}.market_status`

IMPORTANT:

- Always use the fully qualified table name.
- Never guess or invent the project ID.
- Never query another project.
- Never query another dataset.
- Use SELECT queries only.
- Never INSERT, UPDATE, DELETE, MERGE, CREATE, DROP or ALTER data.

Steps:

1. Extract the product symbol from the original request.

2. Query:

`{project_id}.{dataset_id}.market_status`

3. Retrieve:

- symbol
- trading_status
- status_reason
- last_updated

4. Retrieve the latest status using:

ORDER BY last_updated DESC
LIMIT 1

5. Report the result clearly.

Return:

- Product Symbol
- Trading Status
- Status Reason
- Last Updated

Trading status may include:

TRADING
HALTED
CLOSED

Do not invent information that was not returned by BigQuery.
""",

    tools=[
        bigquery_toolset,
    ],
)


# ============================================================
# 4C. PRODUCT SUPPORT AGENT
# ============================================================

product_support_agent = Agent(
    name="product_support_agent",
    model=MODEL,

    instruction="""
You are the CME Product Support specialist.

ORIGINAL USER REQUEST:

{original_request}

Google Cloud Project:
{project_id}

BigQuery Dataset:
{dataset_id}

Use the BigQuery tools to answer the request.

You may query ONLY:

`{project_id}.{dataset_id}.products`

IMPORTANT:

- Always use the fully qualified table name.
- Never guess or invent the project ID.
- Never query another project.
- Never query another dataset.
- Use SELECT queries only.
- Never INSERT, UPDATE, DELETE, MERGE, CREATE, DROP or ALTER data.

Steps:

1. Extract the product symbol from the original request.

2. Query:

`{project_id}.{dataset_id}.products`

3. Retrieve only the columns required to answer the question.

Available information includes:

- symbol
- product_name
- asset_class
- contract_size
- currency
- primary_support_team

4. Filter by the requested product symbol.

5. Use LIMIT 1 for a single product lookup.

6. Answer the user's original question based on the
BigQuery result.

Do not invent information that was not returned by BigQuery.
""",

    tools=[
        bigquery_toolset,
    ],
)


# ============================================================
# 5. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="part4_bigquery_support_routing",

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
                "INCIDENT_SUPPORT":
                    incident_support_agent,

                "MARKET_STATUS_SUPPORT":
                    market_status_support_agent,

                "PRODUCT_SUPPORT":
                    product_support_agent,
            },
        ),
    ],
)