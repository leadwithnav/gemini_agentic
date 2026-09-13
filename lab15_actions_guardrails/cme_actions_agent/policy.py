"""
Deterministic Policy & Guardrail Engine for CME Market Operations Agent (Lab 2).

Enforces:
1. Risk Tiers (SAFE, CONTROLLED, SENSITIVE)
2. Parameter Guardrail Validation (Symbol whitelist, status enums, margin bounds)
3. Idempotency Locks (investigation_id + action_name deduplication)
4. Immutable Audit Trail Logging
5. Human-in-the-Loop (HITL) Gatekeeper for SENSITIVE actions
"""

from enum import Enum
from typing import Dict, Any, Callable, List, Optional
import uuid
import datetime
from .data import PRODUCTS

class RiskTier(str, Enum):
    SAFE = "SAFE"
    CONTROLLED = "CONTROLLED"
    SENSITIVE = "SENSITIVE"

class PolicyEngine:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.idempotency_store: Dict[str, str] = {}  # key -> audit_id
        self.pending_actions: Dict[str, Dict[str, Any]] = {} # audit_id -> action info

    def _generate_audit_id(self) -> str:
        return f"AUDIT-{uuid.uuid4().hex[:8].upper()}"

    def validate_guardrails(self, action_name: str, args: Dict[str, Any]) -> Optional[str]:
        """
        Deterministic parameter guardrail validation.
        Returns an error message string if a guardrail rule is violated, or None if passed.
        """
        symbol = args.get("symbol", "").strip().upper()
        
        # Guardrail 1: Symbol Whitelist Check
        if symbol and symbol not in PRODUCTS:
            return f"GUARDRAIL_VIOLATION: Product symbol '{symbol}' is not recognized in the CME product catalog. Valid symbols: {list(PRODUCTS.keys())}"

        # Guardrail 2: Status Enum Check for status update tools
        if action_name == "update_product_status":
            new_status = args.get("new_status", "").strip().upper()
            valid_statuses = ["TRADING", "HALTED", "SUSPENDED", "CLOSED"]
            if new_status not in valid_statuses:
                return f"GUARDRAIL_VIOLATION: Invalid status '{new_status}'. Must be one of {valid_statuses}."

        # Guardrail 3: Margin Type and Threshold Check for margin update tools
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
        """
        Evaluates guardrails, checks idempotency, and executes or gates actions based on Risk Tier.
        """
        audit_id = self._generate_audit_id()
        idempotency_key = f"{investigation_id.strip()}:{action_name.strip()}"

        # Step 1: Deterministic Guardrail Check
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

        # Step 2: Idempotency Enforcement
        if idempotency_key in self.idempotency_store:
            prior_audit_id = self.idempotency_store[idempotency_key]
            err_msg = (
                f"IDEMPOTENCY_REJECTED: Action '{action_name}' with investigation_id "
                f"'{investigation_id}' has already been processed under audit ID {prior_audit_id}."
            )
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_type": action_name,
                "arguments": arguments,
                "risk_tier": risk_tier.value,
                "guardrail_status": "PASSED",
                "approval_status": "REJECTED_DUPLICATE",
                "execution_status": "IDEMPOTENCY_REJECTED",
                "error_message": err_msg,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            return {
                "status": "error",
                "error": err_msg,
                "audit_id": audit_id,
                "prior_audit_id": prior_audit_id,
                "is_simulated_data": True
            }

        # Record idempotency lock
        self.idempotency_store[idempotency_key] = audit_id

        # Step 3: Handle Execution based on Risk Tier
        if risk_tier in [RiskTier.SAFE, RiskTier.CONTROLLED]:
            # Auto-approve & Execute immediately
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
            # Gate action requiring Human-in-the-Loop Approval
            pending_entry = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_name": action_name,
                "arguments": arguments,
                "execution_func": execution_func
            }
            self.pending_actions[audit_id] = pending_entry

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
                "message": (
                    f"ACTION GATED: Action '{action_name}' is classified as SENSITIVE. "
                    f"Human approval is required before changes are applied to production simulated systems."
                ),
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "action_name": action_name,
                "arguments": arguments,
                "risk_tier": "SENSITIVE",
                "approval_required": True,
                "is_simulated_data": True
            }

    def approve_action(self, audit_id: str) -> Dict[str, Any]:
        """Human approval callback to execute a pending SENSITIVE action."""
        if audit_id not in self.pending_actions:
            return {
                "status": "error",
                "error": f"Audit ID '{audit_id}' not found in pending human approval queue.",
                "is_simulated_data": True
            }

        pending = self.pending_actions.pop(audit_id)
        exec_func = pending["execution_func"]
        result = exec_func()

        # Update audit trail
        for record in self.audit_log:
            if record["audit_id"] == audit_id:
                record["approval_status"] = "HUMAN_APPROVED"
                record["execution_status"] = "EXECUTED"
                record["executed_at"] = datetime.datetime.now().isoformat()
                record["result"] = result
                break

        result["audit_id"] = audit_id
        result["approval_status"] = "HUMAN_APPROVED"
        return result

    def reject_action(self, audit_id: str, reason: str = "Rejected by operator") -> Dict[str, Any]:
        """Human rejection callback for a pending SENSITIVE action."""
        if audit_id not in self.pending_actions:
            return {
                "status": "error",
                "error": f"Audit ID '{audit_id}' not found in pending approval queue.",
                "is_simulated_data": True
            }

        self.pending_actions.pop(audit_id)

        for record in self.audit_log:
            if record["audit_id"] == audit_id:
                record["approval_status"] = "HUMAN_REJECTED"
                record["execution_status"] = "CANCELLED"
                record["rejection_reason"] = reason
                break

        return {
            "status": "rejected",
            "audit_id": audit_id,
            "message": f"Action '{audit_id}' was rejected by operator. Reason: {reason}",
            "is_simulated_data": True
        }

# Global singleton policy engine instance
policy_engine = PolicyEngine()
