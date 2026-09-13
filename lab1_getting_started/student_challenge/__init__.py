"""
Student Challenge 1B Package: Fix the Product Support Agent

Contains:
- starter_agent.py: Flawed starter agent with 4 imperfect tools & weak instructions (For Student Refactoring)
- solution_agent.py: Reference solution meeting all 4 test criteria and safety guardrails
"""

from .starter_agent import starter_agent
from .solution_agent import solution_agent

__all__ = ["starter_agent", "solution_agent"]
