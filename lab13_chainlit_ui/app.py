import os
import uuid

import httpx
import chainlit as cl

from google.auth.transport.requests import Request
from google.oauth2.id_token import fetch_id_token


ADK_BASE_URL = os.getenv(
    "ADK_BASE_URL",
    "https://cme-support-agent-1064748107249.us-central1.run.app"
)

APP_NAME = os.getenv(
    "APP_NAME",
    "lab9_cloud_run.app.configured_agent"
)

USER_ID = "demo-user"


def get_auth_headers():
    """
    Generate Google-signed ID token for the
    private ADK Cloud Run service.
    """
    token = fetch_id_token(
        Request(),
        ADK_BASE_URL,
    )

    return {
        "Authorization": f"Bearer {token}"
    }


async def create_session(session_id: str):

    url = (
        f"{ADK_BASE_URL}/apps/{APP_NAME}"
        f"/users/{USER_ID}/sessions/{session_id}"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:

        response = await client.post(
            url,
            json={},
            headers=get_auth_headers(),
        )

        response.raise_for_status()

        return response.json()


async def run_agent(
    session_id: str,
    message: str
):

    url = f"{ADK_BASE_URL}/run"

    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [
                {
                    "text": message
                }
            ]
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:

        response = await client.post(
            url,
            json=payload,
            headers=get_auth_headers(),
        )

        response.raise_for_status()

        return response.json()


def extract_answer(events):

    if not isinstance(events, list):
        return str(events)

    for event in reversed(events):

        content = event.get("content")

        if not content:
            continue

        parts = content.get("parts", [])

        texts = [
            part["text"]
            for part in parts
            if isinstance(part, dict)
            and part.get("text")
        ]

        if texts:
            return "\n".join(texts)

    return "Agent completed the request but returned no text response."


@cl.on_chat_start
async def on_chat_start():

    session_id = str(uuid.uuid4())

    cl.user_session.set(
        "session_id",
        session_id
    )

    try:

        await create_session(session_id)

        await cl.Message(
            content="""
### CME Support Agent

Connected to the ADK agent deployed on Cloud Run.

Try asking:

- Show incidents for NQ
- Is NQ currently trading?
- What is the contract size of ES?
"""
        ).send()

    except Exception as e:

        await cl.Message(
            content=(
                "Failed to create ADK session:\n\n"
                f"`{e}`"
            )
        ).send()


@cl.on_message
async def on_message(
    message: cl.Message
):

    session_id = cl.user_session.get(
        "session_id"
    )

    try:

        events = await run_agent(
            session_id=session_id,
            message=message.content,
        )

        answer = extract_answer(events)

        await cl.Message(
            content=answer
        ).send()

    except httpx.HTTPStatusError as e:

        await cl.Message(
            content=(
                "ADK request failed.\n\n"
                f"Status: `{e.response.status_code}`\n\n"
                f"Response:\n"
                f"```text\n{e.response.text}\n```"
            )
        ).send()

    except Exception as e:

        await cl.Message(
            content=(
                "Error calling ADK agent:\n\n"
                f"`{e}`"
            )
        ).send()