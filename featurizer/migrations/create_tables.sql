-- Complete patient_features table schema
-- Updated to match the current PatientFeatures model

CREATE TABLE IF NOT EXISTS patient_features (
    id SERIAL PRIMARY KEY,
    patient_resource_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Target variable for readmission prediction
    readmission_30d BOOLEAN DEFAULT FALSE,
    
    -- Patient demographics
    gender VARCHAR(50),
    birth_date VARCHAR(50),
    age INTEGER,
    state VARCHAR(100),
    
    -- Encounter features
    num_encounters INTEGER DEFAULT 0,
    length_of_stay_days INTEGER DEFAULT 0,
    avg_los FLOAT DEFAULT 0.0,
    class_code VARCHAR(100),
    type_code VARCHAR(100),
    is_emergency BOOLEAN DEFAULT FALSE,
    is_inpatient BOOLEAN DEFAULT FALSE,
    days_since_last_discharge INTEGER,
    
    -- Condition features
    num_conditions INTEGER DEFAULT 0,
    primary_condition_code VARCHAR(200),
    primary_condition_display TEXT,
    has_chronic_conditions BOOLEAN DEFAULT FALSE,
    condition_codes JSONB,
    
    -- Observation features  
    num_observations INTEGER DEFAULT 0,
    obs_abnormal_count INTEGER DEFAULT 0,
    has_abnormal_glucose BOOLEAN DEFAULT FALSE,
    has_abnormal_hr BOOLEAN DEFAULT FALSE,
    has_abnormal_temp BOOLEAN DEFAULT FALSE,
    has_abnormal_saturation BOOLEAN DEFAULT FALSE,
    vital_signs_available BOOLEAN DEFAULT FALSE,
    
    -- Medication features
    num_med_requests INTEGER DEFAULT 0,
    num_procedures INTEGER DEFAULT 0,
    polypharmacy BOOLEAN DEFAULT FALSE,
    medication_codes JSONB,
    
    -- NLP features
    ner_entities JSONB,
    embedding_mean JSONB,
    
    -- Risk indicators for readmission prediction
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

CREATE INDEX IF NOT EXISTS ix_patient_features_id 
ON patient_features(id);

CREATE INDEX IF NOT EXISTS ix_patient_features_readmission_30d 
ON patient_features(readmission_30d);

CREATE INDEX IF NOT EXISTS ix_patient_features_age 
ON patient_features(age);

CREATE INDEX IF NOT EXISTS ix_patient_features_num_encounters 
ON patient_features(num_encounters);