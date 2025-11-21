from __future__ import annotations
import os
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a file-based SQLite DB for thread-safety with TestClient and background tasks
TEST_DB_URL = "sqlite:///./test_app.db"
os.environ["DATABASE_URL"] = TEST_DB_URL

from app.main import app
from app.db import Base
from app.models import User
from app.auth import get_password_hash


def get_test_engine():
    connect_args = {"check_same_thread": False}
    return create_engine(TEST_DB_URL, connect_args=connect_args, future=True)

@pytest.fixture(scope="session")
def db_engine():
    engine = get_test_engine()
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("./test_app.db")
    except Exception:
        pass

@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine, future=True)
    db = TestingSessionLocal()
    # Clean tables between tests
    for tbl in reversed(Base.metadata.sorted_tables):
        db.execute(tbl.delete())
    db.commit()
    yield db
    db.close()

# Override get_db dependency to use the test session
from app import db as app_db  # after defining fixtures

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[app_db.get_db] = override_get_db

    # Seed users
    admin = User(
        username="admin",
        password_hash=get_password_hash("adminpass"),
        role="admin",
        created_at=datetime.now(tz=timezone.utc),
    )
    user = User(
        username="user",
        password_hash=get_password_hash("userpass"),
        role="user",
        created_at=datetime.now(tz=timezone.utc),
    )
    db_session.add_all([admin, user])
    db_session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
