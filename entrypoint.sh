#!/bin/bash
set -e

echo "Running Ingestion..."
python -u scripts/run_ingestion.py

echo "Setting up Vector DB..."
python -u scripts/run_vectordb_setup.py

echo "Starting Chat Application..."
# Using 'exec' ensures the python process gets system signals (like CTRL+C)
exec python -u scripts/chat.py