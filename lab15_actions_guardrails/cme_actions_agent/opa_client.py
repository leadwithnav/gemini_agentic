"""
OPA (Open Policy Agent) Client for CME Market Operations Agent.

Integrates with a locally running OPA server (via Docker container at http://localhost:8181)
and includes an embedded Rego evaluator fallback for offline execution.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple

OPA_URL = "http://localhost:8181/v1/data/cme/authz/allow"

class OPAClient:
    def __init__(self, server_url: str = OPA_URL):
        self.server_url = server_url

    def evaluate_policy_remote(self, input_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Query local OPA server via REST HTTP request.
        Returns (allow_boolean, mode_description).
        """
        try:
            req_data = json.dumps({"input": input_payload}).encode("utf-8")
            req = urllib.request.Request(
                self.server_url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    body = json.loads(resp.read().decode("utf-8"))
                    allowed = body.get("result", False)
                    return allowed, "OPA Container (http://localhost:8181)"
        except (urllib.error.URLError, TimeoutError, OSError):
            pass  # Server not reachable, fallback to embedded evaluator

        return self.evaluate_policy_embedded(input_payload)

    def evaluate_policy_embedded(self, input_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Embedded Python implementation matching policy.rego rules.
        Used as a fallback when OPA container is offline.
        """
        user = input_payload.get("user", {})
        action = input_payload.get("action", "")
        resource = input_payload.get("resource", {})
        arguments = input_payload.get("arguments", {})
        role = user.get("role", "UNAUTHENTICATED")

        # Rule 1: SUPER_ADMIN
        if role == "SUPER_ADMIN":
            return True, "Embedded Rego Policy (SUPER_ADMIN Rule)"

        # Margin Threshold ABAC Check (> $50,000 requires SUPER_ADMIN)
        if action == "update_margin_requirement":
            new_amt = float(arguments.get("new_amount_usd", 0))
            if new_amt > 50000.0 and role != "SUPER_ADMIN":
                return False, "Embedded Rego Policy (ABAC Deny: Margin > $50k requires SUPER_ADMIN)"

        # Rule 2: RISK_OFFICER
        if role == "RISK_OFFICER":
            if action in ["update_product_status", "update_margin_requirement", "create_support_ticket", "get_product_details", "get_market_status"]:
                return True, "Embedded Rego Policy (RISK_OFFICER Rule)"

        # Rule 3: SUPPORT_ANALYST (ABAC Rules)
        if role == "SUPPORT_ANALYST":
            if action in ["create_support_ticket", "get_product_details", "get_market_status"]:
                return True, "Embedded Rego Policy (SUPPORT_ANALYST Safe Rule)"
            if action == "update_product_status":
                asset_class = resource.get("asset_class", "")
                if asset_class in ["Agriculture", "Metals", "Energy", "FX"]:
                    return True, f"Embedded Rego Policy (ABAC Allow: SUPPORT_ANALYST permitted for {asset_class})"
                else:
                    return False, f"Embedded Rego Policy (ABAC Deny: SUPPORT_ANALYST forbidden for {asset_class})"

        return False, "Embedded Rego Policy (Default Deny)"

    def is_allowed(self, user_context: Dict[str, Any], action: str, resource_context: Dict[str, Any], arguments: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluate access policy against OPA container or embedded Rego engine."""
        payload = {
            "user": user_context,
            "action": action,
            "resource": resource_context,
            "arguments": arguments
        }
        return self.evaluate_policy_remote(payload)

# Global singleton client instance
opa_client = OPAClient()
