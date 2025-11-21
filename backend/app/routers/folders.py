# Folders router
# References:
# - see docs/02_functional_req.txt §1 (User can add/remove monitored folders)
# - see docs/07_database_design.txt §2(b) Folders

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from ..db import get_db
from ..models import Folder, Log
from ..schemas import FolderCreate, FolderOut
from ..auth import get_current_user
from ..services.file_monitor import get_monitor_service
from ..config import settings

router = APIRouter()


@router.get("/", response_model=dict)
def list_folders(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    # Users: list only own folders (02 §1 User)
    q = db.query(Folder).filter(Folder.owner_id == current.id)
    
    # Get total count
    total = db.scalar(select(func.count()).select_from(Folder).where(Folder.owner_id == current.id)) or 0
    
    # Get paginated results
    folders = q.offset(offset).limit(limit).all()
    
    return {
        "items": folders,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@router.post("/", response_model=FolderOut)
def create_folder(payload: FolderCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    folder = Folder(name=payload.name, path=payload.path, owner_id=current.id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    # Audit log
    db.add(Log(log_type="FOLDER_CREATE", message=f"FOLDER_CREATE: User {current.id} created folder {folder.id}", related_event_id=None))
    db.commit()
    
    # Add to file monitoring service if enabled
    if settings.enable_file_monitoring:
        try:
            monitor = get_monitor_service()
            monitor.add_folder(folder.id, folder.path)
        except Exception as e:
            # Log error but don't fail the request
            db.add(Log(log_type="FILE_MONITOR_ERROR", message=f"Failed to add folder {folder.id} to monitoring: {e}", related_event_id=None))
            db.commit()
    
    return folder


@router.delete("/{folder_id}")
def delete_folder(folder_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    folder = db.get(Folder, folder_id)
    if not folder or folder.owner_id != current.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Remove from file monitoring service if enabled
    if settings.enable_file_monitoring:
        try:
            monitor = get_monitor_service()
            monitor.remove_folder(folder_id)
        except Exception:
            pass  # Ignore errors on deletion
    
    db.delete(folder)
    db.commit()
    
    # Audit log
    db.add(Log(log_type="FOLDER_DELETE", message=f"FOLDER_DELETE: User {current.id} deleted folder {folder_id}", related_event_id=None))
    db.commit()
    
    return {"status": "deleted"}

