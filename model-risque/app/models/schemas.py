from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

# ==================== Pydantic Models ====================

class PredictionRequest(BaseModel):
    patient_resource_id: str = Field(..., description="Patient ID for prediction")


class FeatureVector(BaseModel):
    """Patient features for prediction"""
    age: Optional[float] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    
    # Encounter features
    num_encounters: int = 0
    length_of_stay_days: float = 0.0
    avg_los: float = 0.0
    is_emergency: bool = False
    is_inpatient: bool = False
    days_since_last_discharge: Optional[int] = None
    
    # Condition features
    num_conditions: int = 0
    has_chronic_conditions: bool = False
    
    # Observation features
    num_observations: int = 0
    obs_abnormal_count: int = 0
    has_abnormal_glucose: bool = False
    has_abnormal_hr: bool = False
    has_abnormal_temp: bool = False
    has_abnormal_saturation: bool = False
    vital_signs_available: bool = False
    
    # Medication/procedure features
    num_med_requests: int = 0
    num_procedures: int = 0
    polypharmacy: bool = False
    
    # Risk indicators
    has_multiple_encounters: bool = False
    has_long_stay: bool = False
    high_med_burden: bool = False
    high_condition_count: bool = False
    has_abnormal_labs: bool = False
    clinical_complexity_score: float = 0.0


class SHAPExplanation(BaseModel):
    """SHAP explanation for a prediction"""
    feature_name: str
    feature_value: Any
    shap_value: float
    impact: str  # "increases_risk" or "decreases_risk"


class PredictionResponse(BaseModel):
    """Response for readmission risk prediction"""
    patient_resource_id: str
    readmission_risk_score: float = Field(..., ge=0.0, le=1.0, description="Probability of 30-day readmission (0-1)")
    risk_category: str = Field(..., description="LOW, MEDIUM, HIGH")
    features_used: Dict[str, Any] = Field(..., description="Features used for prediction")
    shap_explanations: List[SHAPExplanation] = Field(..., description="SHAP explanations for key features")
    model_version: str = Field(..., description="Version of the prediction model")
    prediction_timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        from_attributes = True


class TrainingRequest(BaseModel):
    """Request to train a new model"""
    max_samples: Optional[int] = Field(None, description="Maximum number of samples to use for training")
    test_size: float = Field(0.2, description="Test set proportion")
    random_state: int = Field(42, description="Random seed for reproducibility")


class TrainingResponse(BaseModel):
    """Response for model training"""
    success: bool
    message: str
    model_version: str
    training_samples: int
    test_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float
    feature_importance: Dict[str, float]
    training_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelMetrics(BaseModel):
    """Model performance metrics"""
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float
    training_samples: int
    test_samples: int
    feature_count: int
    training_date: datetime
