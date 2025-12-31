from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import py_eureka_client.eureka_client as eureka_client

from app.core.config import settings
from app.core.db import Base, engine
from app.api.v1.fairness_router import router as fairness_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    Base.metadata.create_all(bind=engine)

    # Startup: register with Eureka (note instance_host/ip)
    await eureka_client.init_async(
        eureka_server="http://localhost:8761/eureka",
        app_name="AUDIT-FAIRNESS",
        instance_port=8100,
        instance_host="localhost",
        instance_ip="127.0.0.1",
    )
    print("✓ Audit Fairness service registered with Eureka")

    yield  # app runs

    # Shutdown: unregister
    await eureka_client.stop_async()
    print("✓ Audit Fairness service unregistered from Eureka")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fairness_router, prefix=settings.API_V1_PREFIX)
