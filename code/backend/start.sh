#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or no migrations to run"

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
