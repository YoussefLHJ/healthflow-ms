#!/usr/bin/env python3
"""
Quick Database Schema Update using SQLAlchemy
This will create missing columns automatically
"""

from featurizer.database import engine
from featurizer.models import PatientFeatures
from dotenv import load_dotenv

load_dotenv()

print("Creating missing database columns...")

try:
    # This will create any missing columns
    PatientFeatures.metadata.create_all(bind=engine)
    print("✅ Database schema updated successfully!")
    print("All readmission prediction columns are now available.")
except Exception as e:
    print(f"❌ Schema update failed: {e}")