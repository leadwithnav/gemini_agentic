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

try:
    from .tools.bigquery_tools import PROJECT_ID, DATASET_ID
except ImportError:
    from lab7_runner_session.tools.bigquery_tools import PROJECT_ID, DATASET_ID

# Configure logger
logger = logging.getLogger("cme_agent")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


# ============================================================
# 1. PYDANTIC MODEL
# Validate tool input
# ============================================================

class SQLToolInput(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="SQL query to execute"
    )


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

FORBIDDEN_OPERATIONS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "MERGE",
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


def validate_input(tool_name: str, args: Dict[str, Any]) -> Optional[str]:
    """
    Step 1: Pydantic Input Validation.
    Validates structural correctness of tool arguments.
    """
    args_dict = args or {}
    print(f"[BEFORE TOOL] Arguments: {args_dict}", flush=True)

    # Bypass Pydantic SQL validation for non-SQL tools
    if tool_name != "execute_sql" and "sql" not in args_dict:
        return None

    try:
        SQLToolInput.model_validate(args_dict)
        print("[PYDANTIC] [OK] Input is valid", flush=True)
        return None
    except ValidationError as error:
        print("[PYDANTIC] [FAIL] Invalid input", flush=True)
        return f"Invalid tool input: {error}"


def check_permission(tool_name: str, ctx: Context) -> Optional[str]:
    """
    Step 2: Permission Check.
    Validates whether the user is authorized to execute the tool.
    """
    user_id = ctx.state.get("user_id", "alice")
    user_authorized = AUTHORIZED_USERS.get(user_id, False)

    if not user_authorized:
        print(f"[PERMISSION] [FAIL] User '{user_id}' is not authorized", flush=True)
        return f"User '{user_id}' is not authorized."

    print(f"[PERMISSION] [OK] User '{user_id}' is authorized", flush=True)
    return None


def check_business_guardrails(
    tool_name: str,
    args: Dict[str, Any],
    ctx: Context,
) -> Optional[str]:
    """
    Step 3: Business Guardrails.
    Enforces business rules on tool execution (SELECT only, forbidden operations, approved tables, target project & dataset).
    """
    args_dict = args or {}

    # Bypass guardrails for non-SQL tools
    if tool_name != "execute_sql":
        print("[BEFORE TOOL] [OK] ALL CHECKS PASSED", flush=True)
        print("[BEFORE TOOL] -> Executing tool\n", flush=True)
        return None

    sql = args_dict.get("query", "").strip()
    sql_upper = sql.upper()

    # Rule 1: Only SELECT queries are allowed
    if not sql_upper.startswith("SELECT"):
        print("[GUARDRAIL] [FAIL] Only SELECT queries are allowed", flush=True)
        return "Only SELECT queries are allowed."

    # Rule 2: Block mutation operations
    for operation in FORBIDDEN_OPERATIONS:
        if re.search(r"\b" + operation + r"\b", sql_upper):
            print(
                f"[GUARDRAIL] [FAIL] Forbidden operation: {operation}",
                flush=True
            )
            return f"Operation '{operation}' is not allowed."

    # Rule 3: Only approved tables can be queried
    if not any(table in sql_upper for table in ALLOWED_TABLES):
        print("[GUARDRAIL] [FAIL] Unauthorized table", flush=True)
        return f"Only these tables are allowed: {sorted(ALLOWED_TABLES)}"

    # Rule 4: Query must target authorized project & dataset
    expected_project = (ctx.state.get("project_id") or PROJECT_ID or "").strip().upper()
    if expected_project and expected_project not in sql_upper:
        print(f"[GUARDRAIL] [FAIL] Unauthorized project: '{expected_project}'", flush=True)
        return f"Query does not target authorized project '{expected_project}'."

    expected_dataset = (ctx.state.get("dataset_id") or DATASET_ID or "").strip().upper()
    if expected_dataset and expected_dataset not in sql_upper:
        print(f"[GUARDRAIL] [FAIL] Unauthorized dataset: '{expected_dataset}'", flush=True)
        return f"Query does not target authorized dataset '{expected_dataset}'."

    print("[GUARDRAIL] [OK] Operation is allowed", flush=True)
    print("[BEFORE TOOL] [OK] ALL CHECKS PASSED", flush=True)
    print("[BEFORE TOOL] -> Executing tool\n", flush=True)

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

    validation_error = validate_input(tool_name, args)
    if validation_error:
        return block(validation_error)

    permission_error = check_permission(tool_name, tool_context)
    if permission_error:
        return block(permission_error)

    guardrail_error = check_business_guardrails(
        tool_name,
        args,
        tool_context
    )
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

    Responsibilities:
    1. Record tool execution information
    2. Calculate tool latency
    3. Add business observability context
    5. Preserve useful state for later metrics / tracing

    Returning None:
        ADK continues using the original tool response.

    Returning a dict:
        Replaces the original tool response.
    """
    tool_name = getattr(
        tool,
        "name",
        str(tool),
    )

    request_id = tool_context.state.get(
        "request_id",
        "unknown",
    )

    user_id = tool_context.state.get(
        "user_id",
        "unknown",
    )

    route = tool_context.state.get(
        "route",
        "unknown",
    )

    # --------------------------------------------------------
    # TOOL LATENCY
    # --------------------------------------------------------

    start_key = f"tool_start_time:{tool_name}"

    start_time = tool_context.state.get(
        start_key
    )

    duration_ms = None

    if start_time:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

    # --------------------------------------------------------
    # STRUCTURED APPLICATION LOG
    # --------------------------------------------------------

    logger.info(
        "tool_execution_completed",
        extra={
            "request_id": request_id,
            "user_id": user_id,
            "route": route,
            "tool_name": tool_name,
            "duration_ms": duration_ms,
            "success": True,
        },
    )

    if duration_ms is not None:
        print(f"\n[AFTER TOOL] Tool '{tool_name}' completed in {duration_ms:.2f}ms", flush=True)
    else:
        print(f"\n[AFTER TOOL] Tool '{tool_name}' completed", flush=True)

    print(f"[AFTER TOOL] Observability state: request_id={request_id}, user_id={user_id}, route={route}", flush=True)

    # --------------------------------------------------------
    # Store useful observability state
    # --------------------------------------------------------

    tool_context.state["last_tool"] = tool_name
    tool_context.state["last_tool_success"] = True

    if duration_ms is not None:
        tool_context.state[
            "last_tool_duration_ms"
        ] = duration_ms

    # Keep original response
    return None
