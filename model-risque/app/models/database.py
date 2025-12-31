import os
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("MODEL_DB_URL", "sqlite:///./model_risque.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Prediction model for storing prediction results
class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_resource_id = Column(String, index=True, nullable=False)
    readmission_risk_score = Column(Float, nullable=False)
    risk_category = Column(String, nullable=False)  # LOW, MEDIUM, HIGH
    features_used = Column(JSON, nullable=True)
    shap_explanations = Column(JSON, nullable=True)
    model_version = Column(String, nullable=False)
    prediction_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

# PatientFeatures model (matches featurizer schema)
class PatientFeatures(Base):
    __tablename__ = "patient_features"

    id = Column(Integer, primary_key=True, index=True)
    patient_resource_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Target Variable
    readmission_30d = Column(Boolean, default=False)
    
    # Demographics
    gender = Column(String(50), nullable=True)
    age = Column(Float, nullable=True)
    state = Column(String(100), nullable=True)
    
    # Encounter Features
    num_encounters = Column(Integer, default=0)
    length_of_stay_days = Column(Float, default=0.0)
    avg_los = Column(Float, default=0.0)
    is_emergency = Column(Boolean, default=False)
    is_inpatient = Column(Boolean, default=False)
    days_since_last_discharge = Column(Integer, nullable=True)
    
    # Condition Features
    num_conditions = Column(Integer, default=0)
    has_chronic_conditions = Column(Boolean, default=False)
    
    # Observation Features
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
    polypharmacy = Column(Boolean, default=False)
    
    # Derived risk indicators
    has_multiple_encounters = Column(Boolean, default=False)
    has_long_stay = Column(Boolean, default=False)
    high_med_burden = Column(Boolean, default=False)
    high_condition_count = Column(Boolean, default=False)
    has_abnormal_labs = Column(Boolean, default=False)
    clinical_complexity_score = Column(Float, default=0.0)


def get_feature_columns() -> List[str]:
    """Define the feature columns for ML model"""
    return [
        # Demographics
        'age',
        
        # Encounter Features
        'num_encounters', 'length_of_stay_days', 'avg_los',
        'is_emergency', 'is_inpatient', 'days_since_last_discharge',
        
        # Condition Features  
        'num_conditions', 'has_chronic_conditions',
        
        # Observation Features
        'num_observations', 'obs_abnormal_count',
        'has_abnormal_glucose', 'has_abnormal_hr', 'has_abnormal_temp',
        'has_abnormal_saturation', 'vital_signs_available',
        
        # Medication/Procedure Features
        'num_med_requests', 'num_procedures', 'polypharmacy',
        
        # Risk Indicators
        'has_multiple_encounters', 'has_long_stay', 'high_med_burden',
        'high_condition_count', 'has_abnormal_labs', 'clinical_complexity_score'
    ]


def get_categorical_columns() -> List[str]:
    """Define categorical columns for encoding"""
    return ['gender', 'state']


def load_training_data(db: Session, featurizer_api_url: str, limit: Optional[int] = None) -> pd.DataFrame:
    """Load training data from featurizer API and store in local database"""
    import httpx
    
    try:
        # Fetch patient features from featurizer API
        with httpx.Client(timeout=30) as client:
            # Get bulk features from featurizer service
            response = client.get(f"{featurizer_api_url}/features/stats")
            if response.status_code != 200:
                raise ValueError(f"Failed to connect to featurizer API: {response.status_code}")
            
            stats = response.json()
            total_patients = stats.get("total_patients", 0)
            
            if total_patients == 0:
                raise ValueError("No patients found in featurizer database")
            
            # Fetch all patient features (or limited number)
            patients = []
            batch_size = 50
            max_patients = min(limit or total_patients, total_patients)
            
            for offset in range(0, max_patients, batch_size):
                batch_response = client.get(f"{featurizer_api_url}/features/batch", 
                                          params={"offset": offset, "limit": batch_size})
                
                if batch_response.status_code == 200:
                    batch_data = batch_response.json()
                    patients.extend(batch_data.get("patients", []))
                else:
                    # Fallback: try to get individual patient features
                    break
            
            if not patients:
                raise ValueError("Could not fetch patient data from featurizer API")
            
            # Store in local database for faster access during training
            for patient_data in patients:
                existing = db.query(PatientFeatures).filter(
                    PatientFeatures.patient_resource_id == patient_data["patient_resource_id"]
                ).first()
                
                if not existing:
                    patient_record = PatientFeatures(**patient_data)
                    db.add(patient_record)
            
            db.commit()
            
            # Convert to DataFrame for ML training
            df_data = []
            for patient in patients:
                df_data.append({
                    'patient_resource_id': patient.get('patient_resource_id'),
                    'readmission_30d': patient.get('readmission_30d', False),
                    'gender': patient.get('gender'),
                    'age': patient.get('age'),
                    'state': patient.get('state'),
                    'num_encounters': patient.get('num_encounters', 0),
                    'length_of_stay_days': patient.get('length_of_stay_days', 0.0),
                    'avg_los': patient.get('avg_los', 0.0),
                    'is_emergency': patient.get('is_emergency', False),
                    'is_inpatient': patient.get('is_inpatient', False),
                    'days_since_last_discharge': patient.get('days_since_last_discharge'),
                    'num_conditions': patient.get('num_conditions', 0),
                    'has_chronic_conditions': patient.get('has_chronic_conditions', False),
                    'num_observations': patient.get('num_observations', 0),
                    'obs_abnormal_count': patient.get('obs_abnormal_count', 0),
                    'has_abnormal_glucose': patient.get('has_abnormal_glucose', False),
                    'has_abnormal_hr': patient.get('has_abnormal_hr', False),
                    'has_abnormal_temp': patient.get('has_abnormal_temp', False),
                    'has_abnormal_saturation': patient.get('has_abnormal_saturation', False),
                    'vital_signs_available': patient.get('vital_signs_available', False),
                    'num_med_requests': patient.get('num_med_requests', 0),
                    'num_procedures': patient.get('num_procedures', 0),
                    'polypharmacy': patient.get('polypharmacy', False),
                    'has_multiple_encounters': patient.get('has_multiple_encounters', False),
                    'has_long_stay': patient.get('has_long_stay', False),
                    'high_med_burden': patient.get('high_med_burden', False),
                    'high_condition_count': patient.get('high_condition_count', False),
                    'has_abnormal_labs': patient.get('has_abnormal_labs', False),
                    'clinical_complexity_score': patient.get('clinical_complexity_score', 0.0),
                })
            
            return pd.DataFrame(df_data)
            
    except Exception as e:
        # Fallback: load from local database if API fails
        print(f"API fetch failed: {e}. Using local database.")
        return load_local_training_data(db, limit)


def load_local_training_data(db: Session, limit: Optional[int] = None) -> pd.DataFrame:
    """Load training data from local database"""
    query = db.query(PatientFeatures)
    
    if limit:
        query = query.limit(limit)
    
    # Convert to list of dictionaries
    patients = []
    for patient in query.all():
        patient_dict = {
            'patient_resource_id': patient.patient_resource_id,
            'readmission_30d': patient.readmission_30d,
            'gender': patient.gender,
            'age': patient.age,
            'state': patient.state,
            'num_encounters': patient.num_encounters,
            'length_of_stay_days': patient.length_of_stay_days,
            'avg_los': patient.avg_los,
            'is_emergency': patient.is_emergency,
            'is_inpatient': patient.is_inpatient,
            'days_since_last_discharge': patient.days_since_last_discharge,
            'num_conditions': patient.num_conditions,
            'has_chronic_conditions': patient.has_chronic_conditions,
            'num_observations': patient.num_observations,
            'obs_abnormal_count': patient.obs_abnormal_count,
            'has_abnormal_glucose': patient.has_abnormal_glucose,
            'has_abnormal_hr': patient.has_abnormal_hr,
            'has_abnormal_temp': patient.has_abnormal_temp,
            'has_abnormal_saturation': patient.has_abnormal_saturation,
            'vital_signs_available': patient.vital_signs_available,
            'num_med_requests': patient.num_med_requests,
            'num_procedures': patient.num_procedures,
            'polypharmacy': patient.polypharmacy,
            'has_multiple_encounters': patient.has_multiple_encounters,
            'has_long_stay': patient.has_long_stay,
            'high_med_burden': patient.high_med_burden,
            'high_condition_count': patient.high_condition_count,
            'has_abnormal_labs': patient.has_abnormal_labs,
            'clinical_complexity_score': patient.clinical_complexity_score,
        }
        patients.append(patient_dict)
    
    return pd.DataFrame(patients)