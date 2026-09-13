import asyncio

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent
import asyncio
import logging
import warnings

# Hide Python warnings
warnings.filterwarnings("ignore")

# Hide noisy framework INFO logs
logging.getLogger("google_adk").setLevel(logging.ERROR)
logging.getLogger("google.adk").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.auth").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)

logging.getLogger("cme_agent").setLevel(logging.INFO)


APP_NAME = "cme_support_desk"
USER_ID = "alice"
SESSION_ID = "session_1001"


# ------------------------------------------------------------
# SESSION SERVICE
# ------------------------------------------------------------

session_service = InMemorySessionService()


# ------------------------------------------------------------
# RUNNER
# ------------------------------------------------------------

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# ------------------------------------------------------------
# SEND ONE MESSAGE
# ------------------------------------------------------------

async def send_message(message: str):

    print(f"\nUSER: {message}")

    new_message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=message)
        ],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):

        if event.is_final_response():

            if event.content and event.content.parts:

                response = "".join(
                    part.text or ""
                    for part in event.content.parts
                )

                print(f"AGENT: {response}")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

async def main():

    # Create session only once
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={
            "user_id": USER_ID
        },
    )

    print(f"Session created: {SESSION_ID}")

    # Message 1
    await send_message(
        "What is the contract size of NQ?"
    )

    # Message 2 - SAME SESSION
    await send_message(
        "Is it currently trading?"
    )

    # Message 3 - SAME SESSION
    await send_message(
        "Are there any incidents affecting it?"
    )

     # Message 3 - SAME SESSION
    await send_message(
            "What about ES"
    )

    # Inspect final session state
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print("\nFINAL SESSION STATE")

    safe_keys = [
        "user_id",
        "original_request",
        "project_id",
        "dataset_id",
        "request_id",
        "route",
        "last_tool",
        "last_tool_success",
        "last_tool_duration_ms",
    ]


    print("\nFINAL SESSION STATE")
    for key in safe_keys:
        print(f"{key}: {session.state.get(key)}")



if __name__ == "__main__":
    asyncio.run(main())