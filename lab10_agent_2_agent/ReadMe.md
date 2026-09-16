# Activate your python venv
source venv/bin/activate

# Add requirement for A2A
cd lab10_agent_2_agent
pip install -r requirements.txt


# Run Remote Agent
uvicorn remote_agent.agent:a2a_app --host 0.0.0.0 --port 8001

# Check Agent Card Exposed by Remote Agent

Open a browser and check this Url
http://localhost:8001/.well-known/agent-card.json

# Open a new terminal and keep the remote agent running in previous terminal

# Activate your Virtual Environment
source venv/bin/activate

# Run the Main Agent
cd lab10_agent_2_agent
adk web .

# Test Prompt
"what is market status of NQ?"

