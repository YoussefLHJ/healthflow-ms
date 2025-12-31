# ModelRisque - Readmission Risk Prediction Service

## Overview
ModelRisque is a machine learning microservice that predicts 30-day hospital readmission risk using XGBoost and provides SHAP explanations for model interpretability.

## Features
- **XGBoost Model**: Trained on patient features extracted from FHIR data
- **SHAP Explanations**: Interpretable AI with feature importance explanations
- **Risk Scoring**: Probability scores (0-1) with LOW/MEDIUM/HIGH categories  
- **FastAPI**: RESTful API with automatic OpenAPI documentation
- **PostgreSQL Integration**: Connects to featurizer database for patient features
- **Docker Support**: Containerized deployment with health checks

## Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FHIR Data     │───▶│   Featurizer     │───▶│   ModelRisque   │
│                 │    │  (Feature        │    │ (Risk Prediction│
│                 │    │   Extraction)    │    │  + SHAP)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## API Endpoints

### Core Prediction
- `POST /predict` - Predict readmission risk for a patient by ID
- `POST /predict/custom` - Predict using custom feature values
- `GET /features/patient/{patient_id}` - Get patient features

### Model Management  
- `POST /train` - Train new XGBoost model
- `GET /model/metrics` - Get model performance metrics
- `GET /features/stats` - Database statistics

### Health & Monitoring
- `GET /health` - Service health check
- `GET /` - Service information

## Quick Start

### 1. Build and Run
```bash
cd model-risque
docker-compose up --build -d
```

### 2. Train Initial Model
```bash
curl -X POST http://localhost:8002/train \
  -H "Content-Type: application/json" \
  -d '{"max_samples": 1000, "test_size": 0.2}'
```

### 3. Make Predictions
```bash
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"patient_resource_id": "patient-123"}'
```

## Model Features
The model uses 25+ features extracted from FHIR data:

### Demographics
- `age` - Patient age
- `gender` - Gender (encoded)
- `state` - Location (encoded)

### Encounter Features
- `num_encounters` - Total encounters
- `length_of_stay_days` - Recent LOS
- `avg_los` - Average length of stay
- `is_emergency` - Emergency admission flag
- `is_inpatient` - Inpatient flag
- `days_since_last_discharge` - Time since discharge

### Clinical Complexity
- `num_conditions` - Number of conditions
- `has_chronic_conditions` - Chronic disease flag
- `num_observations` - Lab/vital observations
- `obs_abnormal_count` - Abnormal results
- `clinical_complexity_score` - Composite risk score

### And more... (see database schema for complete list)

## Response Example
```json
{
  "patient_resource_id": "patient-123",
  "readmission_risk_score": 0.72,
  "risk_category": "HIGH", 
  "features_used": {
    "age": 65,
    "num_encounters": 8,
    "has_chronic_conditions": true,
    "length_of_stay_days": 12.5
  },
  "shap_explanations": [
    {
      "feature_name": "length_of_stay_days",
      "feature_value": 12.5,
      "shap_value": 0.15,
      "impact": "increases_risk"
    },
    {
      "feature_name": "age", 
      "feature_value": 65,
      "shap_value": 0.08,
      "impact": "increases_risk"
    }
  ],
  "model_version": "v1.0.0",
  "prediction_timestamp": "2024-12-04T..."
}
```

## Configuration
Environment variables:
- `FEATURIZER_DB_URL` - PostgreSQL connection
- `FEATURIZER_API_URL` - Featurizer service URL  
- `MODEL_PATH` - XGBoost model file path
- `SCALER_PATH` - Feature scaler path

## Integration
ModelRisque integrates with:
- **Featurizer Service**: Reads patient features from PostgreSQL
- **DeID Service**: Can receive de-identified patient data
- **Shared Network**: Uses `healthcare_network` for service discovery

## Performance
- Training time: ~30 seconds for 1000 samples
- Prediction latency: <100ms
- Model accuracy: Typically 85%+ on balanced datasets
- Memory usage: ~512MB with loaded XGBoost model

## Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires database)
uvicorn app.main:app --reload --port 8002

# Run tests
pytest tests/
```

## Monitoring
- Health endpoint: `/health`
- Model metrics: `/model/metrics` 
- Feature stats: `/features/stats`
- Logs: Structured logging with patient IDs