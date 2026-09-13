from google.adk import Agent
from google.adk import Workflow
from google.adk import Event

book_review_agent = Agent(
    name="book_review_agent",
    model="gemini-2.5-flash",
    instruction="""Return the review of a given book in maximum 200 words""",
    output_schema=str,
)

book_review_summarizer_agent = Agent(
    name="book_review_summarizer_agent",
    model="gemini-2.5-flash",
    instruction="""For a given book review, summarize it in maximum 50 words """,
    output_schema=str,
)


def upper_case_tool(node_input: str):
    just_upper_case = node_input.upper()
    return Event(
        message=f"{just_upper_case}\n.",
    )


root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", book_review_agent, book_review_summarizer_agent, upper_case_tool)
    ],
)