"""
Lab 7 Part 3
Vertex AI Session Service + Memory Bank

Demonstrates:

1. Explicit context
       "What is the contract size of NQ?"
       → EXPLICIT

2. Same-session context
       "Is it currently trading?"
       → SESSION

3. Memory update
       "Remember that NQ is my primary product."
       → MEMORY_UPDATE

4. Cross-session long-term memory
       NEW SESSION
       "Is my preferred product currently trading?"
       → MEMORY

Memory persistence strategy:
After every completed user turn, checkpoint the recent
conversation events into Vertex AI Memory Bank.
"""

import asyncio
import logging
import os
import uuid
import warnings

from google.adk import Runner
from google.adk.sessions import VertexAiSessionService
from google.adk.memory.vertex_ai_memory_bank_service import (
    VertexAiMemoryBankService,
)
from google.genai import types

from .agent import root_agent


# ============================================================
# CLEAN DEMO OUTPUT
# ============================================================

# Hide ADK experimental feature warnings.
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=r".*\[EXPERIMENTAL\].*",
)

# This warning currently originates from ADK internals.
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=r".*vertexai\.Client class is deprecated.*",
)

# Keep framework logs at WARNING or above.
logging.basicConfig(level=logging.WARNING)

for logger_name in [
    "google",
    "google_adk",
    "google.adk",
    "google_genai",
    "google.genai",
]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# AFC warning is framework noise for this lab.
logging.getLogger(
    "google_genai.models"
).setLevel(logging.ERROR)

# Keep our own observability logger visible.
logging.getLogger(
    "cme_agent"
).setLevel(logging.INFO)


# ============================================================
# CONFIG
# ============================================================

PROJECT_ID = "instructor-02"
LOCATION = "us-central1"
AGENT_ENGINE_ID = "5344450594956378112"

APP_NAME = "cme-support-desk"
USER_ID = "alice"


# Unique sessions for every demo run
RUN_ID = uuid.uuid4().hex[:8]

SESSION_1 = f"alice-session-1-{RUN_ID}"
SESSION_2 = f"alice-session-2-{RUN_ID}"


# ============================================================
# SERVICES
# ============================================================

session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID,
)

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)


# ============================================================
# CREATE SESSION
# ============================================================

async def create_session(session_id: str):

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state={
            "user_id": USER_ID,
            "user_authorized": True,
            "current_symbol": "",
            "previous_symbol": "",
            "current_request": "",
            "previous_request": "",
            "route": "",
            "symbol_resolution_source": "",
        },
        ttl="604800s",
    )

    print(f"\n[SESSION CREATED] {session_id}")


# ============================================================
# SAVE TURN TO MEMORY BANK
# ============================================================

async def save_to_memory(session_id: str):

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    if not session or not session.events:
        return

    # Lab simplification:
    # checkpoint recent events from the completed turn.
    recent_events = session.events[-2:]

    await memory_service.add_events_to_memory(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        events=recent_events,
    )

    print("[MEMORY] Memory generation triggered.")


# ============================================================
# SEND MESSAGE
# ============================================================

async def ask(
    session_id: str,
    message: str,
):

    print("\n" + "=" * 70)
    print(f"USER : {message}")
    print("=" * 70)

    user_message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=message
            )
        ],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message,
    ):

        if event.is_final_response():

            if event.content and event.content.parts:

                response = "".join(
                    part.text or ""
                    for part in event.content.parts
                )

                print(f"\nAGENT: {response}")


    # Persist completed turn into Memory Bank
    await save_to_memory(session_id)


# ============================================================
# DEMO
# ============================================================

async def main():

    # ========================================================
    # SESSION 1
    # ========================================================

    print("\n### SESSION 1 ###")

    await create_session(
        SESSION_1
    )


    # Explicit context
    await ask(
        SESSION_1,
        "What is the contract size of NQ?",
    )


    # Same-session context
    await ask(
        SESSION_1,
        "Is it currently trading?",
    )


    # Memory update
    await ask(
        SESSION_1,
        (
            "For future conversations, remember that "
            "NQ is the CME product I work with most often "
            "and I consider NQ my primary product."
        ),
    )


    # ========================================================
    # SESSION 2
    # ========================================================

    print("\n### SESSION 2 - NEW SESSION ###")

    await create_session(
        SESSION_2
    )


    # Should resolve NQ from long-term memory
    await ask(
        SESSION_2,
        "Is my preferred product currently trading?",
    )


    # Explicit symbol should override memory
    await ask(
        SESSION_2,
        "What is the contract size of ES?",
    )


    # Should resolve ES from current session
    await ask(
        SESSION_2,
        "Is it currently trading?",
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())