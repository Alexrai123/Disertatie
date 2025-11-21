# SQLite (tests) vs PostgreSQL (production)

This project uses PostgreSQL in production and SQLite for the test suite. This note documents the intentional differences and how to configure each environment.

## Why SQLite for tests
- Fast, portable, no external service needed.
- File-based DB allows multi-threaded/background tasks in tests when configured correctly.

## Model and migration type differences
- Alembic migration (`backend/alembic/versions/0001_initial_schema.py`) uses `BigInteger` IDs to match the original Postgres design.
- Test-time SQLAlchemy models (`backend/app/models.py`) use `Integer` for PK/FK to avoid SQLite autoincrement edge cases and NOT NULL timestamp issues during tests.
- Timestamps:
  - Postgres: server defaults via `CURRENT_TIMESTAMP` in migrations.
  - SQLite/tests: Python-level defaults in models ensure values exist even when server defaults differ.

This divergence is OK because tests validate behavior, not Postgres-specific types. In production, Alembic migrations define the canonical schema for Postgres.

## Test database configuration
- Tests set `DATABASE_URL` to a file-based SQLite DB: `sqlite:///./test_app.db`.
- `check_same_thread=False` is used in the test engine/Session to allow use across background tasks/threads.
- See `backend/tests/conftest.py`:
  - Exports `DATABASE_URL` before importing the app to ensure all sessions (including BackgroundTasks) use the test DB file.
  - Overrides the FastAPI `get_db` dependency to reuse the same SQLAlchemy session per test, and cleans tables between tests.

## BackgroundTasks in tests
- Escalation uses FastAPI `BackgroundTasks` and runs in-process after the response is returned.
- The escalation test sets delays to 0 for fast execution and polls `/logs` to observe an `ESCALATE` entry.
- Key detail: Because `DATABASE_URL` is exported before app import, the background task writes to the same SQLite file as the test client.

## SMTP behavior in tests
- SMTP settings are optional. Without configuration, email sending is a no-op.
- Notifications and escalations are primarily validated via `Log` rows; email is "best-effort" only and failures are ignored in tests.

## How to run tests locally
1. Create and activate a virtualenv (Windows):
   - `py -m venv .venv`
   - `.venv\Scripts\Activate.ps1`
2. Install deps:
   - `.venv\Scripts\python -m pip install -r backend\requirements.txt`
3. Run tests:
   - `.venv\Scripts\python -m pytest backend\tests -q`

## How to run against Postgres locally
- Set `DATABASE_URL` (example):
  - `postgresql+psycopg2://postgres:postgres@localhost:5432/secure_ai_sandbox`
- Apply migrations:
  - `alembic upgrade head`
- Start the app with the same env.

## Summary of differences
- IDs: Postgres BigInteger (migrations) vs SQLite Integer (models for tests).
- Timestamps: server defaults (Postgres) vs Python-level defaults (tests).
- Concurrency: tests use file-based SQLite with `check_same_thread=False` to support BackgroundTasks.

These choices prioritize deterministic tests and fast feedback, while Alembic migrations remain the source of truth for production schema.
