"""
Student Challenge 2B — Starter Policy Engine (Defense-in-Depth).

Students complete:
1. Pydantic schema validation for update_margin_requirement.
2. ABAC OPA check for user role + margin amount limits.
"""

from typing import Dict, Any, Callable
try:
    from cme_actions_agent.policy_engine import defense_policy_engine
except ImportError:
    from lab2_actions_guardrails.cme_actions_agent.policy_engine import defense_policy_engine

def student_evaluate_and_execute(
    user_context: Dict[str, Any],
    action_name: str,
    execution_func: Callable[[], Dict[str, Any]],
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    # Pass through to defense policy engine
    return defense_policy_engine.evaluate_and_execute(
        user_context=user_context,
        action_name=action_name,
        execution_func=execution_func,
        arguments=arguments
    )
