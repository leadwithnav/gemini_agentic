"""
Student Challenge 2: Dynamic Adaptive Exchange Assistant (ADK V2)

Goal:
Complete ONLY the dynamic workflow orchestration in dynamic_exchange_workflow().

Flow:
User Request -> Planner -> Determine Capabilities -> Run Required Specialists (Exchange Info / Product List) -> Aggregate Results -> Final Response
"""

from google.adk import Agent, Workflow, Context
from google.adk.workflow import node

try:
    from tools import get_exchange_details, list_products_by_exchange
except ImportError:
    from lab3_multi_agents.student_challenge2.tools import (
        get_exchange_details,
        list_products_by_exchange,
    )


# ============================================================
# 1. PLANNER AGENT (PRE-WRITTEN)
# ============================================================

exchange_planner = Agent(
    name="exchange_planner",
    model="gemini-2.5-flash",
    instruction="""
You are the CME Exchange Planner.

Analyze the user's request and decide which capabilities are required:

EXCHANGE_INFO
Use when the user asks for details about an exchange (name, location, description).

PRODUCT_LIST
Use when the user asks which products or symbols belong to an exchange.

You may select MORE THAN ONE capability if both are needed.

Return a comma-separated list only.

Examples:
EXCHANGE_INFO
PRODUCT_LIST
EXCHANGE_INFO,PRODUCT_LIST
""",
)


# ============================================================
# 2. EXCHANGE INFO SPECIALIST (PRE-WRITTEN)
# ============================================================

exchange_info_specialist = Agent(
    name="exchange_info_specialist",
    model="gemini-2.5-flash",
    instruction="""
You are the CME Exchange Info Specialist.
Use `get_exchange_details` to look up information for the requested exchange.
""",
    tools=[get_exchange_details],
)


# ============================================================
# 3. PRODUCT LIST SPECIALIST (PRE-WRITTEN)
# ============================================================

product_list_specialist = Agent(
    name="product_list_specialist",
    model="gemini-2.5-flash",
    instruction="""
You are the CME Product Catalog Specialist.
Use `list_products_by_exchange` to list products associated with the requested exchange.
""",
    tools=[list_products_by_exchange],
)


# ============================================================
# 4. RESPONSE AGGREGATOR (PRE-WRITTEN)
# ============================================================

response_aggregator = Agent(
    name="response_aggregator",
    model="gemini-2.5-flash",
    instruction="""
You are the CME Exchange Response Coordinator.
Combine the findings from the specialists and provide a clear, professional final response.
Do not invent data. Do not call tools.
""",
)


# ============================================================
# 5. DYNAMIC WORKFLOW (STUDENT CHALLENGE: COMPLETE THIS NODE)
# ============================================================

@node(rerun_on_resume=True)
async def dynamic_exchange_workflow(
    ctx: Context,
    node_input: str
) -> str:
    original_request = node_input
    results = []

    # --------------------------------------------------------
    # STEP 1: Run the planner to get required capabilities
    # --------------------------------------------------------
    # TODO: Invoke exchange_planner using ctx.run_node(...)
    # plan_raw = await ctx.run_node(...)
    # plan = str(plan_raw).upper()

    plan = ""  # TODO: Replace with plan output from exchange_planner


    # --------------------------------------------------------
    # STEP 2: Dynamically run EXCHANGE_INFO specialist if in plan
    # --------------------------------------------------------
    # TODO: Check if "EXCHANGE_INFO" in plan
    # If true, run exchange_info_specialist via ctx.run_node(...) and append result to results list
    pass


    # --------------------------------------------------------
    # STEP 3: Dynamically run PRODUCT_LIST specialist if in plan
    # --------------------------------------------------------
    # TODO: Check if "PRODUCT_LIST" in plan
    # If true, run product_list_specialist via ctx.run_node(...) and append result to results list
    pass


    # --------------------------------------------------------
    # STEP 4: Aggregate findings and return final response
    # --------------------------------------------------------
    # TODO: Combine results into a formatted string and run response_aggregator node
    # combined_results = "\n\n".join(results)
    # final_response = await ctx.run_node(response_aggregator, node_input=...)
    # return final_response

    return "TODO: Complete dynamic_exchange_workflow"


# ============================================================
# 6. ROOT WORKFLOW
# ============================================================

root_agent = Workflow(
    name="student_challenge2",
    edges=[
        (
            "START",
            dynamic_exchange_workflow
        )
    ],
)
