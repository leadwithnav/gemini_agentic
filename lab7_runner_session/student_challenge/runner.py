import asyncio

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

from dotenv import load_dotenv
load_dotenv()

async def main():

    #TODO: Create Inmemory Session Service

    #TODO: Create a new session

    #TODO: Create a Runner

    #TODO: Create a message

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