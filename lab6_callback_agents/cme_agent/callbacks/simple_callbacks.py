"""
Lab 6: Simple ADK Tool Callbacks

Purpose:
- Print which tool is called.
- Store tool information in session state.
"""


from typing import Any, Dict, Optional
from google.adk import Context
import logging
import warnings

# ------------------------------------------------------------
# 1. Show only ERROR-level Python / ADK logs
# ------------------------------------------------------------
logging.basicConfig(level=logging.ERROR)

logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.adk").setLevel(logging.ERROR)

# ------------------------------------------------------------
# 2. Hide Uvicorn request/access logs
# ------------------------------------------------------------
logging.getLogger("uvicorn").setLevel(logging.ERROR)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
logging.getLogger("uvicorn.access").disabled = True

# ------------------------------------------------------------
# 3. Hide Python warnings
# ------------------------------------------------------------
warnings.filterwarnings("ignore")


# ============================================================
# BEFORE TOOL CALLBACK
# ============================================================

def before_tool_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Context,
) -> Optional[Dict[str, Any]]:

    tool_name = getattr(tool, "name", str(tool))

    # Print tool call
    print(f"\n[BEFORE TOOL] Calling: {tool_name}")
    print(f"[BEFORE TOOL] Arguments: {args}")

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

    tool_name = getattr(tool, "name", str(tool))

    # Print completed tool
    print(f"\n[AFTER TOOL] Completed: {tool_name}")

    return None