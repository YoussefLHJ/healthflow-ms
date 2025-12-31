#!/bin/bash

# Fast Docker build script
echo "Creating healthcare network..."
docker network create healthcare_network 2>/dev/null || true

echo "Building ModelRisque with build cache..."
docker build --progress=plain -t model-risque . 

echo "Running with docker-compose..."
docker-compose up model-risque