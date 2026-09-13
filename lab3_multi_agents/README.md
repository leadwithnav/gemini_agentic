# Lab 3: Multi-Agent Orchestration Patterns (ADK V2) - CME Group

This directory contains six core multi-agent orchestration patterns and a student challenge built using Google ADK V2 Graph Architecture (`google.adk.agents.Agent` and `google.adk.Workflow`).

## Overview of Modules

gcloud auth application-default login

1. **`part3_1_sequential_agent`**: Sequential linear graph execution (Market Researcher → Risk Analyst → Executive Reporter).
2. **`part3_2_parallel_agent`**: Concurrent fan-out order inspection (Volatility Analyst + Compliance Auditor + Position Limit Inspector → Synthesis Reporter).
3. **`part3_3_loop_agent`**: Iterative drafting & quality control critique loop (Report Drafter ⇄ QC Critic → Report Formatter).
4. **`part3_4_graph_agent`**: Conditional state-driven DAG routing (`FAST_TRACK`, `LEGAL_REVIEW`, `STANDARD`).
5. **`part3_5_dynamic_agent`**: Runtime async intent classification and dynamic specialist dispatch.
6. **`part3_6_collaborative_agent`**: Peer-to-peer control handoff & collaborative consensus swarm.
7. **`student_challenge`**: Integrated end-to-end CME multi-agent trade workflow.

## Running the Web UI

Launch the ADK Web UI from inside this directory:

```bash
cd lab3_multi_agents
adk web --port 8000 .
```

Open your browser to `http://localhost:8000` to test each pattern interactive dropdown.
