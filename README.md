# HealthFlow

HealthFlow is a multi-service healthcare-data prototype. The repository combines Java/Spring and Python services with PostgreSQL-backed components and a Next.js clinical dashboard.

## Architecture

```text
Synthea sample data -> ProxyFHIR -> deid-microservice -> featurizer -> model-risque
                                             |                         |
                                             +------> Score API <-------+
                                                           |
                                                AuditFairness service
                                                           |
                                                clinical dashboard
```

Docker Compose defines the service network and the service-specific PostgreSQL databases. The diagram describes configured dependencies, not a production deployment.

## Services

| Component | Role evidenced in this repository |
| --- | --- |
| `ProxyFHIR` | Spring-based FHIR proxy and sample-data import component |
| `deid-microservice` | Python de-identification service |
| `featurizer` | Python feature-preparation service |
| `model-risque` | Python risk-model service with repository-resident model assets |
| `ScoreAPI` | Score API service |
| `AuditFairness-microservice` | FastAPI fairness-audit service |
| `clinical-dashboard-build` | Next.js clinical dashboard |

## Technology

Java, Spring Boot, Python, FastAPI, PostgreSQL, Docker Compose, and a Next.js dashboard are present in the repository.

## Getting Started

1. Review `docker-compose.yml` and the environment variables required by each service.
2. Build and start the configured stack with Docker Compose.
3. Use the service-specific README files and API modules for endpoint details.

## Scope and Limitations

This is a development and integration prototype. It does not represent a production clinical system. Credentials and secrets must be supplied through environment-specific configuration rather than committed values.
