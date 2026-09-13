"""
FastAPI CME Incident Management Dummy REST API.

Provides endpoints to check service health and query CME support incidents
by incident ID or product symbol.
"""

import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from .data import INCIDENTS
except (ImportError, ValueError):
    from data import INCIDENTS

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("incident_api")

app = FastAPI(
    title="CME Incident Management REST API",
    description="Simulated CME internal enterprise REST service for support incident management.",
    version="1.0.0",
)


# Pydantic Schemas
class HealthResponse(BaseModel):
    status: str = Field(..., example="UP")


class IncidentModel(BaseModel):
    incident_id: str
    symbol: str
    issue: str
    status: str
    severity: str
    assigned_team: str
    root_cause_notes: str
    created_at: str


class IncidentSearchResponse(BaseModel):
    symbol: Optional[str] = None
    count: int
    incidents: List[IncidentModel]


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health():
    """Returns the operational status of the API service."""
    logger.info("[INCIDENT API] GET /health")
    return {"status": "UP"}


@app.get("/incidents", response_model=IncidentSearchResponse, tags=["Incidents"])
def list_incidents(symbol: Optional[str] = Query(None, description="Optional futures product symbol (e.g., NQ, ES, CL, GC)")):
    """Lists support incidents. If symbol is provided, filters by normalized symbol."""
    if symbol:
        clean_symbol = symbol.strip().upper()
        logger.info(f"[INCIDENT API] Search incidents symbol={clean_symbol}")
        filtered = [inc for inc in INCIDENTS if inc["symbol"].upper() == clean_symbol]
        return {
            "symbol": clean_symbol,
            "count": len(filtered),
            "incidents": filtered,
        }
    
    logger.info("[INCIDENT API] Search incidents all")
    return {
        "count": len(INCIDENTS),
        "incidents": INCIDENTS,
    }


@app.get("/incidents/{incident_id}", response_model=IncidentModel, tags=["Incidents"])
def get_incident_by_id(incident_id: str):
    """Retrieves a single support incident by normalized incident ID (e.g., INC-101)."""
    clean_id = incident_id.strip().upper()
    logger.info(f"[INCIDENT API] Get incident incident_id={clean_id}")
    
    for inc in INCIDENTS:
        if inc["incident_id"].upper() == clean_id:
            return inc
            
    raise HTTPException(
        status_code=404,
        detail=f"Incident '{clean_id}' not found."
    )
