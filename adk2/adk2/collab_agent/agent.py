from google.adk.agents import LlmAgent

weather_agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.5-flash",
    mode="single_turn",
    instruction="""suggest random weather update for a given city. Just make the weather. 
                    No need to say that you cannot get realtime weather""",
    description="An agent which can provide weather updates for a given city",
    )

flight_agent = LlmAgent(
    name="flight_agent",
    model="gemini-2.5-flash",
    mode="task",
    instruction="""Suggest a random flight details between 2 cities. 
                    If city names are not provided, ask for that
                    
                    Crucial: Once you have both cities, provide the flight details 
                    directly to the user. Do not call or transfer back to 'travel_agent'
                    """,
    description="An agent who helps with flight information",
)

root_agent = LlmAgent(
    name="travel_agent",
    model="gemini-2.5-flash",
    instruction="""You are a coordinator who helps with weather and flight information.

         Routing Rules:
         - Call 'weather_agent' if the user asks about the weather.
         - Call 'flight_agent' if the user asks about flights.

         Do not attempt to answer these queries yourself; always delegate to the respective sub-agent.""",
    sub_agents=[flight_agent, weather_agent],
)
