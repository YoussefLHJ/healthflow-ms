#!/usr/bin/env python3
"""
Database Migration Script - Add Readmission Prediction Features
Run this to update the database schema with new columns for readmission prediction
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:root@localhost:5432/featDB')
    
    # SQL to add missing columns
    migration_sql = """
    -- Add readmission prediction columns to patient_features table
    ALTER TABLE patient_features 
    ADD COLUMN IF NOT EXISTS readmission_30d BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS age DECIMAL(5,2),
    ADD COLUMN IF NOT EXISTS length_of_stay_days DECIMAL(8,2) DEFAULT 0.0,
    ADD COLUMN IF NOT EXISTS class_code VARCHAR(50),
    ADD COLUMN IF NOT EXISTS type_code VARCHAR(50),
    ADD COLUMN IF NOT EXISTS is_emergency BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS is_inpatient BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS days_since_last_discharge INTEGER,
    ADD COLUMN IF NOT EXISTS primary_condition_code VARCHAR(50),
    ADD COLUMN IF NOT EXISTS primary_condition_display VARCHAR(255),
    ADD COLUMN IF NOT EXISTS has_chronic_conditions BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS condition_codes JSON,
    ADD COLUMN IF NOT EXISTS num_observations INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS has_abnormal_glucose BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS has_abnormal_hr BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS has_abnormal_temp BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS has_abnormal_saturation BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS vital_signs_available BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS num_procedures INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS polypharmacy BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS medication_codes JSON;
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_patient_features_readmission ON patient_features(readmission_30d);
    CREATE INDEX IF NOT EXISTS idx_patient_features_age ON patient_features(age);
    CREATE INDEX IF NOT EXISTS idx_patient_features_emergency ON patient_features(is_emergency);
    """
    
    try:
        # Connect to database
        print(f"Connecting to database: {DATABASE_URL.split('@')[1]}")  # Hide password in output
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Applying migration...")
        cur.execute(migration_sql)
        conn.commit()
        
        print("✅ Migration applied successfully!")
        print("Database now supports readmission prediction features")
        
        # Verify columns were added
        cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'patient_features' 
        AND column_name IN ('readmission_30d', 'age', 'length_of_stay_days', 'polypharmacy')
        ORDER BY column_name;
        """)
        
        new_columns = cur.fetchall()
        print(f"\n✅ Verified {len(new_columns)} new columns:")
        for col_name, col_type in new_columns:
            print(f"  - {col_name}: {col_type}")
            
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()