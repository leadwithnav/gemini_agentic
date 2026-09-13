"""
Student Challenge 2B — Solution Policy Engine (Lab 2 Reference Solution).

Provides full guardrail validation for `update_margin_requirement`, idempotency locking,
audit trail generation, and HITL authorization gating.
"""

from enum import Enum
from typing import Dict, Any, Callable, List, Optional
import uuid
import datetime
try:
    from cme_actions_agent.data import PRODUCTS
except ImportError:
    from lab2_actions_guardrails.cme_actions_agent.data import PRODUCTS

class RiskTier(str, Enum):
    SAFE = "SAFE"
    CONTROLLED = "CONTROLLED"
    SENSITIVE = "SENSITIVE"

class SolutionPolicyEngine:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.idempotency_store: Dict[str, str] = {}
        self.pending_actions: Dict[str, Dict[str, Any]] = {}

    def _generate_audit_id(self) -> str:
        return f"AUDIT-SOL-{uuid.uuid4().hex[:8].upper()}"

    def validate_guardrails(self, action_name: str, args: Dict[str, Any]) -> Optional[str]:
        symbol = args.get("symbol", "").strip().upper()
        
        if symbol and symbol not in PRODUCTS:
            return f"GUARDRAIL_VIOLATION: Symbol '{symbol}' not found in CME catalog."

        if action_name == "update_product_status":
            new_status = args.get("new_status", "").strip().upper()
            if new_status not in ["TRADING", "HALTED", "SUSPENDED", "CLOSED"]:
                return f"GUARDRAIL_VIOLATION: Invalid status '{new_status}'."

        # Guardrails for update_margin_requirement
        if action_name == "update_margin_requirement":
            margin_type = args.get("margin_type", "").strip().upper()
            if margin_type not in ["INITIAL", "MAINTENANCE"]:
                return f"GUARDRAIL_VIOLATION: Invalid margin_type '{margin_type}'. Must be 'INITIAL' or 'MAINTENANCE'."
            
            try:
                new_amount = float(args.get("new_amount_usd", 0))
                if new_amount < 100.0 or new_amount > 500000.0:
                    return f"GUARDRAIL_VIOLATION: Margin amount ${new_amount:,.2f} USD is out of permitted range [$100 - $500,000]."
            except (ValueError, TypeError):
                return "GUARDRAIL_VIOLATION: Margin amount must be a valid positive numeric value."

        return None

    def evaluate_and_execute(
        self,
        action_name: str,
        risk_tier: RiskTier,
        execution_func: Callable[[], Dict[str, Any]],
        arguments: Dict[str, Any],
        investigation_id: str
    ) -> Dict[str, Any]:
        audit_id = self._generate_audit_id()
        idempotency_key = f"{investigation_id.strip()}:{action_name.strip()}"

        guardrail_error = self.validate_guardrails(action_name, arguments)
        if guardrail_error:
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_type": action_name,
                "arguments": arguments,
                "risk_tier": risk_tier.value,
                "guardrail_status": "FAILED",
                "approval_status": "REJECTED_BY_GUARDRAIL",
                "execution_status": "BLOCKED",
                "error_message": guardrail_error,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            return {
                "status": "error",
                "error": guardrail_error,
                "audit_id": audit_id,
                "is_simulated_data": True
            }

        if idempotency_key in self.idempotency_store:
            prior_id = self.idempotency_store[idempotency_key]
            err_msg = f"IDEMPOTENCY_REJECTED: Duplicate action '{action_name}' under investigation '{investigation_id}'."
            return {
                "status": "error",
                "error": err_msg,
                "audit_id": audit_id,
                "prior_audit_id": prior_id,
                "is_simulated_data": True
            }

        self.idempotency_store[idempotency_key] = audit_id

        if risk_tier in [RiskTier.SAFE, RiskTier.CONTROLLED]:
            result = execution_func()
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_type": action_name,
                "arguments": arguments,
                "risk_tier": risk_tier.value,
                "guardrail_status": "PASSED",
                "approval_status": "AUTO_APPROVED",
                "execution_status": "EXECUTED",
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            result["audit_id"] = audit_id
            return result

        elif risk_tier == RiskTier.SENSITIVE:
            self.pending_actions[audit_id] = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_name": action_name,
                "arguments": arguments,
                "execution_func": execution_func
            }
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_type": action_name,
                "arguments": arguments,
                "risk_tier": risk_tier.value,
                "guardrail_status": "PASSED",
                "approval_status": "PENDING_HUMAN_APPROVAL",
                "execution_status": "BLOCKED_WAITING_APPROVAL",
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            return {
                "status": "pending_approval",
                "message": f"ACTION GATED: Action '{action_name}' is SENSITIVE and requires human approval.",
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_name": action_name,
                "arguments": arguments,
                "risk_tier": "SENSITIVE",
                "approval_required": True,
                "is_simulated_data": True
            }

    def approve_action(self, audit_id: str) -> Dict[str, Any]:
        if audit_id not in self.pending_actions:
            return {"status": "error", "error": "Audit ID not found.", "is_simulated_data": True}
        pending = self.pending_actions.pop(audit_id)
        result = pending["execution_func"]()
        for record in self.audit_log:
            if record["audit_id"] == audit_id:
                record["approval_status"] = "HUMAN_APPROVED"
                record["execution_status"] = "EXECUTED"
                break
        result["audit_id"] = audit_id
        result["approval_status"] = "HUMAN_APPROVED"
        return result

solution_policy_engine = SolutionPolicyEngine()
