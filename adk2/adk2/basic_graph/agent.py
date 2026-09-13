from google.adk import Agent
from google.adk import Workflow

city_visit_places_agent = Agent(
    name="city_visit_places_agent",
    model="gemini-3.5-flash",
    instruction="""When a city name is provided, return the primary places to visit. 
    Limit the answer to 10 lines only""",

)

city_best_time_visit_agent = Agent(
    name="city_best_time_visit_agent",
    model="gemini-3.5-flash",
    instruction="""For a given city suggests the best time to visit. 
    Limit the answer to 10 lines only""",
)


root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", city_visit_places_agent, city_best_time_visit_agent,)
    ],
)