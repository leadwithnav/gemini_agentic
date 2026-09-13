from google.adk import Agent
from google.adk import Workflow
from google.adk import Event

city_name_agent = Agent(
    name="city_name_agent",
    model="gemini-3.5-flash",
    instruction="""Suggest a random famous city name. Just the name, nothing else""",
)

def welcome_city(node_input: str):
    output_value = f"Welcome to {node_input}"
    return Event(output=output_value)

def message_city(node_input):
    return Event(
        message=f"Hello, {node_input}. It is a nice place to visit\n",
    )

root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", city_name_agent, welcome_city, message_city)
    ],
)