# Chatbot router (Admin-only)
# References:
# - see docs/02_functional_req.txt §7 Chatbot (Admin Only)
# - see docs/13_app_arch.txt §1 Presentation (Admin dashboard with AI chatbot)
# - Provides simple summaries and log queries for the frontend Chatbot page

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from ..db import get_db
from ..auth import require_admin
from ..models import Event, Log

router = APIRouter()


@router.get("/summary")
def chatbot_summary(db: Session = Depends(get_db), admin=Depends(require_admin)):
    # Basic counts
    total_events = db.scalar(select(func.count()).select_from(Event)) or 0
    total_logs = db.scalar(select(func.count()).select_from(Log)) or 0

    # Recent AI decision snippets
    recent_ai = (
        db.execute(
            select(Log).where(Log.log_type == "AI_DECISION").order_by(Log.id.desc()).limit(10)
        ).scalars().all()
    )
    recent_ai_messages = [entry.message for entry in recent_ai]

    return {
        "totals": {
            "events": total_events,
            "logs": total_logs,
        },
        "recent_ai_decisions": recent_ai_messages,
    }


@router.get("/query")
def chatbot_query(
    q: Optional[str] = Query(default=None, description="substring to search in log messages"),
    type: Optional[str] = Query(default=None, description="log_type exact match (e.g., NOTIFY, ESCALATE, AI_DECISION)"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    stmt = select(Log).order_by(Log.id.desc())
    if type:
        stmt = stmt.where(Log.log_type == type)
    if q:
        # simple ILIKE substring search
        stmt = stmt.where(Log.message.ilike(f"%{q}%"))
    rows = db.execute(stmt.limit(limit)).scalars().all()
    return [{"id": r.id, "type": r.log_type, "message": r.message, "related_event_id": r.related_event_id} for r in rows]
