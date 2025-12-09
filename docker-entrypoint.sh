#!/bin/bash
set -e

# Ensure data directory exists
mkdir -p /app/data

# Start the FastAPI application with uvicorn
exec uvicorn universal_corpus.api:app --host 0.0.0.0 --port 8000

