from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.deid_routes import router as deid_router
from app.db.session import engine
from app.db.base import Base
from contextlib import asynccontextmanager
import py_eureka_client.eureka_client as eureka_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup: Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Startup: Register with Eureka when FastAPI starts
    await eureka_client.init_async(
        eureka_server="http://localhost:8761/eureka",
        app_name="DEID-SERVICE",
        instance_port=8000,
        instance_host="localhost",
        instance_ip="127.0.0.1"
    )
    print("✓ DeID service registered with Eureka")
    
    yield  # Application runs here
    
    # Shutdown: Unregister when FastAPI stops
    await eureka_client.stop_async()
    print("✓ DeID service unregistered from Eureka")

app = FastAPI(
    title="FHIR De-Identification Service",
    description="Anonymizes personal and sensitive data from FHIR resources before downstream processing",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router)
app.include_router(deid_router)

@app.get("/")
def read_root():
    return {
        "message": "FHIR De-Identification Microservice",
        "description": "Anonymizes PII from FHIR data using Faker and PostgreSQL",
        "critical_resources": [
            "Patient", "Encounter", "Condition", "Observation", 
            "MedicationRequest", "Procedure", "DiagnosticReport",
            "DocumentReference", "AllergyIntolerance", "Immunization",
            "Practitioner", "PractitionerRole", "Organization"
        ],
        "endpoints": {
            "ingest": "POST /deid/ingest - Fetch, de-identify, and store all critical FHIR resources",
            "patients": "GET /deid/patients",
            "encounters": "GET /deid/encounters",
            "conditions": "GET /deid/conditions",
            "observations": "GET /deid/observations",
            "medications": "GET /deid/medication-requests",
            "procedures": "GET /deid/procedures",
            "reports": "GET /deid/diagnostic-reports",
            "documents": "GET /deid/document-references",
            "allergies": "GET /deid/allergy-intolerances",
            "immunizations": "GET /deid/immunizations",
            "practitioners": "GET /deid/practitioners",
            "roles": "GET /deid/practitioner-roles",
            "organizations": "GET /deid/organizations",
        }
    }