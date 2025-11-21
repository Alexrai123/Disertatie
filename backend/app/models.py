# SQLAlchemy models mapping to Alembic schema
# References:
# - see docs/07_database_design.txt §2 Tables
# - see docs/08_database_design.txt (normalized mirror)
# - see docs/08_ai_behavior_rules.txt for ai_rules semantics

from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class User(Base):
    __tablename__ = "users"
    # 07 §2(a)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # admin/user per docs
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    folders: Mapped[list["Folder"]] = relationship("Folder", back_populates="owner")
    files: Mapped[list["File"]] = relationship("File", back_populates="owner")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Folder(Base):
    __tablename__ = "folders"
    # 07 §2(b)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    modified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    owner: Mapped[User] = relationship("User", back_populates="folders")
    files: Mapped[list["File"]] = relationship("File", back_populates="folder")
    
    def __repr__(self) -> str:
        return f"<Folder(id={self.id}, name='{self.name}', path='{self.path}')>"


class File(Base):
    __tablename__ = "files"
    # 07 §2(c)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    folder_id: Mapped[int] = mapped_column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    modified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    hash: Mapped[str | None] = mapped_column(String(128))

    owner: Mapped[User] = relationship("User", back_populates="files")
    folder: Mapped[Folder] = relationship("Folder", back_populates="files")
    
    def __repr__(self) -> str:
        return f"<File(id={self.id}, name='{self.name}', path='{self.path}')>"


class AIRule(Base):
    __tablename__ = "ai_rules"
    # 07 §2(d), semantics 08_ai_behavior_rules.txt
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity_level: Mapped[str | None] = mapped_column(String(20))
    action_type: Mapped[str | None] = mapped_column(String(50))
    adaptive_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    stored_in_engine: Mapped[bool] = mapped_column(Boolean, default=False)
    
    def __repr__(self) -> str:
        return f"<AIRule(id={self.id}, name='{self.rule_name}', severity='{self.severity_level}')>"


class Event(Base):
    __tablename__ = "events"
    # 07 §2(e)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_file_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("files.id", ondelete="SET NULL"))
    target_folder_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("folders.id", ondelete="SET NULL"))
    triggered_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    target_file: Mapped[File | None] = relationship("File")
    target_folder: Mapped[Folder | None] = relationship("Folder")
    triggered_by_user: Mapped[User | None] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type='{self.event_type}', processed={self.processed_flag})>"


class AIFeedback(Base):
    __tablename__ = "ai_feedback"
    # 07 §2(f)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    admin_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    event: Mapped[Event] = relationship("Event")
    admin: Mapped[User | None] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<AIFeedback(id={self.id}, event_id={self.event_id}, type='{self.feedback_type}')>"


class Log(Base):
    __tablename__ = "logs"
    # 07 §2(g)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    log_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_event_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("events.id", ondelete="SET NULL"))
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    related_event: Mapped[Event | None] = relationship("Event")
    
    def __repr__(self) -> str:
        return f"<Log(id={self.id}, type='{self.log_type}', timestamp={self.timestamp})>"

