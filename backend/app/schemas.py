# Pydantic schemas (request/response models)
# References:
# - see docs/07_database_design.txt §2 Tables
# - see docs/02_functional_req.txt (role capabilities)

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, Field
from app.services.validation import (
    validate_username,
    validate_password_strength,
    validate_path,
    validate_event_type,
    validate_severity_level,
    validate_role,
    validate_string_length,
)



# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Users
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(..., pattern="^(admin|user)$")
    
    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        return validate_username(v)
    
    @field_validator('role')
    @classmethod
    def validate_role_value(cls, v: str) -> str:
        return validate_role(v)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., pattern="^(admin|user)$")
    
    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        return validate_username(v)
    
    @field_validator('password')
    @classmethod
    def validate_password_format(cls, v: str) -> str:
        validate_password_strength(v)
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role_value(cls, v: str) -> str:
        return validate_role(v)


class UserOut(UserBase):
    id: int
    created_at: datetime | None = None
    last_login: datetime | None = None

    class Config:
        from_attributes = True


# Folders
class FolderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1, max_length=1000)
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        return validate_string_length(v, "Folder name", min_length=1, max_length=255)
    
    @field_validator('path')
    @classmethod
    def validate_path_format(cls, v: str) -> str:
        # Validate path but don't require it to exist yet
        return validate_path(v, must_exist=False, must_be_absolute=True)


class FolderCreate(FolderBase):
    pass


class FolderOut(FolderBase):
    id: int
    owner_id: int
    created_at: datetime | None = None
    modified_at: datetime | None = None

    class Config:
        from_attributes = True


# Files
class FileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1, max_length=1000)
    folder_id: int = Field(..., gt=0)
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        return validate_string_length(v, "File name", min_length=1, max_length=255)
    
    @field_validator('path')
    @classmethod
    def validate_path_format(cls, v: str) -> str:
        # Validate path but don't require it to exist yet
        return validate_path(v, must_exist=False, must_be_absolute=True)


class FileCreate(FileBase):
    pass


class FileOut(FileBase):
    id: int
    owner_id: int
    created_at: datetime | None = None
    modified_at: datetime | None = None
    hash: Optional[str] = None

    class Config:
        from_attributes = True


# AI Rules
class AIRuleBase(BaseModel):
    rule_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    severity_level: Optional[str] = Field(None, pattern="^(Low|Medium|High|Critical)$")
    action_type: Optional[str] = Field(None, max_length=50)
    adaptive_flag: bool = False
    
    @field_validator('rule_name')
    @classmethod
    def validate_rule_name_length(cls, v: str) -> str:
        return validate_string_length(v, "Rule name", min_length=1, max_length=200)
    
    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_string_length(v, "Description", min_length=0, max_length=1000)
        return v
    
    @field_validator('severity_level')
    @classmethod
    def validate_severity_value(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_severity_level(v)
        return v
    
    @field_validator('action_type')
    @classmethod
    def validate_action_type_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_string_length(v, "Action type", min_length=1, max_length=50)
        return v


class AIRuleCreate(AIRuleBase):
    pass


class AIRuleOut(AIRuleBase):
    id: int
    last_updated: datetime | None = None
    stored_in_engine: bool = False

    class Config:
        from_attributes = True


# Events
class EventBase(BaseModel):
    event_type: str = Field(..., pattern="^(create|modify|delete)$")
    target_file_id: Optional[int] = Field(None, gt=0)
    target_folder_id: Optional[int] = Field(None, gt=0)
    
    @field_validator('event_type')
    @classmethod
    def validate_event_type_value(cls, v: str) -> str:
        return validate_event_type(v)
    
    @field_validator('target_folder_id')
    @classmethod
    def validate_xor_constraint(cls, v: Optional[int], info) -> Optional[int]:
        # Ensure either file_id or folder_id is set, but not both
        file_id = info.data.get('target_file_id')
        if file_id is None and v is None:
            raise ValueError("Either target_file_id or target_folder_id must be set")
        if file_id is not None and v is not None:
            raise ValueError("Cannot set both target_file_id and target_folder_id")
        return v


class EventCreate(EventBase):
    pass


class EventOut(EventBase):
    id: int
    triggered_by_user_id: Optional[int] = None
    timestamp: datetime | None = None
    processed_flag: bool = False

    class Config:
        from_attributes = True


# Logs
class LogOut(BaseModel):
    id: int
    log_type: str
    message: str
    related_event_id: Optional[int] = None
    timestamp: datetime | None = None

    class Config:
        from_attributes = True


# Pagination
class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
    items: list
    total: int
    limit: int
    offset: int
    has_more: bool

