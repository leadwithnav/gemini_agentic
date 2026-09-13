"""
Pydantic Schemas for Layer 3 Application Guardrails.

Provides strict data type checking, regex symbol validation, numerical boundary limits,
and field sanity checks before any action execution.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal

VALID_SYMBOLS = ["ES", "NQ", "CL", "GC", "ZC", "6E"]

class UpdateProductStatusRequest(BaseModel):
    symbol: str = Field(..., description="CME Futures Product Symbol (e.g. ES, CL, NQ)")
    new_status: Literal["TRADING", "HALTED", "SUSPENDED", "CLOSED"] = Field(..., description="New operational status")
    reason: str = Field(..., min_length=10, description="Justification reason (minimum 10 characters)")
    investigation_id: str = Field(..., min_length=5, description="Unique correlation ID for idempotency deduplication")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_SYMBOLS:
            raise ValueError(f"Invalid symbol '{clean}'. Must be one of {VALID_SYMBOLS}.")
        return clean


class UpdateMarginRequest(BaseModel):
    symbol: str = Field(..., description="CME Futures Product Symbol")
    margin_type: Literal["INITIAL", "MAINTENANCE"] = Field(..., description="Margin requirement level")
    new_amount_usd: float = Field(..., ge=100.0, le=500000.0, description="Margin requirement in USD ($100 to $500,000)")
    reason: str = Field(..., min_length=10, description="Operational justification reason")
    investigation_id: str = Field(..., min_length=5, description="Unique correlation ID for idempotency deduplication")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_SYMBOLS:
            raise ValueError(f"Invalid symbol '{clean}'. Must be one of {VALID_SYMBOLS}.")
        return clean


class CreateSupportTicketRequest(BaseModel):
    symbol: str = Field(..., description="CME Product Symbol")
    issue_type: str = Field(..., min_length=3, description="Incident category")
    description: str = Field(..., min_length=10, description="Detailed problem description")
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    investigation_id: str = Field(..., min_length=5, description="Unique correlation ID for idempotency deduplication")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_SYMBOLS:
            raise ValueError(f"Invalid symbol '{clean}'. Must be one of {VALID_SYMBOLS}.")
        return clean
