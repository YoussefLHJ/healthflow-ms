-- Migration to add readmission risk features
-- Run this after the initial table creation

ALTER TABLE patient_features 
ADD COLUMN IF NOT EXISTS has_multiple_encounters BOOLEAN DEFAULT FALSE;

ALTER TABLE patient_features 
ADD COLUMN IF NOT EXISTS has_long_stay BOOLEAN DEFAULT FALSE;

ALTER TABLE patient_features 
ADD COLUMN IF NOT EXISTS high_med_burden BOOLEAN DEFAULT FALSE;

ALTER TABLE patient_features 
ADD COLUMN IF NOT EXISTS high_condition_count BOOLEAN DEFAULT FALSE;

ALTER TABLE patient_features 
ADD COLUMN IF NOT EXISTS has_abnormal_labs BOOLEAN DEFAULT FALSE;

ALTER TABLE patient_features 
ADD COLUMN IF NOT EXISTS clinical_complexity_score FLOAT DEFAULT 0.0;

-- Create index for ML queries
CREATE INDEX IF NOT EXISTS ix_patient_features_complexity 
ON patient_features(clinical_complexity_score);

CREATE INDEX IF NOT EXISTS ix_patient_features_risk_indicators 
ON patient_features(has_multiple_encounters, has_long_stay, high_med_burden);