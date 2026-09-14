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
# 1. INPUT MODEL
# ============================================================

class SQLToolInput(BaseModel):
    query: str = Field(..., min_length=1)


# ============================================================
# 2. SIMPLE BUSINESS RULE
# ============================================================

ALLOWED_TABLE = "EXCHANGE_PRODUCTS"


# ============================================================
# 3. BEFORE TOOL CALLBACK
# ============================================================

def before_tool_callback(
    tool: Any,
    args: Dict[str, Any],
    tool_context: Context,
) -> Optional[Dict[str, Any]]:

    tool_name = getattr(tool, "name", str(tool))

    print(f"\n[BEFORE TOOL] {tool_name}")

    # TODO 1:
    # Store current time in state.
    #
    # Hint:
    # time.perf_counter()
    #
    # Store it using:
    # tool_context.state["tool_start_time"]

    ______________________________


    # Only validate SQL tool
    if tool_name == "execute_sql":

        # TODO 2:
        # Validate args using SQLToolInput.
        #
        # Hint:
        # SQLToolInput.model_validate(...)

        try:

            ______________________________

            print("[PYDANTIC] Input valid")

        except ValidationError as error:

            return {
                "status": "BLOCKED",
                "error": f"Invalid input: {error}"
            }


        # ====================================================
        # SIMPLE BUSINESS GUARDRAIL
        # ====================================================

        sql = args.get("query", "").upper()


        # TODO 3:
        # Block query if it is NOT a SELECT.
        #
        # Hint:
        # sql.startswith("SELECT")

        if ______________________________:

            return {
                "status": "BLOCKED",
                "error": "Only SELECT queries are allowed."
            }


        # TODO 4:
        # Allow only EXCHANGE_PRODUCTS table.
        #
        # Hint:
        # Check whether ALLOWED_TABLE exists in sql.

        if ______________________________:

            return {
                "status": "BLOCKED",
                "error": "Only exchange_products table is allowed."
            }


    print("[BEFORE TOOL] Checks passed")

    # Returning None allows tool execution.
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


    # TODO 5:
    # Read start time from state.

    start_time = ______________________________


    # TODO 6:
    # Calculate duration in milliseconds.
    #
    # Formula:
    #
    # (current_time - start_time) * 1000

    duration_ms = ______________________________


    # TODO 7:
    # Log successful execution.
    #
    # Hint:
    #
    # logger.info(
    #     f"Tool {tool_name} completed in ..."
    # )

    ______________________________


    print(
        f"[AFTER TOOL] {tool_name} completed "
        f"in {duration_ms:.2f} ms"
    )


    # Store simple observability state

    tool_context.state["last_tool"] = tool_name
    tool_context.state["last_tool_duration_ms"] = duration_ms
    tool_context.state["last_tool_success"] = True


    # We are observing the response,
    # not replacing it.

    return None