-- Migration 003: Add readmission prediction features to PatientFeatures table
-- Adds target variable and essential features for 30-day readmission prediction

ALTER TABLE featDB.patient_features 
-- Target Variable
ADD COLUMN readmission_30d BOOLEAN DEFAULT FALSE,

-- Enhanced Demographics
ADD COLUMN age DECIMAL(5,2),

-- Enhanced Encounter Features
ADD COLUMN length_of_stay_days DECIMAL(8,2) DEFAULT 0.0,
ADD COLUMN class_code VARCHAR(50),
ADD COLUMN type_code VARCHAR(50),
ADD COLUMN is_emergency BOOLEAN DEFAULT FALSE,
ADD COLUMN is_inpatient BOOLEAN DEFAULT FALSE,
ADD COLUMN days_since_last_discharge INTEGER,

-- Condition Features  
ADD COLUMN primary_condition_code VARCHAR(50),
ADD COLUMN primary_condition_display VARCHAR(255),
ADD COLUMN has_chronic_conditions BOOLEAN DEFAULT FALSE,
ADD COLUMN condition_codes JSON,

-- Enhanced Observation Features
ADD COLUMN num_observations INTEGER DEFAULT 0,
ADD COLUMN has_abnormal_glucose BOOLEAN DEFAULT FALSE,
ADD COLUMN has_abnormal_hr BOOLEAN DEFAULT FALSE,
ADD COLUMN has_abnormal_temp BOOLEAN DEFAULT FALSE,
ADD COLUMN has_abnormal_saturation BOOLEAN DEFAULT FALSE,
ADD COLUMN vital_signs_available BOOLEAN DEFAULT FALSE,

-- Medication/Procedure Features
ADD COLUMN num_procedures INTEGER DEFAULT 0,
ADD COLUMN polypharmacy BOOLEAN DEFAULT FALSE,
ADD COLUMN medication_codes JSON;

-- Create indexes for query optimization
CREATE INDEX idx_patient_features_readmission ON featDB.patient_features(readmission_30d);
CREATE INDEX idx_patient_features_class_code ON featDB.patient_features(class_code);
CREATE INDEX idx_patient_features_is_emergency ON featDB.patient_features(is_emergency);
CREATE INDEX idx_patient_features_is_inpatient ON featDB.patient_features(is_inpatient);
CREATE INDEX idx_patient_features_age ON featDB.patient_features(age);
CREATE INDEX idx_patient_features_polypharmacy ON featDB.patient_features(polypharmacy);

-- Add comments for documentation
COMMENT ON COLUMN featDB.patient_features.readmission_30d IS 'Target: Binary indicator for 30-day unplanned readmission';
COMMENT ON COLUMN featDB.patient_features.age IS 'Patient age computed from birth_date';
COMMENT ON COLUMN featDB.patient_features.class_code IS 'Encounter class: EMER, IMP, AMB';
COMMENT ON COLUMN featDB.patient_features.polypharmacy IS 'TRUE if patient has >= 5 medications';
COMMENT ON COLUMN featDB.patient_features.condition_codes IS 'JSON array of condition codes and displays';
COMMENT ON COLUMN featDB.patient_features.medication_codes IS 'JSON array of medication codes and displays';