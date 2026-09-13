from google.adk import Agent, Workflow
from tools import get_market_status, get_product_details, list_incidents_by_product
from google.adk.workflow import JoinNode

product_specs_worker = Agent(
    name="product_specs_worker",
    model="gemini-3.8-flash",
    instruction="""
    You are the Product Specifications Worker.

        Your ONLY responsibility is to retrieve product
        specification information for the requested CME product.

        You have exactly one tool available:

        get_product_details

        When given a user request:
        1. Identify the product symbol.
        2. Call get_product_details using that symbol.
        3. Return the product specification information.
    IMPORTANT:
    - Do NOT perform the complete product health check.
    - Do NOT invent or call any other tool.
    - Use only the exact registered tool name: get_product_details.
    - The final health summary will be produced by another agent.
    """,
    tools=[get_product_details],
    output_key="product_specs_result",
)


market_status_worker = Agent(
    name="market_status_worker",
    model="gemini-3.8-flash",
    instruction="""
        You are the Market Status Worker.

        Your ONLY responsibility is to determine the market
        status of the requested CME product.

        You have exactly one tool available:

        get_market_status

        Steps:
        1. Identify the product symbol.
        2. Call get_market_status using the symbol.
        3. Return only the relevant market status information.

        IMPORTANT:
        - Do NOT perform the complete product health check.
        - Do NOT invent alternative tool names.
        - Use exactly: get_market_status.
        - The final health summary will be produced by another agent.
    """,
    tools=[get_market_status],
    output_key="market_status_result",
)


incident_check_worker = Agent(
    name="incident_check_worker",
    model="gemini-3.8-flash",
    instruction="""
    You are the Incident Check Worker.

        Your ONLY responsibility is to check whether there
        are incidents associated with the requested CME product.

        You have exactly one tool available:

        list_incidents_by_product

        Steps:
        1. Identify the product symbol.
        2. Call list_incidents_by_product using the symbol.
        3. Return the incident information.

        IMPORTANT:
        - Do NOT perform the complete health check yourself.
        - Do NOT invent any other function or tool name.
        - Use exactly: list_incidents_by_product.
        - The final health summary will be produced by another agent.
    """,
    tools=[list_incidents_by_product],
    output_key="incident_result",
)



health_summary_aggregator = Agent(
    name="health_summary_aggregator",
    model="gemini-3.6-flash",
    instruction="""
    You are the CME Product Health Summary Manager.

    Combine the following worker results.

    PRODUCT SPECIFICATIONS:
    {product_specs_result}

    MARKET STATUS:
    {market_status_result}

    INCIDENT INFORMATION:
    {incident_result}


    Produce a concise product health summary containing:

    Product:
    Market Status:
    Active Incidents:
    Overall Health:
    Recommendation:
    """,
)

# -----------------------------
# JOIN
# -----------------------------
health_checks_join = JoinNode(
    name="health_checks_join"
)


root_agent = Workflow(
    name="part3_2_parallel_agent",

    edges=[

        # Fan-out
        (
            "START",
            (
                product_specs_worker,
                market_status_worker,
                incident_check_worker,
            ),
             health_checks_join,
             health_summary_aggregator,
        ),
    ],
)