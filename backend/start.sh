#!/usr/bin/env bash
set -euo pipefail

# Run DB migrations (docs/03_non_func_req.txt §6 Database migrations)
alembic -c /app/alembic.ini upgrade head

# Start FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
