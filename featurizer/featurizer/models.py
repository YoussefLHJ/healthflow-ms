from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from featurizer.database import Base


class PatientFeatures(Base):
    __tablename__ = "patient_features"

    id = Column(Integer, primary_key=True, index=True)
    patient_resource_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Target Variable for 30-day readmission prediction
    readmission_30d = Column(Boolean, default=False)  # Binary target (0/1)
    
    # Demographics
    gender = Column(String(50), nullable=True)
    birth_date = Column(String(50), nullable=True)  # Keep as string from DeID
    age = Column(Float, nullable=True)  # Computed from birth_date
    state = Column(String(100), nullable=True)
    
    # Encounter Features (prioritized for readmission prediction)
    num_encounters = Column(Integer, default=0)
    length_of_stay_days = Column(Float, default=0.0)  # Most recent or average LOS
    avg_los = Column(Float, default=0.0)
    class_code = Column(String(50), nullable=True)  # EMER, IMP, AMB
    type_code = Column(String(50), nullable=True) 
    is_emergency = Column(Boolean, default=False)  # class_code='EMER'
    is_inpatient = Column(Boolean, default=False)   # class_code='IMP'
    days_since_last_discharge = Column(Integer, nullable=True)
    
    # Condition Features (major readmission predictor)
    num_conditions = Column(Integer, default=0)
    primary_condition_code = Column(String(50), nullable=True)  # Main ICD/SNOMED
    primary_condition_display = Column(String(255), nullable=True)
    has_chronic_conditions = Column(Boolean, default=False)
    condition_codes = Column(JSON, nullable=True)  # List of all condition codes
    
    # Observation Features (vitals/labs volatility)
    num_observations = Column(Integer, default=0)
    obs_abnormal_count = Column(Integer, default=0)
    has_abnormal_glucose = Column(Boolean, default=False)
    has_abnormal_hr = Column(Boolean, default=False)
    has_abnormal_temp = Column(Boolean, default=False)
    has_abnormal_saturation = Column(Boolean, default=False)
    vital_signs_available = Column(Boolean, default=False)
    
    # Medication/Procedure Features
    num_med_requests = Column(Integer, default=0)
    num_procedures = Column(Integer, default=0)
    polypharmacy = Column(Boolean, default=False)  # >= 5 medications
    medication_codes = Column(JSON, nullable=True)  # List of med codes
    
    # NLP features (from clinical notes)
    ner_entities = Column(JSON, nullable=True)
    embedding_mean = Column(JSON, nullable=True)  # Store as array
    
    # Derived risk indicators (legacy from previous implementation)
    has_multiple_encounters = Column(Boolean, default=False)
    has_long_stay = Column(Boolean, default=False)
    high_med_burden = Column(Boolean, default=False)
    high_condition_count = Column(Boolean, default=False)
    has_abnormal_labs = Column(Boolean, default=False)
    clinical_complexity_score = Column(Float, default=0.0)  # Computed risk indicator
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "patient_resource_id": self.patient_resource_id,
            "readmission_30d": self.readmission_30d,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "age": self.age,
            "state": self.state,
            "num_encounters": self.num_encounters,
            "length_of_stay_days": self.length_of_stay_days,
            "avg_los": self.avg_los,
            "class_code": self.class_code,
            "type_code": self.type_code,
            "is_emergency": self.is_emergency,
            "is_inpatient": self.is_inpatient,
            "days_since_last_discharge": self.days_since_last_discharge,
            "num_conditions": self.num_conditions,
            "primary_condition_code": self.primary_condition_code,
            "primary_condition_display": self.primary_condition_display,
            "has_chronic_conditions": self.has_chronic_conditions,
            "condition_codes": self.condition_codes,
            "num_observations": self.num_observations,
            "obs_abnormal_count": self.obs_abnormal_count,
            "has_abnormal_glucose": self.has_abnormal_glucose,
            "has_abnormal_hr": self.has_abnormal_hr,
            "has_abnormal_temp": self.has_abnormal_temp,
            "has_abnormal_saturation": self.has_abnormal_saturation,
            "vital_signs_available": self.vital_signs_available,
            "num_med_requests": self.num_med_requests,
            "num_procedures": self.num_procedures,
            "polypharmacy": self.polypharmacy,
            "medication_codes": self.medication_codes,
            "ner_entities": self.ner_entities,
            "embedding_mean": self.embedding_mean,
            "clinical_complexity_score": self.clinical_complexity_score,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }