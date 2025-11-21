# Files router
# References:
# - see docs/02_functional_req.txt §1, §8 (Users manage monitored files)
# - see docs/07_database_design.txt §2(c) Files

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from ..db import get_db
from ..models import File, Folder, Log
from ..schemas import FileCreate, FileOut
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=dict)
def list_files(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    # Users: list only own files (02 §1 User)
    q = db.query(File).filter(File.owner_id == current.id)
    
    # Get total count
    total = db.scalar(select(func.count()).select_from(File).where(File.owner_id == current.id)) or 0
    
    # Get paginated results
    files = q.offset(offset).limit(limit).all()
    
    return {
        "items": files,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }


@router.post("/", response_model=FileOut)
def create_file(payload: FileCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    # Ensure the folder belongs to the current user (02 §1)
    folder = db.get(Folder, payload.folder_id)
    if not folder or folder.owner_id != current.id:
        raise HTTPException(status_code=404, detail="Folder not found or not owned by user")
    f = File(name=payload.name, path=payload.path, folder_id=payload.folder_id, owner_id=current.id)
    db.add(f)
    db.commit()
    db.refresh(f)
    # Audit log
    db.add(Log(log_type="FILE_CREATE", message=f"FILE_CREATE: User {current.id} created file {f.id}", related_event_id=None))
    db.commit()
    return f


@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    f = db.get(File, file_id)
    if not f or f.owner_id != current.id:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(f)
    db.commit()
    # Audit log
    db.add(Log(log_type="FILE_DELETE", message=f"FILE_DELETE: User {current.id} deleted file {file_id}", related_event_id=None))
    db.commit()
    return {"status": "deleted"}

