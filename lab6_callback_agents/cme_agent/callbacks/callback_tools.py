"""
Before-Tool and After-Tool Callbacks for Security Governance & Observability (Lab 6).

Flow:
Gemini
   │
   │ execute_sql(...)
   ▼
before_tool_callback
   │
   ├── Record start time
   ├── Pydantic Input Validation
   ├── Authorization / Permission Check
   └── Business Guardrails
   │
   ▼
BigQuery / Tool Execution
   │
   ▼
after_tool_callback
   │
   ├── Calculate duration (latency)
   ├── Log success metrics
   ├── Sanitize response (remove internal_notes, debug_info, etc.)
   └── Store observability state
   │
   ▼
Gemini
"""

import time
import logging
import re
from typing import Dict, Any, Optional

from google.adk import Context
from pydantic import BaseModel, Field, ValidationError


from ..tools.bigquery_tools import PROJECT_ID, DATASET_ID
from ..tools.bigquery_tools import PROJECT_ID, DATASET_ID

# Configure logger
logger = logging.getLogger("cme_agent")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


# ============================================================
# SIMULATED PERMISSION DATA
# Later this can be replaced with OPA / IAM / RBAC
# ============================================================

AUTHORIZED_USERS = {
    "alice": True,
    "bob": True,
    "guest": False,
}


# ============================================================
# BUSINESS RULES
# ============================================================

ALLOWED_TABLES = {
    "PRODUCTS",
    "MARKET_STATUS",
    "INCIDENTS",
}


# ============================================================
# HELPER FUNCTIONS FOR BEFORE TOOL CALLBACK
# ============================================================

def block(error_message: str) -> Dict[str, Any]:
    """Return a standardized block payload for tool callbacks."""
    return {
        "status": "BLOCKED",
        "error": error_message
    }


def get_tool_name(tool: Any) -> str:
    """Extract tool name from tool instance or string representation."""
    return getattr(tool, "name", str(tool))


def record_start_time(tool_name: str, ctx: Context) -> None:
    """Record start time for latency calculation in after_tool_callback."""
    print(f"\n[BEFORE TOOL] Intercepting tool: {tool_name}", flush=True)
    ctx.state[f"tool_start_time:{tool_name}"] = time.perf_counter()




def check_permission(tool_name: str, ctx: Context) -> Optional[str]:
    user_id = ctx.state.get("user_id")
    user_authorized = AUTHORIZED_USERS.get(user_id, False)
    if not user_authorized:
        return f"User '{user_id}' is not authorized."
    return None


def check_business_guardrails(
    tool_name: str,
    args: Dict[str, Any],
    ctx: Context,
) -> Optional[str]:

    args_dict = args or {}

    sql = args_dict.get("query", "").strip()
    sql_upper = sql.upper()

    # Rule 1: Only SELECT queries are allowed
    if not sql_upper.startswith("SELECT"):
        return "Only SELECT queries are allowed."

    # Rule 2: Only approved tables can be queried
    if not any(table in sql_upper for table in ALLOWED_TABLES):
        print("[GUARDRAIL] [FAIL] Unauthorized table", flush=True)
        return f"Only these tables are allowed: {sorted(ALLOWED_TABLES)}"

    return None


# ============================================================
# BEFORE TOOL CALLBACK
# ============================================================

def before_tool_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Context,
) -> Optional[Dict[str, Any]]:

    tool_name = get_tool_name(tool)

    record_start_time(tool_name, tool_context)

    permission_error = check_permission(tool_name, tool_context)
    if permission_error:
        return block(permission_error)

    guardrail_error = check_business_guardrails(tool_name,args,tool_context)
    if guardrail_error:
        return block(guardrail_error)

    return None


# ============================================================
# AFTER TOOL CALLBACK
# ============================================================

def after_tool_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Context,
    tool_response: Any,
) -> Optional[Dict[str, Any]]:
    """
    Runs after a tool executes successfully.
    """
    tool_name = getattr(tool, "name", str(tool))

    # Latency calculation
    start_key = f"tool_start_time:{tool_name}"
    start_time = tool_context.state.get(start_key)
    duration_ms = None
    if start_time:
        duration_ms = (time.perf_counter() - start_time) * 1000
    if duration_ms is not None:
        tool_context.state["last_tool_duration_ms"] = duration_ms

    return None
