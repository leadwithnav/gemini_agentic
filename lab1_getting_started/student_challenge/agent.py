from google.adk.agents import Agent

from .tools import (
    get_exchange_details,
    list_products_by_exchange
)


root_agent = Agent(
    name="cme_exchange_assistant",

    # TODO 1: Configure the appropriate Gemini model
    model="________________",

    description="""
    TODO: Add agent description
    """,

    instruction="""
    You are a CME Group Exchange Information Assistant.

    Help employees find information about CME Group exchanges
    and the products associated with them.

    TODO:
    Add appropriate instructions for:
    - Using available tools
    - Handling unknown exchanges
    - Avoiding invented information
    - Providing clear responses
    """,

    tools=[
        # TODO 2: Register tools
    ]
)