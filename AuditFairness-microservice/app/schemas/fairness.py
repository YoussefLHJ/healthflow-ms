from pydantic import BaseModel
from typing import Any, Dict, List, Literal


class PredictionRecord(BaseModel):
    patient_id: str
    y_true: int
    y_pred: int
    score: float
    race: str
    gender: str
    age_group: str


class GroupPerformance(BaseModel):
    group: str
    accuracy: float
    precision: float
    recall: float
    fpr: float
    fnr: float
    count: int


class FairnessMetric(BaseModel):
    metric: str
    value: float
    threshold: float
    status: Literal["pass", "warn", "fail"]


class FairnessTrendPoint(BaseModel):
    month: str
    disparateImpact: float
    statisticalParity: float
    equalOpportunity: float


class FairnessSnapshotBase(BaseModel):
    model_version: str
    overall_status: str
    disparate_impact: float
    statistical_parity: float
    equal_opportunity: float
    predictive_parity: float
    race_metrics: List[Dict[str, Any]]
    gender_metrics: List[Dict[str, Any]]
    age_metrics: List[Dict[str, Any]]
    fairness_metrics: List[Dict[str, Any]]
    fairness_trend: List[Dict[str, Any]]
    risk_distribution: List[Dict[str, Any]]


class FairnessSnapshotOut(FairnessSnapshotBase):
    id: int

    class Config:
        from_attributes = True


class AuditFairnessResponse(BaseModel):
    snapshot: FairnessSnapshotOut
