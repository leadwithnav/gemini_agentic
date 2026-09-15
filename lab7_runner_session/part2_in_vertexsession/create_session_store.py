# create_session_store.py

import vertexai

PROJECT_ID = "instructor-02"
LOCATION = "us-central1"

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
)

agent_engine = client.agent_engines.create(
    config={
        "display_name": "CME Support Session Store"
    }
)

resource_name = agent_engine.api_resource.name

print("FULL RESOURCE NAME:")
print(resource_name)

print("\nAGENT ENGINE ID:")
print(resource_name.split("/")[-1])