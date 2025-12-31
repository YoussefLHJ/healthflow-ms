-- ModelRisque database schema
-- This creates tables for storing patient features and model metadata

CREATE TABLE IF NOT EXISTS patient_features (
    id SERIAL PRIMARY KEY,
    patient_resource_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Target Variable
    readmission_30d BOOLEAN DEFAULT FALSE,
    
    -- Demographics
    gender VARCHAR(50),
    age FLOAT,
    state VARCHAR(100),
    
    -- Encounter Features
    num_encounters INTEGER DEFAULT 0,
    length_of_stay_days FLOAT DEFAULT 0.0,
    avg_los FLOAT DEFAULT 0.0,
    is_emergency BOOLEAN DEFAULT FALSE,
    is_inpatient BOOLEAN DEFAULT FALSE,
    days_since_last_discharge INTEGER,
    
    -- Condition Features
    num_conditions INTEGER DEFAULT 0,
    has_chronic_conditions BOOLEAN DEFAULT FALSE,
    
    -- Observation Features
    num_observations INTEGER DEFAULT 0,
    obs_abnormal_count INTEGER DEFAULT 0,
    has_abnormal_glucose BOOLEAN DEFAULT FALSE,
    has_abnormal_hr BOOLEAN DEFAULT FALSE,
    has_abnormal_temp BOOLEAN DEFAULT FALSE,
    has_abnormal_saturation BOOLEAN DEFAULT FALSE,
    vital_signs_available BOOLEAN DEFAULT FALSE,
    
    -- Medication/Procedure Features
    num_med_requests INTEGER DEFAULT 0,
    num_procedures INTEGER DEFAULT 0,
    polypharmacy BOOLEAN DEFAULT FALSE,
    
    -- Risk Indicators
    has_multiple_encounters BOOLEAN DEFAULT FALSE,
    has_long_stay BOOLEAN DEFAULT FALSE,
    high_med_burden BOOLEAN DEFAULT FALSE,
    high_condition_count BOOLEAN DEFAULT FALSE,
    has_abnormal_labs BOOLEAN DEFAULT FALSE,
    clinical_complexity_score FLOAT DEFAULT 0.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS ix_patient_features_patient_resource_id 
ON patient_features(patient_resource_id);

CREATE INDEX IF NOT EXISTS ix_patient_features_readmission_30d 
ON patient_features(readmission_30d);

-- Model metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL DEFAULT 'xgboost',
    accuracy FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    auc_score FLOAT,
    training_samples INTEGER,
    test_samples INTEGER,
    feature_count INTEGER,
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Predictions log table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    patient_resource_id VARCHAR(255) NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_category VARCHAR(10) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    features_used JSONB,
    shap_explanations JSONB,
    prediction_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_predictions_patient_resource_id 
ON predictions(patient_resource_id);

CREATE INDEX IF NOT EXISTS ix_predictions_timestamp 
ON predictions(prediction_timestamp);