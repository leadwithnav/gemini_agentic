"""
Part 3.1: Sequential Graph Agents (ADK V2)
Use case: Investigate a Product Support Ticket
Flow: Get Ticket -> Get Product Details -> Check Related Incident -> Generate Support Summary
Reference: adk2/basic_graph
"""
from google.adk import Agent
from google.adk import Workflow

try:
    from tools import get_ticket_details, get_product_details, list_incidents_by_product
except ImportError:
    from lab3_multi_agents.tools import get_ticket_details, get_product_details, list_incidents_by_product

# Stage 1: Get Ticket Agent
get_ticket_agent = Agent(
    name="get_ticket_agent",
    model="gemini-3.8-flash",
    instruction="""You are the CME Ticket Inspection Agent.
When provided with a ticket request (e.g., INC-101, INC-102, or INC-103):
1. Call `get_ticket_details` to fetch ticket title, symbol, status, priority, and description.
2. Present a clear initial summary of the support ticket.""",
    tools=[get_ticket_details],
)

# Stage 2: Get Product Details Agent
get_product_agent = Agent(
    name="get_product_agent",
    model="gemini-3.8-flash",
    instruction="""You are the CME Product Data Agent.
Based on the ticket details from Stage 1:
1. Call `get_product_details` for the ticket's product symbol (ES, NQ, CL, GC).
2. Retrieve product name, asset class, exchange, and primary support team.
3. Present how the product specs relate to the ticket.""",
    tools=[get_product_details],
)

# Stage 3: Check Related Incident Agent
check_related_incidents_agent = Agent(
    name="check_related_incidents_agent",
    model="gemini-3.8-flash",
    instruction="""You are the CME Incident History Auditor.
Based on the product symbol:
1. Call `list_incidents_by_product` to check all related incident tickets for this product.
2. Identify if there is a pattern or multiple open tickets on the same symbol.""",
    tools=[list_incidents_by_product],
)

# Stage 4: Generate Support Summary Agent
generate_support_summary_agent = Agent(
    name="generate_support_summary_agent",
    model="gemini-3.8-flash",
    instruction="""You are the CME Support Lead Reporter.
Synthesize all collected information into an Executive Support Investigation Report:
- Ticket ID, Product Symbol & Name
- Current Ticket Status & Priority
- Related Incidents Pattern Summary
- Actionable Next Steps & Recommended Assigned Team
Format cleanly with markdown headers.""",
)

# Root Sequential Graph Workflow
root_agent = Workflow(
    name="part3_1_sequential_agent",
    edges=[
        ("START", get_ticket_agent, get_product_agent, check_related_incidents_agent, generate_support_summary_agent)
    ],
)
