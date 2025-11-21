# Secure AI Monitoring Sandbox — Backend Migrations

This backend folder contains Alembic configuration and the initial PostgreSQL schema for the Secure AI Monitoring Sandbox.

## Documentation Mapping

- Core schema tables are defined per:
  - `docs/07_database_design.txt` (sections 2, 3, 4, 5)
  - `docs/08_database_design.txt` (normalized mirror of 07)
  - `docs/08_ai_behavior_rules.txt` (referenced for severity/action semantics on `ai_rules`)
- Extended constraints and indices are placeholders pending details in:
  - `docs/11_database_design_extended.txt` (currently a placeholder; see comments inside migration)

## Created Files

- `backend/alembic.ini` — Alembic config pointing to PostgreSQL URL.
- `backend/alembic/env.py` — Alembic environment script.
- `backend/alembic/versions/0001_initial_schema.py` — Initial migration with tables:
  - `users` — 07 §2(a)
  - `folders` — 07 §2(b)
  - `files` — 07 §2(c)
  - `ai_rules` — 07 §2(d); 08 for semantics
  - `events` — 07 §2(e)
  - `ai_feedback` — 07 §2(f)
  - `logs` — 07 §2(g)

## Notable Constraints and Placeholders

- Events target XOR (file vs folder):
  - Requirement: `docs/11_database_design_extended.txt` §2 suggests constraints; exact rule not documented.
  - Current migration does not enforce XOR; will be added when documented.

- Indices:
  - `docs/11_database_design_extended.txt` §1 mentions indices; some basic indexes are added as placeholders:
    - `ix_folders_owner_id`, `ix_files_folder_id`, `ix_files_owner_id`,
      `ix_events_target_file_id`, `ix_events_target_folder_id`, `ix_events_triggered_by_user_id`,
      `ix_ai_feedback_event_id`, `ix_logs_related_event_id`.
  - Further index strategy is “Not documented in the provided files”.

- Additional tables (Notifications, Actions, AuditLog):
  - `docs/11_database_design_extended.txt` §3 lists these, but definitions are not provided.
  - Status: Not implemented. Marked as “Not documented in the provided files”.

- Security/RLS/roles mapping:
  - `docs/11_database_design_extended.txt` §4 mentions RLS and roles; specifics are not provided.
  - Status: Not implemented in migration; to be added once documented.

## Configuration

- Default connection URL is configured in `backend/alembic.ini`:
  - `postgresql+psycopg2://postgres:postgres@localhost:5432/secure_ai_sandbox`
- You can override this with `DATABASE_URL` environment variable.

## How to Run Migrations (Windows PowerShell)

```powershell
# Optional: create a virtual environment
python -m venv .venv
. .venv/Scripts/Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Ensure your PostgreSQL server has a database named secure_ai_sandbox
# Example using psql (adjust if needed):
# createdb secure_ai_sandbox

# Run migrations
alembic -c backend/alembic.ini upgrade head
```

## Rollback

```powershell
alembic -c backend/alembic.ini downgrade base
```

## Next Steps (per project brief)

- Add SQLAlchemy models mirroring the migration tables.
- Implement backend service (FastAPI/Express/Flask as per docs) with RBAC and JWT.
- Implement AI Engine modules (Event Listener, Rules Processor, Decision Maker, Feedback Processor, Persistence, Notifications, Logging) with persistence mapped to these tables.
- Add remaining tables once documented in `docs/11_database_design_extended.txt`.
