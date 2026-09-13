import asyncio
import logging
import os
import sys
from pathlib import Path
import warnings

from google.adk import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai import types
from .agent import root_agent


# Hide Python warnings
warnings.filterwarnings("ignore")

# Hide noisy framework INFO logs
logging.getLogger("google_adk").setLevel(logging.ERROR)
logging.getLogger("google.adk").setLevel(logging.ERROR)
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google.auth").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)

logging.getLogger("cme_agent").setLevel(logging.INFO)

# ------------------------------------------------------------
# CONFIGURATION FOR VERTEX AI SESSION SERVICE
# ------------------------------------------------------------



# Reasoning Engine / Agent Engine Resource ID for Vertex AI Session Service
AGENT_ENGINE_ID = 5344450594956378112
LOCATION = "us-central1"
PROJECT_ID="instructor-02"
APP_NAME = os.getenv("APP_NAME", "cme-support-desk")
USER_ID = "alice"
SESSION_ID = "session-1001"  # Vertex AI Session IDs require hyphens, digits, or lowercase letters


# ------------------------------------------------------------
# VERTEX AI SESSION SERVICE
# ------------------------------------------------------------

session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)


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

    try:
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
    except Exception as e:
        print(f"Vertex AI Session execution note: {e}")

async def get_or_create_session():

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    if session:
        print(f"Resuming existing Vertex AI Session: {SESSION_ID}")
        return session

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={
            "user_id": USER_ID
        },
        ttl="604800s",   # 7 days
    )

    print(f"Created Vertex AI Session: {SESSION_ID}")

    return session

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

async def main():

    print(f"Initializing Vertex AI Session Service (Project: {PROJECT_ID}, Location: {LOCATION})...")

    # Create session in Vertex AI Session Service
    session = get_or_create_session()
    
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

    # Message 4 - SAME SESSION
    await send_message(
        "What about ES"
    )

    # Inspect final session state from Vertex AI Session Service
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

        print("\nFINAL SESSION STATE")

        safe_keys = [
            "user_id",
            "current_request",
            "previous_request",
            "current_symbol",
            "previous_symbol",
            "project_id",
            "dataset_id",
            "route",
            "previous_route",
            "last_tool",
            "last_tool_success",
            "last_tool_duration_ms",
        ]

        for key in safe_keys:
            if key in session.state:
                print(f"{key}: {session.state.get(key)}")

    except Exception as e:
        print(f"\nUnable to fetch final session state: {e}")


if __name__ == "__main__":
    asyncio.run(main())