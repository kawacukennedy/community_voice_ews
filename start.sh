#!/bin/bash
set -e

echo "Starting Community Voice EWS..."
echo "Database: ${DATABASE_URL:-sqlite:///./ews.db}"

cd backend

uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
