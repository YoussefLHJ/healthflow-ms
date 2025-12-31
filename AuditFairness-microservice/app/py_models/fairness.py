from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.db import Base


class FairnessSnapshot(Base):
    __tablename__ = "fairness_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # High-level fairness summary
    overall_status = Column(String, default="unknown")  # pass/warn/fail
    disparate_impact = Column(Float)
    statistical_parity = Column(Float)
    equal_opportunity = Column(Float)
    predictive_parity = Column(Float)

    # Serialized JSON blobs used by the frontend
    race_metrics = Column(JSON, nullable=False, default=list)
    gender_metrics = Column(JSON, nullable=False, default=list)
    age_metrics = Column(JSON, nullable=False, default=list)
    fairness_metrics = Column(JSON, nullable=False, default=list)
    fairness_trend = Column(JSON, nullable=False, default=list)
    risk_distribution = Column(JSON, nullable=False, default=list)
