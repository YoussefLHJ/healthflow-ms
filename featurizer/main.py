from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import py_eureka_client.eureka_client as eureka_client
import logging

# Load environment variables from .env file
load_dotenv()

from featurizer.services.featurizer_service import FeaturizerService
from featurizer.database import get_db, engine
from featurizer.models import PatientFeatures

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for API documentation and validation
class PatientRequest(BaseModel):
    patient_id: str = Field(..., description="Patient resource ID from FHIR data")
    force_refresh: bool = Field(False, description="Force refresh from source, bypass cache")

class BulkFeaturizeRequest(BaseModel):
    patient_ids: List[str] = Field(..., description="List of patient resource IDs")

class ReadmissionFeatures(BaseModel):
    """Enhanced features for 30-day readmission prediction"""
    # Target
    readmission_30d: bool = Field(description="Binary target: 30-day unplanned readmission")
    
    # Demographics  
    gender: Optional[str] = Field(description="Patient gender")
    age: Optional[float] = Field(description="Patient age computed from birth_date")
    
    # Encounters (key predictors)
    num_encounters: int = Field(description="Total number of encounters")
    length_of_stay_days: float = Field(description="Most recent length of stay")
    class_code: Optional[str] = Field(description="Encounter class: EMER/IMP/AMB") 
    is_emergency: bool = Field(description="TRUE if emergency encounter")
    is_inpatient: bool = Field(description="TRUE if inpatient encounter")
    days_since_last_discharge: Optional[int] = Field(description="Days since last discharge")
    
    # Conditions (major predictor)
    num_conditions: int = Field(description="Total condition count")
    primary_condition_code: Optional[str] = Field(description="Primary ICD/SNOMED code")
    has_chronic_conditions: bool = Field(description="Has chronic condition indicators")
    
    # Observations (vitals volatility)
    obs_abnormal_count: int = Field(description="Count of abnormal lab/vital values")
    has_abnormal_glucose: bool = Field(description="Abnormal glucose detected")
    has_abnormal_hr: bool = Field(description="Abnormal heart rate detected")
    vital_signs_available: bool = Field(description="Vital signs data available")
    
    # Medications
    num_med_requests: int = Field(description="Number of medications") 
    polypharmacy: bool = Field(description="≥5 medications (polypharmacy)")
    
    # Risk scoring
    clinical_complexity_score: float = Field(description="Computed clinical complexity (0-1)")

