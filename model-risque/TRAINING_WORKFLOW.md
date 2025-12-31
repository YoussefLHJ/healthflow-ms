# Model Training & Deployment Workflow

## Quick Start Guide

### 1. Train the Model

Run the training notebook to train the XGBoost model:

```bash
# Open and run the notebook
cd model-risque/notebooks
jupyter notebook prediction_model_test.ipynb
```

**Important cells to run:**
1. Import libraries and connect to Featurizer API
2. Load training data (all patients with features)
3. Preprocess features (encode categoricals, handle missing values)
4. Train XGBoost model with hyperparameters
5. **Save model artifacts** (last cell - this saves the model for deployment)

The save cell will create:
- `trained_models/xgboost/readmission_model.pkl` - The trained XGBoost model
- `trained_models/metadata/feature_columns.json` - List of feature names in order
- `trained_models/metadata/model_metadata.json` - Model metrics and metadata

### 2. Start the ModelRisque Service

```bash
cd model-risque
uvicorn app.main:app --reload --port 8002
```

The service will automatically load the saved model on startup.

### 3. Test the Full Pipeline

```bash
# Test with default patient ID
python test_full_pipeline.py

# Or test with specific patient ID
python test_full_pipeline.py <patient-id>
```

This tests the complete flow:
- **ProxyFHIR** → Fetch patient FHIR bundle
- **DEID** → Anonymize patient data
- **Featurizer** → Extract/compute features
- **ModelRisque** → Predict readmission risk with SHAP explanations

## API Endpoints

### Health Check
```bash
GET http://localhost:8002/health
```

Returns:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1.0.0"
}
```

### Predict Readmission Risk
```bash
POST http://localhost:8002/predict
Content-Type: application/json

{
  "patient_resource_id": "2d0a99c4-1612-e78d-d540-3fbc42aecd07"
}
```

Response:
```json
{
  "patient_resource_id": "2d0a99c4-1612-e78d-d540-3fbc42aecd07",
  "readmission_risk_score": 0.456,
  "risk_category": "MEDIUM",
  "features_used": {
    "age": 65,
    "gender": "male",
    "num_encounters": 5,
    "length_of_stay_days": 3.5,
    ...
  },
  "shap_explanations": [
    {
      "feature_name": "num_encounters",
      "feature_value": 5,
      "shap_value": 0.123,
      "impact": "increases_risk"
    },
    ...
  ],
  "model_version": "v1.0.0"
}
```

### Train New Model (Hot-Swap)
```bash
POST http://localhost:8002/train
Content-Type: application/json

{
  "max_samples": 1000,
  "test_size": 0.2
}
```

This endpoint:
1. Fetches latest patient features from Featurizer
2. Trains a new XGBoost model
3. Saves the new model (bumps version)
4. Hot-swaps the model (no service restart needed)

## Model Retraining Workflow

When you have more data (aim for 100+ positive cases):

1. **Collect more patient data** through the pipeline
2. **Re-run the notebook** with updated data:
   - Adjust `num_of_data` parameter to fetch more samples
   - Train with the same workflow
   - Evaluate metrics (AUC, precision, recall)
3. **Update model version** in the save cell (e.g., v1.1.0)
4. **Save the new model** artifacts
5. **Restart ModelRisque service** or use `/train` endpoint

The service will automatically load the latest model version.

## Model Performance Monitoring

Check current model metrics:
```bash
GET http://localhost:8002/model/metrics
```

Returns:
```json
{
  "model_version": "v1.0.0",
  "accuracy": 0.85,
  "precision": 0.78,
  "recall": 0.82,
  "f1_score": 0.80,
  "auc_score": 0.88,
  "training_samples": 464,
  "test_samples": 116,
  "feature_count": 15,
  "training_date": "2025-12-10T10:30:00"
}
```

## Risk Categories

- **LOW** risk: score < 0.3
- **MEDIUM** risk: 0.3 ≤ score < 0.7
- **HIGH** risk: score ≥ 0.7

## SHAP Explanations

Each prediction includes SHAP (SHapley Additive exPlanations) values that explain:
- Which features contributed most to the prediction
- How much each feature increased or decreased the risk
- The actual values of those features for this patient

Example:
```
Feature: num_encounters = 5
SHAP value: +0.123
Impact: increases_risk
→ Patient's 5 prior encounters increased readmission risk by 0.123
```

## Dependencies

All required dependencies are in `requirements.txt`:
- **xgboost**: XGBoost model
- **scikit-learn**: Data preprocessing and metrics
- **shap**: Model interpretability
- **pandas/numpy**: Data manipulation
- **fastapi/uvicorn**: Web API framework
- **joblib**: Model serialization

## Troubleshooting

### Model not loaded
- Make sure you ran the notebook save cell
- Check that files exist in `trained_models/` directory
- Restart the service

### Patient not found in Featurizer
- Ensure patient data was ingested through ProxyFHIR → DEID → Featurizer pipeline
- Check Featurizer database: `GET http://localhost:8001/features/patient/{patient_id}`

### Prediction fails
- Verify model is loaded: `GET http://localhost:8002/health`
- Check Featurizer is running: `GET http://localhost:8001/health`
- Ensure feature schema matches between training and prediction

## Next Steps

1. ✅ Train model with notebook
2. ✅ Save model artifacts
3. ✅ Start ModelRisque service
4. ✅ Test full pipeline
5. 🔄 Collect more patient data
6. 🔄 Retrain with 100+ positive cases
7. 🔄 Monitor model performance
8. 🔄 Set up automated retraining pipeline
