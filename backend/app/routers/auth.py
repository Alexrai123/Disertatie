# Auth router
# References:
# - see docs/02_functional_req.txt §1 (User/Admin roles)
# - see docs/07_database_design.txt §2(a)

from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import authenticate_user, create_access_token, get_password_hash
from ..db import get_db
from ..models import User
from ..schemas import Token, UserCreate, UserOut
from ..auth import require_admin, get_current_user
from typing import Any, cast

router = APIRouter()


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 02_functional_req.txt §5 Security; JWT login flow
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Update last_login (07 §2(a))
    user.last_login = cast(Any, datetime.now(tz=timezone.utc))
    db.add(user)
    db.commit()
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(access_token=access_token)


@router.post("/users", response_model=UserOut)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    # Admin-only create user (02_functional_req.txt §1)
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def read_me(current=Depends(get_current_user)):
    return current
