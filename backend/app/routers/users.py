# Users router
# References:
# - see docs/02_functional_req.txt §1 (roles); §5 Security
# - see docs/07_database_design.txt §2(a) Users
# Note: Only admin user creation is exposed as per docs; listing all users is Not documented in the provided files.

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import UserOut
from ..auth import require_admin, get_current_user

router = APIRouter()


@router.get("/me", response_model=UserOut)
def get_me(current=Depends(get_current_user)):
    # 02_functional_req.txt §1: retrieve current user info
    return current


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    # Admin-only access; listing/searching users is Not documented otherwise
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
