"""
CME Exchange Information REST API.

Provides exchange metadata used by the MCP Server.
"""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .data import EXCHANGES


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("exchange_api")


app = FastAPI(
    title="CME Exchange Information REST API",
    description="Simulated enterprise REST service for CME exchange metadata.",
    version="1.0.0",
)


class ExchangeModel(BaseModel):
    exchange_code: str
    exchange_name: str
    location: str
    description: str


@app.get("/health")
def health():
    return {
        "status": "UP"
    }


@app.get(
    "/exchanges/{exchange_code}",
    response_model=ExchangeModel,
)
def get_exchange(exchange_code: str):

    code = exchange_code.strip().upper()

    logger.info(
        f"[EXCHANGE API] GET /exchanges/{code}"
    )

    exchange = EXCHANGES.get(code)

    if not exchange:
        raise HTTPException(
            status_code=404,
            detail=f"Exchange '{code}' not found.",
        )

    return exchange