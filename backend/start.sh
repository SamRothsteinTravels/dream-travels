#!/bin/bash
# Render startup script for Dream Travels backend

echo "Starting Dream Travels backend..."
echo "Environment check:"
echo "MONGO_URL: ${MONGO_URL:0:20}..."
echo "DB_NAME: $DB_NAME"
echo "PORT: $PORT"

# Start the FastAPI application
exec uvicorn enhanced_server:app --host 0.0.0.0 --port $PORT --log-level info