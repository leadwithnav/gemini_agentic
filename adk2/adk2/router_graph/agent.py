from google.adk import Agent
from google.adk import Workflow
from google.adk import Event

process_message = Agent(
    name="process_message",
    model="gemini-2.5-flash",
    instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
      or "LOGISTICS". If you think a message applies to more than one category,
      reply with a comma separated list of categories.
   """,
    output_schema=str,
)

def router(node_input: str):
    routes = node_input.split(",")
    routes = [route.strip() for route in routes]
    return Event(route=routes)

def response_1_bug():
    return Event(message="Handling bug...")

def response_2_support():
    return Event(message="Handling customer support...")

def response_3_logistics():
    return Event(message="Handling logistics...")

customer_support_agent = Agent(
    name="customer_support_agent",
    model="gemini-2.5-flash",
    instruction="""Return a 5 line basic customer support help based on technical issues on Laptop and Mobile.
   """,
    output_schema=str,
)

root_agent = Workflow(
   name="routing_workflow",
   edges=[
       ("START", process_message, router),
       ( router,
           {
               "BUG": response_1_bug,
               "CUSTOMER_SUPPORT": customer_support_agent,
               "LOGISTICS": response_3_logistics,
           }
       )
   ],
)