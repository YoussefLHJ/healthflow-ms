import datetime
import os
import logging
from typing import Dict, Any, List
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx
import py_eureka_client.eureka_client as eureka_client

# Local imports
from app.models.database import get_db, PatientFeatures, Prediction, init_db
from app.models.schemas import (
    PredictionRequest, PredictionResponse, FeatureVector,
    TrainingRequest, TrainingResponse, ModelMetrics
)
from app.services.model_service import ModelService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_risque")

# Global model service instance
model_service = ModelService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    logger.info("Starting ModelRisque service...")
    
    # Initialize database tables
    try:
        init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    # Try to load existing model
    if not model_service.load_model():
        logger.info("No pre-trained model found. Train a model using /train endpoint.")
    
    # Register with Eureka
    await eureka_client.init_async(
        eureka_server="http://localhost:8761/eureka",
        app_name="MODEL-RISQUE",
        instance_port=int(os.getenv("PORT", 8002)),
        instance_host="localhost",
        instance_ip="127.0.0.1"
    )
    logger.info("✓ ModelRisque service registered with Eureka")
    
    yield
    
    # Shutdown: Unregister from Eureka
    await eureka_client.stop_async()
    logger.info("✓ ModelRisque service unregistered from Eureka")
    logger.info("Shutting down ModelRisque service...")

