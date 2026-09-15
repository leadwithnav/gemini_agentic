"""
Simple Agent Callbacks - Lab 6

Purpose:
- Print when an agent starts.
- Print when an agent finishes.
- Store agent execution information in session state.
"""

from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types


# ============================================================
# BEFORE AGENT CALLBACK
# ============================================================

def before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:

    agent_name = callback_context.agent_name

    print(f"\n[AGENT START] {agent_name}")

    return None


# ============================================================
# AFTER AGENT CALLBACK
# ============================================================

def after_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:

    agent_name = callback_context.agent_name

    print(f"\n[AGENT END] {agent_name}")

    return None
