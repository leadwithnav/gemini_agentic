from google.adk import Agent
from google.adk import Workflow
from google.adk import Event
from google.adk.workflow import node
from typing import Any
from google.adk import Context


process_message = Agent(
    name="process_message",
    model="gemini-2.5-flash",
    instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
      or "LOGISTICS". Return only one of these options
   """,
    output_schema=str,
)

@node(name="response_1_bug")
def response_1_bug(node_input: Any):
    return Event(message="Handling bug...")

@node(name="response_2_support")
def response_2_support(node_input: Any):
    return Event(message="Handling customer support...")

@node(name="response_3_logistics")
def response_3_logistics(node_input: Any):
    return Event(message="Handling logistics...")

customer_support_agent = Agent(
    name="customer_support_agent",
    model="gemini-2.5-flash",
    instruction="""Return a 5 line basic customer support help based on technical issues on Laptop and Mobile.
                """,
    output_schema=str,
)


@node(rerun_on_resume=True)
async def my_workflow(ctx: Context, node_input: str) -> str:
    return_message = "We are unable to process your request at this moment. Please try again later."

    issue_type = await ctx.run_node(process_message)
    if issue_type == "BUG":
        return_message = await ctx.run_node(response_1_bug, node_input=issue_type)
    elif issue_type == "CUSTOMER_SUPPORT":
        return_message = await ctx.run_node(customer_support_agent, node_input=issue_type)
    elif issue_type == "LOGISTICS":
        return_message = await ctx.run_node(response_3_logistics, node_input=issue_type)

    return return_message

root_agent = Workflow(
    name="root_agent",
    edges=[("START", my_workflow)],
)