# Create FastAPI application
app = FastAPI(
    title="ModelRisque - Readmission Risk Prediction Service",
    description="XGBoost-based service for predicting 30-day hospital readmission risk with SHAP explanations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ModelRisque",
        "version": "1.0.0",
        "description": "XGBoost-based readmission risk prediction with SHAP explanations"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = model_service.model is not None
    return {
        "status": "healthy",
        "model_loaded": model_loaded,
        "model_version": model_service.model_version if model_loaded else "none"
    }

@app.post("/prediction/data")
async def predict_data(
    skip_cache: bool = False,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Batch predict 30-day readmission risk for all featurized patients and save to DB"""
    
    if not model_service.model:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train a model first using /train endpoint."
        )
    
    predictions = {}
    featurizer_api_url = os.getenv("FEATURIZER_API_URL", "http://localhost:8001")
    
    try:
        # Fetch all patients from featurizer service using /features/all
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{featurizer_api_url}/features/all",
                params={"skip": 0, "limit": limit}
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to fetch patients from featurizer: {response.status_code}"
                )
            featurizer_data = response.json()
            patients = featurizer_data.get("rows", [])
            if not patients:
                return {
                    "message": "No patients found in featurizer database",
                    "total_processed": 0,
                    "predictions": {}
                }
            logger.info(f"Fetched {len(patients)} patients from featurizer")

        # Process each patient
        success_count = 0
        error_count = 0
        for patient_data in patients:
            patient_id = patient_data.get("patient_resource_id")
            try:
                # Check if prediction already exists in database (skip cache if requested)
                if not skip_cache:
                    existing_prediction = db.query(Prediction).filter(
                        Prediction.patient_resource_id == patient_id
                    ).order_by(Prediction.prediction_timestamp.desc()).first()
                    # If recent prediction exists (within last 24 hours), use cached
                    if existing_prediction:
                        time_since_prediction = datetime.now(timezone.utc) - existing_prediction.prediction_timestamp
                        if time_since_prediction.total_seconds() < 86400:  # 24 hours
                            logger.info(f"Using cached prediction for patient {patient_id}")
                            predictions[patient_id] = {
                                "patient_resource_id": existing_prediction.patient_resource_id,
                                "readmission_risk_score": existing_prediction.readmission_risk_score,
                                "risk_category": existing_prediction.risk_category,
                                "model_version": existing_prediction.model_version,
                                "prediction_timestamp": existing_prediction.prediction_timestamp.isoformat(),
                                "cached": True
                            }
                            success_count += 1
                            continue
                # Convert to feature vector
                features = FeatureVector(**patient_data)
                # Make prediction
                risk_score, features_used, shap_explanations = model_service.predict(features)
                # Determine risk category
                if risk_score < 0.3:
                    risk_category = "LOW"
                elif risk_score < 0.7:
                    risk_category = "MEDIUM"
                else:
                    risk_category = "HIGH"
                # Save to database
                db_prediction = Prediction(
                    patient_resource_id=patient_id,
                    readmission_risk_score=risk_score,
                    risk_category=risk_category,
                    features_used=features_used,
                    shap_explanations=[exp.dict() if hasattr(exp, 'dict') else exp for exp in shap_explanations],
                    model_version=model_service.model_version,
                    prediction_timestamp=datetime.now(timezone.utc)
                )
                db.add(db_prediction)
                db.commit()
                db.refresh(db_prediction)
                logger.info(f"Saved new prediction for patient {patient_id}")
                predictions[patient_id] = {
                    "patient_resource_id": patient_id,
                    "readmission_risk_score": risk_score,
                    "risk_category": risk_category,
                    "model_version": model_service.model_version,
                    "prediction_timestamp": db_prediction.prediction_timestamp.isoformat(),
                    "cached": False
                }
                success_count += 1
            except Exception as e:
                logger.error(f"Prediction failed for patient {patient_id}: {str(e)}")
                predictions[patient_id] = {"error": f"Prediction failed: {str(e)}"}
                error_count += 1
                db.rollback()
        return {
            "message": f"Processed {len(patients)} patients",
            "total_processed": len(patients),
            "successful": success_count,
            "failed": error_count,
            "predictions": predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/predictions/patient/{patient_resource_id}", response_model=PredictionResponse)
async def get_patient_prediction(
    patient_resource_id: str,
    db: Session = Depends(get_db)
):
    """Get latest cached prediction for a patient"""
    prediction = db.query(Prediction).filter(
        Prediction.patient_resource_id == patient_resource_id
    ).order_by(Prediction.prediction_timestamp.desc()).first()
    
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail=f"No prediction found for patient {patient_resource_id}"
        )
    
    return PredictionResponse(
        patient_resource_id=prediction.patient_resource_id,
        readmission_risk_score=prediction.readmission_risk_score,
        risk_category=prediction.risk_category,
        features_used=prediction.features_used,
        shap_explanations=prediction.shap_explanations,
        model_version=prediction.model_version,
        prediction_timestamp=prediction.prediction_timestamp
    )


@app.get("/predictions/all", response_model=List[PredictionResponse])
async def get_all_predictions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all cached predictions (paginated)"""
    predictions = db.query(Prediction).order_by(
        Prediction.prediction_timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        PredictionResponse(
            patient_resource_id=p.patient_resource_id,
            readmission_risk_score=p.readmission_risk_score,
            risk_category=p.risk_category,
            features_used=p.features_used,
            shap_explanations=p.shap_explanations,
            model_version=p.model_version,
            prediction_timestamp=p.prediction_timestamp
        )
        for p in predictions
    ]


@app.delete("/predictions/clear")
async def clear_predictions(db: Session = Depends(get_db)):
    """Clear all cached predictions"""
    deleted_count = db.query(Prediction).delete()
    db.commit()
    return {"message": f"Deleted {deleted_count} predictions"}

    
@app.post("/predict", response_model=PredictionResponse)
async def predict_readmission(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """Predict 30-day readmission risk for a patient"""
    try:
        # Get patient features from featurizer API
        featurizer_api_url = os.getenv("FEATURIZER_API_URL", "http://featurizer:8001")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{featurizer_api_url}/features/patient/{request.patient_resource_id}")
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Patient {request.patient_resource_id} not found in featurizer database"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to fetch patient features: {response.status_code}"
                )
            
            patient_data = response.json()
        
        # Convert to feature vector
        features = FeatureVector(**patient_data)
        
        # Make prediction
        risk_score, features_used, shap_explanations = model_service.predict(features)
        
        # Determine risk category
        if risk_score < 0.3:
            risk_category = "LOW"
        elif risk_score < 0.7:
            risk_category = "MEDIUM"
        else:
            risk_category = "HIGH"
        
        # Log prediction to local database
        prediction_log = {
            "patient_resource_id": request.patient_resource_id,
            "risk_score": risk_score,
            "risk_category": risk_category,
            "model_version": model_service.model_version,
            "features_used": features_used,
            "shap_explanations": [exp.dict() for exp in shap_explanations]
        }
        
        return PredictionResponse(
            patient_resource_id=request.patient_resource_id,
            readmission_risk_score=risk_score,
            risk_category=risk_category,
            features_used=features_used,
            shap_explanations=shap_explanations,
            model_version=model_service.model_version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/custom", response_model=PredictionResponse)
async def predict_custom_features(features: FeatureVector):
    """Predict readmission risk using custom feature values"""
    try:
        if not model_service.model:
            raise HTTPException(
                status_code=503, 
                detail="Model not loaded. Please train a model first using /train endpoint."
            )
        
        # Make prediction
        risk_score, features_used, shap_explanations = model_service.predict(features)
        
        # Determine risk category
        if risk_score < 0.3:
            risk_category = "LOW"
        elif risk_score < 0.7:
            risk_category = "MEDIUM"
        else:
            risk_category = "HIGH"
        
        return PredictionResponse(
            patient_resource_id="custom_features",
            readmission_risk_score=risk_score,
            risk_category=risk_category,
            features_used=features_used,
            shap_explanations=shap_explanations,
            model_version=model_service.model_version
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/generate-test-data")
async def generate_test_data(
    count: int = 100,
    db: Session = Depends(get_db)
):
    """Generate test patient data for training"""
    import random
    import uuid
    
    try:
        # Generate synthetic patient data
        for i in range(count):
            patient = PatientFeatures(
                patient_resource_id=f"test-patient-{uuid.uuid4().hex[:8]}",
                readmission_30d=random.choice([True, False]),
                gender=random.choice(['male', 'female']),
                age=random.uniform(18, 90),
                state=random.choice(['CA', 'NY', 'TX', 'FL', 'IL']),
                num_encounters=random.randint(1, 10),
                length_of_stay_days=random.uniform(1, 30),
                avg_los=random.uniform(1, 15),
                is_emergency=random.choice([True, False]),
                is_inpatient=random.choice([True, False]),
                days_since_last_discharge=random.randint(1, 365) if random.choice([True, False]) else None,
                num_conditions=random.randint(0, 15),
                has_chronic_conditions=random.choice([True, False]),
                num_observations=random.randint(0, 50),
                obs_abnormal_count=random.randint(0, 20),
                has_abnormal_glucose=random.choice([True, False]),
                has_abnormal_hr=random.choice([True, False]),
                has_abnormal_temp=random.choice([True, False]),
                has_abnormal_saturation=random.choice([True, False]),
                vital_signs_available=random.choice([True, False]),
                num_med_requests=random.randint(0, 20),
                num_procedures=random.randint(0, 10),
                polypharmacy=random.choice([True, False]),
                has_multiple_encounters=random.choice([True, False]),
                has_long_stay=random.choice([True, False]),
                high_med_burden=random.choice([True, False]),
                high_condition_count=random.choice([True, False]),
                has_abnormal_labs=random.choice([True, False]),
                clinical_complexity_score=random.uniform(0, 1)
            )
            db.add(patient)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Generated {count} test patients",
            "total_patients": count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to generate test data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate test data: {str(e)}")


@app.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Train a new readmission prediction model"""
    try:
        logger.info(f"Starting model training with parameters: {request.dict()}")
        
        # Get featurizer API URL
        featurizer_api_url = os.getenv("FEATURIZER_API_URL", "http://localhost:8001")
        
        # Run training
        response = model_service.train_model(
            db=db,
            featurizer_api_url=featurizer_api_url,
            max_samples=request.max_samples,
            test_size=request.test_size,
            random_state=request.random_state
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.get("/model/metrics", response_model=ModelMetrics)
async def get_model_metrics():
    """Get current model performance metrics"""
    try:
        metrics = model_service.get_model_metrics()
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail="No trained model found. Train a model first using /train endpoint."
            )
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get model metrics: {str(e)}")


@app.get("/features/patient/{patient_id}")
async def get_patient_features(patient_id: str, db: Session = Depends(get_db)):
    """Get extracted features for a specific patient"""
    try:
        patient = db.query(PatientFeatures).filter(
            PatientFeatures.patient_resource_id == patient_id
        ).first()
        
        if not patient:
            raise HTTPException(
                status_code=404,
                detail=f"Patient {patient_id} not found in features database"
            )
        
        return {
            "patient_resource_id": patient.patient_resource_id,
            "readmission_30d": patient.readmission_30d,
            "age": patient.age,
            "gender": patient.gender,
            "state": patient.state,
            "num_encounters": patient.num_encounters,
            "length_of_stay_days": patient.length_of_stay_days,
            "avg_los": patient.avg_los,
            "is_emergency": patient.is_emergency,
            "is_inpatient": patient.is_inpatient,
            "days_since_last_discharge": patient.days_since_last_discharge,
            "num_conditions": patient.num_conditions,
            "has_chronic_conditions": patient.has_chronic_conditions,
            "num_observations": patient.num_observations,
            "obs_abnormal_count": patient.obs_abnormal_count,
            "has_abnormal_glucose": patient.has_abnormal_glucose,
            "has_abnormal_hr": patient.has_abnormal_hr,
            "has_abnormal_temp": patient.has_abnormal_temp,
            "has_abnormal_saturation": patient.has_abnormal_saturation,
            "vital_signs_available": patient.vital_signs_available,
            "num_med_requests": patient.num_med_requests,
            "num_procedures": patient.num_procedures,
            "polypharmacy": patient.polypharmacy,
            "has_multiple_encounters": patient.has_multiple_encounters,
            "has_long_stay": patient.has_long_stay,
            "high_med_burden": patient.high_med_burden,
            "high_condition_count": patient.high_condition_count,
            "has_abnormal_labs": patient.has_abnormal_labs,
            "clinical_complexity_score": patient.clinical_complexity_score,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get patient features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get patient features: {str(e)}")


@app.get("/features/stats")
async def get_feature_statistics(db: Session = Depends(get_db)):
    """Get statistics about the feature database"""
    try:
        total_patients = db.query(PatientFeatures).count()
        
        if total_patients == 0:
            return {
                "total_patients": 0,
                "readmission_rate": 0.0,
                "message": "No patient features found in database"
            }
        
        readmissions = db.query(PatientFeatures).filter(
            PatientFeatures.readmission_30d == True
        ).count()
        
        readmission_rate = readmissions / total_patients if total_patients > 0 else 0.0
        
        return {
            "total_patients": total_patients,
            "patients_with_readmission": readmissions,
            "readmission_rate": readmission_rate,
            "model_ready": total_patients >= 10
        }
        
    except Exception as e:
        logger.error(f"Failed to get feature statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature statistics: {str(e)}")

@app.delete("/model/patients/prune")
async def prune_patient_data(
    db: Session = Depends(get_db)
):
    """Prune patient feature data older than the specified number of days"""
    try:
        
        
        deleted_count = db.query(PatientFeatures).delete()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Pruned {deleted_count} patient records from feature database",
            "total_deleted": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to prune patient data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to prune patient data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)