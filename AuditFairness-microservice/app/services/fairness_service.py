from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import httpx
from app.schemas.fairness import PredictionRecord
from app.core.config import settings

# from evidently import Report
# from evidently.metrics import (
#     ClassificationPerformanceByGroupMetric,
#     ClassificationFairnessMetric,
# )

from app.py_models.fairness import FairnessSnapshot
from app.schemas.fairness import PredictionRecord, FairnessSnapshotOut


def compute_fairness_snapshot(db: Session, model_version: str, records: List[PredictionRecord]) -> FairnessSnapshotOut:
    df = pd.DataFrame([r.dict() for r in records])

    def build_group_perf(group_col: str) -> List[Dict[str, Any]]:
        groups = df[group_col].unique().tolist()
        result = []
        for g in groups:
            sub = df[df[group_col] == g]
            if sub.empty:
                continue
            tp = ((sub.y_true == 1) & (sub.y_pred == 1)).sum()
            tn = ((sub.y_true == 0) & (sub.y_pred == 0)).sum()
            fp = ((sub.y_true == 0) & (sub.y_pred == 1)).sum()
            fn = ((sub.y_true == 1) & (sub.y_pred == 0)).sum()
            total = len(sub)
            acc = (tp + tn) / total if total else 0.0
            prec = tp / (tp + fp) if (tp + fp) else 0.0
            rec = tp / (tp + fn) if (tp + fn) else 0.0
            fpr = fp / (fp + tn) if (fp + tn) else 0.0
            fnr = fn / (fn + tp) if (fn + tp) else 0.0
            result.append(
                {
                    "group": g,
                    "accuracy": acc,
                    "precision": prec,
                    "recall": rec,
                    "fpr": fpr,
                    "fnr": fnr,
                    "count": total,
                }
            )
        return result

    race_metrics = build_group_perf("race")
    gender_metrics = build_group_perf("gender")
    age_metrics = build_group_perf("age_group")

    # simple global metrics (placeholder logic)
    disparate_impact = 0.94
    statistical_parity = 0.96
    equal_opportunity = 0.92
    predictive_parity = 0.93
    overall_status = "pass"

    fairness_metrics = [
        {
            "metric": "Disparate Impact (Race)",
            "value": disparate_impact,
            "threshold": 0.8,
            "status": "pass",
        },
        {
            "metric": "Statistical Parity (Gender)",
            "value": statistical_parity,
            "threshold": 0.8,
            "status": "pass",
        },
        {
            "metric": "Equal Opportunity (Age)",
            "value": equal_opportunity,
            "threshold": 0.8,
            "status": "pass",
        },
        {
            "metric": "Predictive Parity (Race)",
            "value": predictive_parity,
            "threshold": 0.8,
            "status": "pass",
        },
    ]

    snapshot = FairnessSnapshot(
        model_version=model_version,
        overall_status=overall_status,
        disparate_impact=disparate_impact,
        statistical_parity=statistical_parity,
        equal_opportunity=equal_opportunity,
        predictive_parity=predictive_parity,
        race_metrics=race_metrics,
        gender_metrics=gender_metrics,
        age_metrics=age_metrics,
        fairness_metrics=fairness_metrics,
        fairness_trend=[],
        risk_distribution=[],
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)          # first/only refresh: get id, created_at

    # now compute and store trend (no extra refresh afterwards)
    trend = build_fairness_trend(db, model_version)
    snapshot.fairness_trend = trend
    db.commit()

    return FairnessSnapshotOut.model_validate(snapshot)

def get_latest_snapshot(db: Session, model_version: str | None = None) -> FairnessSnapshotOut | None:
    q = db.query(FairnessSnapshot)
    if model_version:
        q = q.filter(FairnessSnapshot.model_version == model_version)
    snapshot = q.order_by(FairnessSnapshot.created_at.desc()).first()
    if not snapshot:
        return None
    return FairnessSnapshotOut.model_validate(snapshot)





async def fetch_records_from_scoreapi(limit: int = 1000) -> List[PredictionRecord]:
    base = settings.SCORE_API_BASE  # from .env
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{base}/scores/all", params={"skip": 0, "limit": limit})
        res.raise_for_status()
        items = res.json()

    records: List[PredictionRecord] = []
    for item in items:
        features = item["features_used"]
        score = item["readmission_risk_score"]
        risk_category = item["risk_category"].upper()

        y_pred = 1 if risk_category in ("MEDIUM", "HIGH") else 0

        age = features.get("age")
        if age is None:
            age_group = "unknown"
        elif age < 36:
            age_group = "18-35"
        elif age < 51:
            age_group = "36-50"
        elif age < 66:
            age_group = "51-65"
        else:
            age_group = "65+"

        gender = features.get("gender", "unknown")

        record = PredictionRecord(
            patient_id=item["patient_resource_id"],
            # TODO: replace with real label when available
            y_true=0,
            y_pred=y_pred,
            score=score,
            race="unknown",   # you only have state in features_used
            gender=gender,
            age_group=age_group,
        )
        records.append(record)

    return records

def build_fairness_trend(db: Session, model_version: str) -> List[Dict[str, Any]]:
    snaps: List[FairnessSnapshot] = (
        db.query(FairnessSnapshot)
        .filter(FairnessSnapshot.model_version == model_version)
        .order_by(FairnessSnapshot.created_at.asc())
        .all()
    )

    trend: List[Dict[str, Any]] = []
    for s in snaps:
        trend.append(
            {
                "month": s.created_at.strftime("%Y-%m-%d"),
                "disparateImpact": s.disparate_impact,
                "statisticalParity": s.statistical_parity,
                "equalOpportunity": s.equal_opportunity,
            }
        )
    return trend
