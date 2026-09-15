import asyncio

from google.adk import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai import types
from .agent import root_agent
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------
# VERTEX AI SESSION SERVICE
# ------------------------------------------------------------

AGENT_ENGINE_ID = 2417269166839955456
LOCATION = "us-central1"
PROJECT_ID="instructor-02"


session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

async def main():

    session = await session_service.create_session(
    app_name="demo",
    user_id="alice",
    )

    print("Created Session:", session.id)
    

    runner = Runner(
        agent=root_agent,
        app_name="demo",
        session_service=session_service,
         memory_service=memory_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="What is market status of NQ?"
            )
        ],
    )

    async for event in runner.run_async(
        user_id="alice",
        session_id=session.id,
        new_message=message,
    ):

        if event.is_final_response():
            if event.content and event.content.parts:
                print(
                    event.content.parts[0].text
                )


asyncio.run(main())