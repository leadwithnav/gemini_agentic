"""
Defense-in-Depth Policy Engine for CME Market Operations Agent (Lab 2).

Integrates:
- Layer 2: OPA RBAC/ABAC Policy Evaluation (opa_client)
- Layer 3: Pydantic Schema Validation (schemas)
- Layer 3: Idempotency Locks (investigation_id)
- Layer 3: Deterministic Business State Machine Rules
- Layer 3: Resilience & Audit Trail Logging
"""

from typing import Dict, Any, Callable, List, Optional
import uuid
import datetime
from pydantic import ValidationError

from .data import PRODUCTS, get_product
from .opa_client import opa_client
from .schemas import (
    UpdateProductStatusRequest,
    UpdateMarginRequest,
    CreateSupportTicketRequest,
)

class DefensePolicyEngine:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.idempotency_store: Dict[str, str] = {}  # key -> audit_id

    def _generate_audit_id(self) -> str:
        return f"AUDIT-DEF-{uuid.uuid4().hex[:8].upper()}"

    def evaluate_and_execute(
        self,
        user_context: Dict[str, Any],
        action_name: str,
        execution_func: Callable[[], Dict[str, Any]],
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes multi-layered defense pipeline:
        1. Layer 2: OPA RBAC/ABAC Policy Authorization Check
        2. Layer 3A: Pydantic Schema & Boundary Validation
        3. Layer 3B: Idempotency Lock Check
        4. Layer 3C: Business Logic State Transition Rule Check
        5. Execution & Audit Logging
        """
        audit_id = self._generate_audit_id()
        symbol = arguments.get("symbol", "").strip().upper()
        investigation_id = arguments.get("investigation_id", "DEFAULT-INV").strip()
        idempotency_key = f"{investigation_id}:{action_name}"

        # Fetch resource attributes for ABAC evaluation
        product_data = get_product(symbol) if symbol else None
        resource_context = {
            "symbol": symbol,
            "asset_class": product_data.get("asset_class", "UNKNOWN") if product_data else "UNKNOWN",
            "current_status": product_data.get("status", "UNKNOWN") if product_data else "UNKNOWN"
        }

        # ---------------------------------------------------------------------
        # STEP 1: LAYER 2 — OPA RBAC/ABAC Policy Evaluation
        # ---------------------------------------------------------------------
        opa_allowed, opa_mode = opa_client.is_allowed(
            user_context=user_context,
            action=action_name,
            resource_context=resource_context,
            arguments=arguments
        )

        if not opa_allowed:
            err_msg = (
                f"OPA_POLICY_DENIED: User '{user_context.get('username')}' (Role: {user_context.get('role')}) "
                f"is not authorized to perform action '{action_name}' on resource '{symbol}' ({resource_context['asset_class']}). Evaluated by {opa_mode}."
            )
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "user": user_context.get("username"),
                "role": user_context.get("role"),
                "action_type": action_name,
                "layer_failed": "LAYER_2_OPA_RBAC_ABAC",
                "opa_mode": opa_mode,
                "execution_status": "DENIED_BY_POLICY",
                "error_message": err_msg,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            return {
                "status": "error",
                "error": err_msg,
                "layer": "LAYER_2_OPA",
                "audit_id": audit_id,
                "is_simulated_data": True
            }

        # ---------------------------------------------------------------------
        # STEP 2: LAYER 3A — Pydantic Application Schema & Boundary Validation
        # ---------------------------------------------------------------------
        try:
            if action_name == "update_product_status":
                UpdateProductStatusRequest(**arguments)
            elif action_name == "update_margin_requirement":
                UpdateMarginRequest(**arguments)
            elif action_name == "create_support_ticket":
                CreateSupportTicketRequest(**arguments)
        except ValidationError as ve:
            errors = ve.errors()
            err_msg = f"PYDANTIC_VALIDATION_ERROR: Invalid payload structure. Details: {errors[0]['msg']} at field '{errors[0]['loc']}'"
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "user": user_context.get("username"),
                "action_type": action_name,
                "layer_failed": "LAYER_3_PYDANTIC_VALIDATION",
                "execution_status": "BLOCKED_INVALID_PAYLOAD",
                "error_message": err_msg,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            return {
                "status": "error",
                "error": err_msg,
                "layer": "LAYER_3_PYDANTIC",
                "audit_id": audit_id,
                "is_simulated_data": True
            }

        # ---------------------------------------------------------------------
        # STEP 3: LAYER 3B — Idempotency Deduplication Lock
        # ---------------------------------------------------------------------
        if idempotency_key in self.idempotency_store:
            prior_audit_id = self.idempotency_store[idempotency_key]
            err_msg = (
                f"IDEMPOTENCY_REJECTED: Duplicate action '{action_name}' under investigation '{investigation_id}' "
                f"has already been executed under audit record '{prior_audit_id}'."
            )
            audit_record = {
                "audit_id": audit_id,
                "investigation_id": investigation_id,
                "user": user_context.get("username"),
                "action_type": action_name,
                "layer_failed": "LAYER_3_IDEMPOTENCY",
                "execution_status": "IDEMPOTENCY_REJECTED",
                "error_message": err_msg,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.audit_log.append(audit_record)
            return {
                "status": "error",
                "error": err_msg,
                "layer": "LAYER_3_IDEMPOTENCY",
                "prior_audit_id": prior_audit_id,
                "audit_id": audit_id,
                "is_simulated_data": True
            }

        # Record idempotency lock
        self.idempotency_store[idempotency_key] = audit_id

        # ---------------------------------------------------------------------
        # STEP 4: LAYER 3C — Business State Machine Rules
        # ---------------------------------------------------------------------
        if action_name == "update_product_status" and product_data:
            current = product_data["status"]
            target = arguments.get("new_status", "").upper()
            if current == "CLOSED" and target == "TRADING":
                err_msg = "BUSINESS_RULE_VIOLATION: Cannot transition directly from CLOSED to TRADING without compliance re-clearing."
                audit_record = {
                    "audit_id": audit_id,
                    "investigation_id": investigation_id,
                    "action_type": action_name,
                    "layer_failed": "LAYER_3_BUSINESS_STATE_RULE",
                    "execution_status": "BLOCKED_STATE_RULE",
                    "error_message": err_msg,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.audit_log.append(audit_record)
                return {
                    "status": "error",
                    "error": err_msg,
                    "layer": "LAYER_3_BUSINESS_RULE",
                    "audit_id": audit_id,
                    "is_simulated_data": True
                }

        # ---------------------------------------------------------------------
        # STEP 5: Execution & Audit Log Recording
        # ---------------------------------------------------------------------
        result = execution_func()
        audit_record = {
            "audit_id": audit_id,
            "investigation_id": investigation_id,
            "user": user_context.get("username"),
            "role": user_context.get("role"),
            "action_type": action_name,
            "arguments": arguments,
            "opa_evaluator": opa_mode,
            "execution_status": "EXECUTED_SUCCESSFULLY",
            "result": result,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.audit_log.append(audit_record)
        result["audit_id"] = audit_id
        result["opa_evaluator"] = opa_mode
        return result

# Global singleton policy engine
defense_policy_engine = DefensePolicyEngine()
