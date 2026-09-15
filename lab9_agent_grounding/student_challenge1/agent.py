from google.adk import Agent
from google.adk.tools import VertexAiSearchTool


#TODO Configure your datastore
DATA_STORE_ID = ()


root_agent = Agent(
    name="exchange_knowledge_agent",
    model="gemini-2.5-flash",

    instruction="""
You are a CME Exchange Support Agent.

Use the Vertex AI Search knowledge base to answer questions
about exchanges and products.

RULES:
- Use the knowledge base for factual information.
- Do not guess or invent information.
- If the information is not found, say so clearly.
- Keep answers clear and concise.
""",

    tools=[
       #TODO: ADD vertex search tool
    ],
)