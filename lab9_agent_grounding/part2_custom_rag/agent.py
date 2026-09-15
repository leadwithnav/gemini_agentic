import agentplatform

from agentplatform import types
from google.genai import types as genai_types
from google.adk import Agent

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ID = "instructor-02"
LOCATION = "us-central1"

CORPUS_NAME = ("projects/instructor-02/locations/us-central1/ragCorpora/4254591030004809728")


MODEL = "gemini-2.5-flash"


# ---------------------------------------------------------
# RAG Client
# ---------------------------------------------------------

rag_client = agentplatform.Client(
    project=PROJECT_ID,
    location=LOCATION,
)


# ---------------------------------------------------------
# RAG Tool
# ---------------------------------------------------------

def search_exchange_knowledge(query: str) -> str:
    """
    Search the CME exchange knowledge base for information
    about exchanges and products.
    """

    response = rag_client.rag.retrieve_contexts(

        vertex_rag_store=genai_types.VertexRagStore(
            rag_resources=[
                genai_types.VertexRagStoreRagResource(
                    rag_corpus=CORPUS_NAME
                )
            ]
        ),

        query=types.RagQuery(
            text=query,
            rag_retrieval_config=genai_types.RagRetrievalConfig(
                top_k=3
            )
        )
    )

    return str(response)


# ---------------------------------------------------------
# ADK Agent
# ---------------------------------------------------------

root_agent = Agent(
    name="cme_exchange_rag_agent",
    model=MODEL,

    description=(
        "Answers questions about CME exchanges and products "
        "using the approved RAG knowledge base."
    ),

    instruction="""
You are a CME Exchange Support Agent.

Use search_exchange_knowledge whenever the user asks factual
questions about CME exchanges or products.

RULES:
- Base factual answers on information returned by the RAG tool.
- Do not invent information.
- If the knowledge base does not contain the answer, say so clearly.
- Keep answers concise and professional.
""",

    tools=[
        search_exchange_knowledge
    ],
)