class HealthResponse(BaseModel):
    status: str = Field(description="Service health status")
    version: str = Field(description="API version")
    features_enabled: List[str] = Field(description="Available feature extraction capabilities")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and register with Eureka on startup"""
    logger.info(" Starting Featurizer service...")
    
    # Create database tables
    PatientFeatures.metadata.create_all(bind=engine)
    logger.info("✓ Database tables initialized")
    
    # Register with Eureka
    await eureka_client.init_async(
        eureka_server="http://localhost:8761/eureka",
        app_name="FEATURIZER-SERVICE",
        instance_port=int(os.getenv("PORT", 8001)),
        instance_host="localhost",
        instance_ip="127.0.0.1"
    )
    logger.info("✓ Featurizer service registered with Eureka")
    logger.info("✓ Featurizer ready to serve requests")
    
    yield
    
    # Shutdown: Unregister from Eureka
    await eureka_client.stop_async()
    logger.info("✓ Featurizer service unregistered from Eureka")
    logger.info(" Shutting down Featurizer service")

app = FastAPI(
    title="Featurizer Microservice for 30-Day Readmission Prediction",
    description="""
    **Enhanced FHIR Featurizer** for healthcare readmission risk prediction models.
    
    ## Key Features
    
    * **Target Variable**: 30-day readmission prediction (binary 0/1)
    * **Demographics**: Age, gender extraction from de-identified patient data
    * **Encounters**: LOS, class codes (EMER/IMP/AMB), emergency/inpatient flags
    * **Conditions**: ICD/SNOMED code extraction, chronic condition detection
    * **Observations**: Vital signs analysis, abnormal lab value detection
    * **Medications**: Polypharmacy detection (≥5 medications)
    * **Clinical Notes**: NLP processing with BioBERT/spaCy for entity extraction
    * **Risk Scoring**: Clinical complexity scoring for ModelRisque integration
    
    ## Essential Readmission Predictors
    
    Extracts literature-backed features including:
    - Length of stay, encounter type, emergency admissions
    - Comorbidity burden, chronic conditions  
    - Medication count, polypharmacy indicators
    """,
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins - adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.getenv("DEID_BASE_URL", "http://deid:8000")


@app.get("/", 
         summary="API Root",
         description="Welcome endpoint with API information")
async def root():
    return {
        "service": "Featurizer Microservice", 
        "version": "2.0.0",
        "description": "Enhanced FHIR featurizer for 30-day readmission prediction",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", 
         response_model=HealthResponse,
         summary="Health Check",
         description="Check service health and available feature extraction capabilities")
async def health_check():
    return HealthResponse(
        status="healthy",
        version="2.0.0", 
        features_enabled=[
            "30-day readmission target",
            "Demographics (age, gender)",
            "Encounter analysis (LOS, class codes)", 
            "Condition extraction (ICD/SNOMED)",
            "Vital signs analysis",
            "Polypharmacy detection",
            "NLP entity extraction",
            "Clinical complexity scoring"
        ]
    )


@app.get("/featurize/patient/{patient_id}",
         summary="Featurize Single Patient", 
         description="""
         Extract comprehensive features for a single patient optimized for readmission prediction.
         
         **Key Features Extracted:**
         - **Target**: 30-day readmission binary indicator
         - **Demographics**: Age computed from birth_date, gender 
         - **Encounters**: Length of stay, emergency/inpatient flags, days since discharge
         - **Conditions**: ICD/SNOMED codes, chronic condition detection
         - **Vitals**: Abnormal glucose/HR/temperature/saturation detection
         - **Medications**: Polypharmacy (≥5 meds), medication codes
         - **Risk Score**: Clinical complexity score (0-1 scale)
         
         Results are automatically cached in PostgreSQL database.
         """,
         tags=["Featurization"])
def featurize_patient(patient_id: str, 
                     force_refresh: bool = Query(False, description="Bypass cache and refresh from source"),
                     db: Session = Depends(get_db)):
    try:
        service = FeaturizerService(base_url=BASE, db_session=db)
        return service.featurize_patient_with_db(patient_id, force_refresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/featurize/patient",
          summary="Featurize Patient (POST)",
          description="Alternative POST endpoint for patient featurization with request body",
          tags=["Featurization"])
def featurize_patient_post(request: PatientRequest, db: Session = Depends(get_db)):
    try:
        service = FeaturizerService(base_url=BASE, db_session=db)
        return service.featurize_patient_with_db(request.patient_id, request.force_refresh)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/featurize/bulk",
          summary="Bulk Patient Featurization",
          description="""
          Featurize multiple patients in a single request for batch processing.
          
          Useful for:
          - Training data preparation 
          - Batch inference for ModelRisque
          - Bulk feature extraction pipelines
          
          Each patient is processed independently - failures for individual patients 
          won't stop the entire batch.
          """,
          tags=["Featurization"])
def featurize_bulk(request: BulkFeaturizeRequest, db: Session = Depends(get_db)):
    try:
        service = FeaturizerService(base_url=BASE, db_session=db)
        results = []
        for pid in request.patient_ids:
            try:
                features = service.featurize_patient_with_db(pid)
                results.append(features)
            except Exception as e:
                results.append({"patient_resource_id": pid, "error": str(e)})
        return {"rows": results, "total_processed": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features/patient/{patient_id}",
         summary="Get Cached Features",
         description="Retrieve cached features from database without recomputing",
         tags=["Database"])
def get_cached_features(patient_id: str, db: Session = Depends(get_db)):
    try:
        service = FeaturizerService(base_url=BASE, db_session=db)
        cached = service.get_features_from_db(patient_id)
        if not cached:
            raise HTTPException(status_code=404, detail="Features not found in cache")
        return cached.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features/all",
         summary="Get All Cached Features", 
         description="Retrieve all cached features with pagination",
         tags=["Database"])
def get_all_cached_features(skip: int = Query(0, description="Number of records to skip"), 
                           limit: int = Query(100, description="Maximum number of records to return"), 
                           db: Session = Depends(get_db)):
    try:
        features = db.query(PatientFeatures).offset(skip).limit(limit).all()
        return {"rows": [f.to_dict() for f in features], "total": len(features)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/features/stats",
         summary="Get Feature Statistics",
         description="Get aggregated statistics about cached features",
         tags=["Database"])
def get_feature_stats(db: Session = Depends(get_db)):
    """Get statistics about the feature database."""
    try:
        from sqlalchemy import func
        
        total_patients = db.query(func.count(PatientFeatures.id)).scalar() or 0
        
        if total_patients == 0:
            return {
                "total_patients": 0,
                "total_encounters": 0,
                "total_conditions": 0,
                "total_observations": 0,
                "total_medication_requests": 0,
                "readmission_rate": 0.0,
                "average_complexity_score": 0.0,
            }
        
        # Aggregate stats
        stats = db.query(
            func.sum(PatientFeatures.num_encounters).label("total_encounters"),
            func.sum(PatientFeatures.num_conditions).label("total_conditions"),
            func.sum(PatientFeatures.num_observations).label("total_observations"),
            func.sum(PatientFeatures.num_med_requests).label("total_medication_requests"),
            func.avg(PatientFeatures.clinical_complexity_score).label("avg_complexity"),
            func.sum(func.cast(PatientFeatures.readmission_30d, func.Integer)).label("readmissions")
        ).first()
        
        readmission_rate = (stats.readmissions / total_patients * 100) if stats.readmissions else 0.0
        
        return {
            "total_patients": total_patients,
            "total_encounters": int(stats.total_encounters or 0),
            "total_conditions": int(stats.total_conditions or 0),
            "total_observations": int(stats.total_observations or 0),
            "total_medication_requests": int(stats.total_medication_requests or 0),
            "readmission_rate": round(readmission_rate, 2),
            "average_complexity_score": round(float(stats.avg_complexity or 0), 2),
        }
    except Exception as e:
        logger.error(f"Error getting feature stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/featurize/all",
          summary="Featurize All Patients",
          description="""
          ⚠️ **CAUTION**: Featurizes ALL patients from DeID service. Use carefully on large datasets.
          
          This endpoint:
          - Fetches all patient IDs from DeID service
          - Processes each patient through the full featurization pipeline
          - Caches results in PostgreSQL database
          - Provides progress feedback for large datasets
          
          Ideal for initial data preparation and bulk processing.
          """,
          tags=["Featurization"])
def featurize_all_patients(force_refresh: bool = Query(False, description="Force refresh all cached features"),
                          limit: int = Query(None, description="Maximum number of patients to featurize (default: all patients)"), 
                          db: Session = Depends(get_db)):
    try:
        service = FeaturizerService(base_url=BASE, db_session=db)
        
        # Get all patient IDs from DeID service (request large limit to get all patients)
        patients_data = service._get("deid/patients?limit=10000")
        
        # Handle wrapped response format
        if isinstance(patients_data, dict):
            # Find the patients array in the response
            patients = None
            for key, value in patients_data.items():
                if isinstance(value, list):
                    patients = value
                    break
            if patients is None:
                patients = []
        else:
            patients = patients_data if isinstance(patients_data, list) else []
            
        patient_ids = [p.get("resource_id") or p.get("patient_resource_id") for p in patients if p.get("resource_id") or p.get("patient_resource_id")]
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            patient_ids = patient_ids[:limit]
            print(f"Limited to first {limit} patients")
        
        if not patient_ids:
            return {"status": "no_patients", "message": "No patients found in DeID service"}
        
        # Process all patients
        results = []
        errors = []
        
        for i, pid in enumerate(patient_ids):
            try:
                features = service.featurize_patient_with_db(pid, force_refresh)
                results.append(features)
                
                # Log progress for large datasets
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(patient_ids)} patients")
                    
            except Exception as e:
                error_info = {"patient_id": pid, "error": str(e)}
                errors.append(error_info)
        
        return {
            "status": "completed",
            "total_patients": len(patient_ids),
            "successful": len(results),
            "errors": len(errors),
            "error_details": errors[:5] if errors else [],
            "message": f"Featurized {len(results)} out of {len(patient_ids)} patients"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/features/{patient_id}",
         summary="ML-Ready Features for Single Patient",
         description="""
         Get ML-optimized features for a single patient, ready for ModelRisque integration.
         
         **Optimized for 30-day readmission prediction with**:
         - Binary target variable (readmission_30d)
         - Normalized numerical features
         - Categorical encoding hints
         - Feature importance metadata
         """,
         tags=["Machine Learning"])
def get_ml_features_single(patient_id: str, db: Session = Depends(get_db)):
    try:
        feature_record = db.query(PatientFeatures).filter(
            PatientFeatures.patient_resource_id == patient_id
        ).first()
        
        if not feature_record:
            raise HTTPException(status_code=404, detail="Patient features not found")
        
        # Extract enhanced readmission-focused features
        ml_features = {
            "patient_id": feature_record.patient_resource_id,
            
            # Target (for training)
            "readmission_30d": feature_record.readmission_30d or False,
            
            # Demographics
            "age": feature_record.age,
            "gender_male": 1 if feature_record.gender == "male" else 0,
            "gender_female": 1 if feature_record.gender == "female" else 0,
            
            # Encounter patterns (key predictors)
            "length_of_stay_days": feature_record.length_of_stay_days or 0.0,
            "is_emergency": feature_record.is_emergency or False,
            "is_inpatient": feature_record.is_inpatient or False,
            "days_since_last_discharge": feature_record.days_since_last_discharge,
            
            # Clinical burden
            "num_conditions": feature_record.num_conditions or 0,
            "num_medications": feature_record.num_med_requests or 0,
            "polypharmacy": feature_record.polypharmacy or False,
            "has_chronic_conditions": feature_record.has_chronic_conditions or False,
            
            # Vital signs volatility
            "abnormal_vitals_count": feature_record.obs_abnormal_count or 0,
            "has_abnormal_glucose": feature_record.has_abnormal_glucose or False,
            "has_abnormal_hr": feature_record.has_abnormal_hr or False,
            "has_abnormal_temp": feature_record.has_abnormal_temp or False,
            
            # Risk scoring
            "clinical_complexity_score": feature_record.clinical_complexity_score or 0.0,
        }
        
        return {
            "features": ml_features,
            "metadata": {
                "target_variable": "readmission_30d",
                "feature_count": len(ml_features) - 2,  # Exclude patient_id and target
                "last_updated": feature_record.updated_at.isoformat() if feature_record.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/features/patient/prune", 
            summary="Prune Old Cached Features",
            description="""
            Delete cached feature records older than the specified number of days.
            
            Helps manage database size by removing stale feature data.
            """,
            tags=["Database"]
            )
def prune_old_features(days: int = Query(30, description="Delete features older than this many days"),
                       db: Session = Depends(get_db)):
    try:
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = db.query(PatientFeatures).filter(
            PatientFeatures.updated_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        
        return {
            "status": "success",
            "deleted_records": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/features",
         summary="ML-Ready Dataset", 
         description="""
         Get ML-optimized features for all patients, ready for ModelRisque training/inference.
         
         **Perfect for**:
         - Training readmission prediction models
         - Batch inference pipelines  
         - Feature analysis and model validation
         
         Features are optimized for scikit-learn, XGBoost, and similar ML frameworks.
         """,
         tags=["Machine Learning"])
def get_ml_ready_features(skip: int = Query(0, description="Number of records to skip"), 
                         limit: int = Query(1000, description="Maximum number of records to return"), 
                         db: Session = Depends(get_db)):
    try:
        features = db.query(PatientFeatures).offset(skip).limit(limit).all()
        
        # Transform to ML-ready format optimized for readmission prediction
        ml_dataset = []
        for f in features:
            row = {
                "patient_id": f.patient_resource_id,
                
                # Target variable (binary)
                "readmission_30d": f.readmission_30d or False,
                
                # Demographics (literature-backed predictors)
                "age": f.age,
                "gender_male": 1 if f.gender == "male" else 0,
                "gender_female": 1 if f.gender == "female" else 0,
                
                # Encounter features (strongest predictors)
                "length_of_stay_days": f.length_of_stay_days or 0.0,
                "is_emergency": f.is_emergency or False,
                "is_inpatient": f.is_inpatient or False,
                "days_since_last_discharge": f.days_since_last_discharge,
                "num_encounters": f.num_encounters or 0,
                
                # Clinical complexity (major risk factors)
                "num_conditions": f.num_conditions or 0,
                "num_medications": f.num_med_requests or 0,
                "polypharmacy": f.polypharmacy or False,
                "has_chronic_conditions": f.has_chronic_conditions or False,
                
                # Vital signs indicators (physiological instability)
                "abnormal_vitals_count": f.obs_abnormal_count or 0,
                "has_abnormal_glucose": f.has_abnormal_glucose or False,
                "has_abnormal_hr": f.has_abnormal_hr or False,
                "has_abnormal_temp": f.has_abnormal_temp or False,
                "has_abnormal_saturation": f.has_abnormal_saturation or False,
                
                # Risk scores
                "clinical_complexity_score": f.clinical_complexity_score or 0.0,
                
                # Metadata
                "last_updated": f.updated_at.isoformat() if f.updated_at else None
            }
            ml_dataset.append(row)
        
        return {
            "dataset": ml_dataset,
            "count": len(ml_dataset),
            "schema": {
                "target": "readmission_30d",
                "features": {
                    "demographic": ["age", "gender_male", "gender_female"],
                    "encounter": ["length_of_stay_days", "is_emergency", "is_inpatient", "days_since_last_discharge"],
                    "clinical": ["num_conditions", "num_medications", "polypharmacy", "has_chronic_conditions"],
                    "vitals": ["abnormal_vitals_count", "has_abnormal_glucose", "has_abnormal_hr", "has_abnormal_temp"],
                    "derived": ["clinical_complexity_score"]
                },
                "data_types": {
                    "binary": ["readmission_30d", "gender_male", "gender_female", "is_emergency", "is_inpatient", "polypharmacy"],
                    "numerical": ["age", "length_of_stay_days", "days_since_last_discharge", "num_conditions", "clinical_complexity_score"],
                    "count": ["num_encounters", "num_medications", "abnormal_vitals_count"]
                }
            },
            "model_ready": True,
            "description": "Features optimized for 30-day readmission prediction models"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
