from google.adk import Agent
from google.adk import Workflow
from google.adk import Event
from google.adk.events import RequestInput

city_list_agent = Agent(
    name="city_list_agent",
    model="gemini-2.5-flash",
    instruction="""List top 10 Nice to visit cities in the world. Just list the names. 
                    Do not provide any further details""",
)

def choose_city(): # Human input step
    yield RequestInput(message="Enter your city selection:")

def welcome_city(node_input):
    return Event(
        message=f"{node_input}\nis a nice place.",
    )

city_detail_agent = Agent(
    name="city_detail_agent",
    model="gemini-2.5-flash",
    instruction="""When a city name provided, list down the places to visit in the city. 
                    Limit the output to 10 lines""",
)

root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", city_list_agent, choose_city, city_detail_agent)
    ],
)