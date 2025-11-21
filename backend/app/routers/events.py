# Events router
# References:
# - see docs/02_functional_req.txt §2 System Monitoring; §5 Security (role restrictions)
# - see docs/07_database_design.txt §2(e) Events

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from ..db import get_db
from ..models import Event
from ..schemas import EventCreate, EventOut
from ..auth import get_current_user
from ..ai.event_listener import handle_event

router = APIRouter()


@router.get("/", response_model=dict)
def list_events(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    event_type: Optional[str] = Query(default=None, pattern="^(create|modify|delete)$"),
    processed: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    # 02 §2 and §5: Users can view their own activity; Admin can view all
    q = db.query(Event)
    if current.role != "admin":
        q = q.filter(Event.triggered_by_user_id == current.id)
    
    # Apply filters
    if event_type:
        q = q.filter(Event.event_type == event_type)
    if processed is not None:
        q = q.filter(Event.processed_flag == processed)
    
    # Get total count with same filters
    count_q = select(func.count()).select_from(Event)
    if current.role != "admin":
        count_q = count_q.where(Event.triggered_by_user_id == current.id)
    if event_type:
        count_q = count_q.where(Event.event_type == event_type)
    if processed is not None:
        count_q = count_q.where(Event.processed_flag == processed)
    
    total = db.scalar(count_q) or 0
    
    # Get paginated results
    events = q.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "items": events,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@router.post("/", response_model=EventOut)
def create_event(
    background_tasks: BackgroundTasks,
    payload: EventCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    # Users can trigger monitoring events per 02 §7 (Chatbot is admin only; monitoring actions allowed for users)
    e = Event(
        event_type=payload.event_type,
        target_file_id=payload.target_file_id,
        target_folder_id=payload.target_folder_id,
        triggered_by_user_id=current.id,
        processed_flag=False,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    # Trigger AI Event Listener (14_ai_engine_design.txt §1(a); 08_ai_behavior_rules.txt §2-§3)
    handle_event(db, e, background_tasks=background_tasks)
    return e


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    e = db.get(Event, event_id)
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    if current.role != "admin" and e.triggered_by_user_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return e

