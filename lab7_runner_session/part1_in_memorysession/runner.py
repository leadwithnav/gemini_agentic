import asyncio

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

from dotenv import load_dotenv
load_dotenv()

async def main():

    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name="demo",
        user_id="alice",
        session_id="session1",
    )

    runner = Runner(
        agent=root_agent,
        app_name="demo",
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="What is the contract size of NQ?"
            )
        ],
    )

    async for event in runner.run_async(
        user_id="alice",
        session_id="session1",
        new_message=message,
    ):

        if event.is_final_response():
            if event.content and event.content.parts:
                print(
                    event.content.parts[0].text
                )


asyncio.run(main())