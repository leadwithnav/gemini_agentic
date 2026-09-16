from google.adk import Agent
from google.adk.tools import VertexAiSearchTool


DATA_STORE_ID = (
    "projects/instructor-02/"
    "locations/global/"
    "collections/default_collection/"
    "dataStores/my-cme-datastore_1789496066667"
)


vertex_search = VertexAiSearchTool(
    data_store_id=DATA_STORE_ID
)


root_agent = Agent(
    name="cme_support_agent",
    model="gemini-2.5-flash",

    instruction="""
You are a CME Product Support Agent.

For every user question:
- Search the Vertex AI Search datastore.
- Use the retrieved information to answer the question.
- Always provide a final text response to the user.
- Do not invent information.
- If the answer is not found, say "Information not found in the knowledge base."
""",

    tools=[vertex_search],
)