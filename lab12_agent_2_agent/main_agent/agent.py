from google.adk import Agent

from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

from google.adk.tools.agent_tool import AgentTool


MODEL = "gemini-2.5-flash"


# ============================================================
# REMOTE A2A AGENT
# ============================================================

KNOWLEDGE_AGENT_URL = "http://localhost:8001"

KNOWLEDGE_AGENT_CARD_URL = (
    f"{KNOWLEDGE_AGENT_URL}"
    f"{AGENT_CARD_WELL_KNOWN_PATH}"
)


remote_knowledge_agent = RemoteA2aAgent(

    name="remote_knowledge_agent",

    description="""
    Remote specialist agent that answers
    company policy and employee-process questions.
    """,

    agent_card=KNOWLEDGE_AGENT_CARD_URL,
)


# ============================================================
# EXPOSE REMOTE AGENT AS TOOL
# ============================================================

knowledge_agent_tool = AgentTool(
    agent=remote_knowledge_agent
)


# ============================================================
# MAIN AGENT
# ============================================================

root_agent = Agent(

    name="employee_assistant",

    model=MODEL,

    description="""
    General employee assistant.

    Delegates company policy questions
    to a remote specialist through A2A.
    """,

    instruction="""
You are an Employee Assistant.

For company policy or internal process questions,
you MUST delegate to the remote Knowledge Policy Agent.

Examples:

- What is the travel policy?
- How many remote-work days are allowed?
- How do I request a laptop?
- What is the parental leave policy?

Do not answer these questions yourself.

Use the remote_knowledge_agent tool.

For simple greetings or general conversation,
you may answer directly.
""",

    tools=[
        knowledge_agent_tool,
    ],
)