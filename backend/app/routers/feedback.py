# Feedback router
# References:
# - see docs/08_ai_behavior_rules.txt §4 Feedback Adaptation
# - see docs/14_ai_engine_design.txt §1(f) Feedback Processor
# - see docs/07_database_design.txt §2(f) AI_Feedback
# - Admin-only per docs/02_functional_req.txt §1

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Event, AIRule
from ..auth import require_admin
from ..ai.feedback_processor import submit_feedback

router = APIRouter()


class FeedbackIn(BaseModel):
    event_id: int
    feedback_type: str  # approve/reject/modify
    comment: Optional[str] = None
    rule_id: Optional[int] = None


@router.post("/")
def give_feedback(payload: FeedbackIn, db: Session = Depends(get_db), admin=Depends(require_admin)):
    event = db.get(Event, payload.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    rule = db.get(AIRule, payload.rule_id) if payload.rule_id else None
    fb = submit_feedback(
        db,
        event=event,
        admin_id=admin.id,
        feedback_type=payload.feedback_type,
        comment=payload.comment,
        rule=rule,
    )
    return {"status": "ok", "feedback_id": fb.id}
