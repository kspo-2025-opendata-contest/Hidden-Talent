#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or no migrations to run"

echo "Loading initial data (if not already loaded)..."
python -m app.scripts.load_all --programs-limit 5000 || echo "Data load skipped or already exists"

echo "Creating test accounts..."
python -m app.scripts.create_accounts || echo "Account creation skipped or already exists"

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
