from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Audit Fairness Service"
    API_V1_PREFIX: str = "/api/v1"

    POSTGRES_URL: str = "postgresql+psycopg2://postgres:root@localhost:5432/auditfairness"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    SCORE_API_BASE: str = "http://localhost:8888/api"  # default

    class Config:
        env_file = ".env"

settings = Settings()
