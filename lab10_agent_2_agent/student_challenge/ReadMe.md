# Activate your python venv
source venv/bin/activate

# Add requirement for A2A
cd lab10_agent_2_agent
pip install -r requirements.txt


# Run Exchange Remote Agent
uvicorn student_challenge.exchange_agent:a2a_app --host 0.0.0.0 --port 8001

# Check Agent Card Exposed by Remote Agent
# Open a browser and check this Url
http://localhost:8001/.well-known/agent-card.json


# Run Product Remote Agent
uvicorn student_challenge.product_agent:a2a_app --host 0.0.0.0 --port 8002

# Check Agent Card Exposed by Remote Agent
# Open a browser and check this Url
http://localhost:8002/.well-known/agent-card.json

# Open a new terminal and keep the remote agent running in previous terminal

# Activate your Virtual Environment
source venv/bin/activate

# Run the Main Agent
cd lab10_agent_2_agent/student_challenge
adk web .

# Test Prompt
"What products are available on CME?"
"Where is NYMEX located and what is it known for?"

