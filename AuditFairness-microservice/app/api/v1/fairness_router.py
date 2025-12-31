from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.fairness import (
    PredictionRecord,
    AuditFairnessResponse,
    FairnessSnapshotOut,
)
from app.services.fairness_service import (
    compute_fairness_snapshot,
    fetch_records_from_scoreapi,
    get_latest_snapshot,
)

router = APIRouter(prefix="/fairness", tags=["fairness"])


@router.post("/audit-from-scoreapi", response_model=FairnessSnapshotOut)
async def run_fairness_from_scoreapi(
    model_version: str = Query("v1"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    records = await fetch_records_from_scoreapi(limit=limit)
    if not records:
        raise HTTPException(status_code=400, detail="No records fetched from ScoreAPI")
    return compute_fairness_snapshot(db, model_version, records)


@router.get("/latest", response_model=AuditFairnessResponse)
def get_latest_fairness(
    model_version: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Return the latest cached fairness snapshot (no recomputation).
    """
    snapshot = get_latest_snapshot(db, model_version)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot available")
    return AuditFairnessResponse(snapshot=snapshot)
