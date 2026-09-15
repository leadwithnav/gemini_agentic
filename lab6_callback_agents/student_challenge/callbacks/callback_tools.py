"""
Lab 6 Student Challenge:
Before-Tool & After-Tool Callbacks

Goal:
Add simple governance and observability
around tool execution.
"""

import time
import logging
from typing import Any, Dict, Optional

from google.adk import Context
from pydantic import BaseModel, Field, ValidationError


logger = logging.getLogger("exchange_agent")
logging.basicConfig(level=logging.INFO)



# ============================================================
# 3. BEFORE TOOL CALLBACK
# ============================================================

def before_tool_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Context,
) -> Optional[Dict[str, Any]]:

    tool_name = getattr(tool, "name", str(tool))
 
    print("[BEFORE TOOL] Checks passed")

    return None


# ============================================================
# 4. AFTER TOOL CALLBACK
# ============================================================

def after_tool_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Context,
    tool_response: Any,
) -> Optional[Dict[str, Any]]:

    tool_name = getattr(tool, "name", str(tool))

    print(f"[AFTER TOOL] {tool_name} completed ")

    return None