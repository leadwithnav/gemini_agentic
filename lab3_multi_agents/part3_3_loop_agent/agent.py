"""
Part 3.3: Iterative Loop Graph Agents (ADK V2)
Use case: Improve an Incident Summary
Flow: Summary Writer -> Quality Reviewer -> revise until required fields are present -> Publish
Reference: adk2/dynamic_workflow_agent
"""
from typing import Any
from google.adk import Agent
from google.adk import Workflow
from google.adk import Context
from google.adk import Event
from google.adk.workflow import node

try:
    from tools import get_ticket_details, update_ticket_status
except ImportError:
    from lab3_multi_agents.tools import get_ticket_details, update_ticket_status

# Node 1: Summary Writer Agent
summary_writer_agent = Agent(
    name="summary_writer_agent",
    model="gemini-3.6-flash",
    instruction="""You are the CME Incident Summary Writer.
Given an incident request (e.g. INC-101, INC-102, or INC-103):
1. Call `get_ticket_details` to fetch current ticket information.
2. Draft an initial Incident Investigation Summary containing Ticket ID, Product Symbol, Problem Description, Current Status, and Assigned Team.""",
    tools=[get_ticket_details],
)

# Node 2: Quality Reviewer Agent
quality_reviewer_agent = Agent(
    name="quality_reviewer_agent",
    model="gemini-3.6-flash",
    instruction="""You are the CME Support Quality Reviewer.
Review the drafted incident summary:
1. Verify if ALL required fields are present: Ticket ID, Symbol, Problem Description, Status (OPEN/INVESTIGATING/RESOLVED), and Assigned Team.
2. If status needs updating or investigation notes need adding, call `update_ticket_status`.
3. Provide feedback on missing fields or clear approval if complete.""",
    tools=[update_ticket_status],
)

# Node 3: Publisher Agent
publisher_agent = Agent(
    name="publisher_agent",
    model="gemini-3.6-flash",
    instruction="""You are the CME Support Publishing Manager.
Take the reviewed and approved incident summary:
1. Format into an official CME Incident Briefing Bulletin.
2. Present with clear headers, verified ticket status stamp, and assigned team recommendations.
Output the finalized publication-ready report.""",
)

# Workflow Loop Controller
@node(rerun_on_resume=True)
async def iterative_loop_workflow(ctx: Context, node_input: str) -> str:
    # Step 1: Draft initial summary
    draft = await ctx.run_node(summary_writer_agent)
    
    # Step 2: Quality review & feedback
    review = await ctx.run_node(quality_reviewer_agent, node_input=draft)
    
    # Step 3: Publish finalized incident bulletin
    final_bulletin = await ctx.run_node(publisher_agent, node_input=review)
    
    return final_bulletin

# Root Loop Graph Workflow
root_agent = Workflow(
    name="part3_3_loop_agent",
    edges=[("START", iterative_loop_workflow)],
)
