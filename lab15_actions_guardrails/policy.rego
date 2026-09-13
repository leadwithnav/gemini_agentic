# Open Policy Agent (OPA) Rego Policy for CME Market Operations Agent
# Package: cme.authz
#
# Implements Role-Based Access Control (RBAC) & Attribute-Based Access Control (ABAC)

package cme.authz

import future.keywords.if
import future.keywords.in

# Default deny all actions
default allow := false

# Rule 1: SUPER_ADMIN has full permissions across all products and actions
allow if {
    input.user.role == "SUPER_ADMIN"
}

# Rule 2: RISK_OFFICER can execute status updates and margin updates for any product
allow if {
    input.user.role == "RISK_OFFICER"
    input.action in ["update_product_status", "update_margin_requirement", "create_support_ticket", "get_product_details", "get_market_status"]
    not margin_exceeds_threshold
}

# Rule 3: SUPPORT_ANALYST (ABAC Rule): Can create support tickets and update product status ONLY for non-Equity commodities (Agriculture, Metals, Energy, FX)
allow if {
    input.user.role == "SUPPORT_ANALYST"
    input.action in ["create_support_ticket", "get_product_details", "get_market_status"]
}

allow if {
    input.user.role == "SUPPORT_ANALYST"
    input.action == "update_product_status"
    # ABAC Attribute Check: Product Asset Class must NOT be Equity Index
    input.resource.asset_class in ["Agriculture", "Metals", "Energy", "FX"]
}

# ABAC Boundary Rule: Margin updates exceeding $50,000 require SUPER_ADMIN
margin_exceeds_threshold if {
    input.action == "update_margin_requirement"
    input.arguments.new_amount_usd > 50000.0
}
