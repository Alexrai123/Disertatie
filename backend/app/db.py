# Database session and base configuration
# References:
# - see docs/07_database_design.txt (tables overview)
# - see docs/08_database_design.txt (normalized mirror)
# - see docs/03_non_func_req.txt for portability (DB support)

from __future__ import annotations
from typing import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/secure_ai_sandbox",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
