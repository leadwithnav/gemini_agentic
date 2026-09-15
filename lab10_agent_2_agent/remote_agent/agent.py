from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from dotenv import load_dotenv

load_dotenv()


MODEL = "gemini-2.5-flash"


def get_company_policy(topic: str) -> str:

    policies = {
        "travel": (
            "Employees may claim hotel expenses up to "
            "$200 per night for approved business travel."
        ),
        "remote work": (
            "Employees may work remotely up to "
            "3 days per week with manager approval."
        ),
        "laptop": (
            "Employees can request a new laptop through "
            "the internal IT service desk."
        ),
        "parental leave": (
            "Employees are eligible for 16 weeks "
            "of parental leave."
        ),
    }

    topic = topic.lower().strip()

    for key, value in policies.items():

        if key in topic:
            return value

    return "No policy was found for this topic."


root_agent = Agent(

    name="knowledge_policy_agent",

    model=MODEL,

    description="""
    Independent company policy advisor.
    """,

    instruction="""
You are the Company Knowledge & Policy Agent.

You answer questions about internal company policies.

Always use get_company_policy when answering policy questions.

Do not invent policy information.

Keep answers concise.
""",

    tools=[
        get_company_policy,
    ],
)


a2a_app = to_a2a(
    root_agent,
    port=8001,
)