from google.adk import Agent
from google.adk.tools import FunctionTool


MODEL = "gemini-2.5-flash"


# ============================================================
# 1. SENSITIVE FUNCTION
# ============================================================

def create_support_ticket(
    product_symbol: str,
    reason: str,
) -> dict:
    """
    Create a CME support ticket.

    Args:
        product_symbol: CME product symbol, for example NQ, ES, CL or GC.
        reason: Reason for creating the support ticket.
    """

    # Simulated ticket creation
    return {
        "ticket_id": "TKT-1001",
        "product_symbol": product_symbol,
        "reason": reason,
        "status": "OPEN",
    }


# ============================================================
# 2. WRAP FUNCTION AS A FUNCTION TOOL
#    REQUIRE HUMAN CONFIRMATION
# ============================================================

create_support_ticket_tool = FunctionTool(
    func=create_support_ticket,
    require_confirmation=True,
)


# ============================================================
# 3. AGENT
# ============================================================

root_agent = Agent(
    name="ticket_creation_agent",

    model=MODEL,

    description=(
        "Creates CME support tickets for product and market issues."
    ),

    instruction="""
    ROLE
    You are a CME Support Ticket Agent.

    RESPONSIBILITY
    Create support tickets when requested by the user.

    AVAILABLE TOOL
    create_support_ticket

    POLICY
    - Use create_support_ticket when the user asks to create a ticket.
    - Extract the product symbol from the user's request.
    - Provide a concise reason for the ticket.
    - Never invent a ticket ID.
    - Never claim that a ticket was created unless the tool
    successfully executes.

    IMPORTANT
    Ticket creation is a sensitive action and requires
    human confirmation before execution.
""",

    tools=[
        create_support_ticket_tool,
    ],
)