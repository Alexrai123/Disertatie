# Logs router
# References:
# - see docs/02_functional_req.txt §1, §2, §5 (Admin can view logs; Users can view own activity logs)
# - see docs/07_database_design.txt §2(g) Logs

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import get_db
from ..models import Log, Event
from ..schemas import LogOut
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[LogOut])
def list_logs(db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Admin sees all logs; User sees only logs for their events (02_functional_req.txt §1, §5)
    if current.role == "admin":
        return db.execute(select(Log).order_by(Log.timestamp.desc())).scalars().all()
    else:
        stmt = (
            select(Log)
            .join(Event, Log.related_event_id == Event.id, isouter=True)
            .where((Event.triggered_by_user_id == current.id) | (Log.related_event_id.is_(None)))
            .order_by(Log.timestamp.desc())
        )
        return db.execute(stmt).scalars().all()


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    log = db.get(Log, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    if current.role != "admin" and log.related_event_id is not None:
        ev = db.get(Event, log.related_event_id)
        if not ev or ev.triggered_by_user_id != current.id:
            raise HTTPException(status_code=403, detail="Forbidden")
    return log
