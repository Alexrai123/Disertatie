# Validation utilities
# Centralized validation for security and data integrity

from __future__ import annotations
import re
from pathlib import Path
from fastapi import HTTPException


class ValidationError(HTTPException):
    """Custom validation error"""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


def validate_path(path: str, must_exist: bool = False, must_be_absolute: bool = True) -> str:
    """
    Validate and sanitize file/folder paths.
    
    Args:
        path: Path to validate
        must_exist: If True, path must exist on filesystem
        must_be_absolute: If True, path must be absolute
        
    Returns:
        Normalized absolute path
        
    Raises:
        ValidationError: If path is invalid or unsafe
    """
    if not path or not isinstance(path, str):
        raise ValidationError("Path must be a non-empty string")
    
    # Remove leading/trailing whitespace
    path = path.strip()
    
    # Convert to Path object for normalization
    try:
        path_obj = Path(path)
    except (ValueError, OSError) as e:
        raise ValidationError(f"Invalid path format: {e}")
    
    # Resolve to absolute path
    try:
        resolved_path = path_obj.resolve()
    except (ValueError, OSError, RuntimeError) as e:
        raise ValidationError(f"Cannot resolve path: {e}")
    
    # Check if absolute path is required
    if must_be_absolute and not resolved_path.is_absolute():
        raise ValidationError("Path must be absolute")
    
    # Prevent directory traversal attacks
    # Check for suspicious patterns
    suspicious_patterns = ['..', '~', '$', '`', ';', '|', '&', '<', '>']
    path_str = str(resolved_path)
    for pattern in suspicious_patterns:
        if pattern in path:  # Check original path
            print(f"DEBUG: Found suspicious pattern '{pattern}' in '{path}'")
            raise ValidationError(f"Path contains suspicious pattern: {pattern}")
    
    # Check if path exists (if required)
    if must_exist and not resolved_path.exists():
        raise ValidationError(f"Path does not exist: {path_str}")
    
    return str(resolved_path)


def sanitize_path(path: str) -> str:
    """
    Sanitize path by removing directory traversal sequences.
    
    This is a simpler version of validate_path that just removes
    suspicious patterns without raising errors.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path with traversal sequences removed
    """
    if not path or not isinstance(path, str):
        return ""
    
    # Remove directory traversal patterns
    sanitized = path.replace("..", "").replace("~", "")
    
    # Normalize the path
    try:
        path_obj = Path(sanitized)
        return str(path_obj)
    except (ValueError, OSError):
        return sanitized



def validate_password_strength(password: str) -> None:
    """
    Validate password meets security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not password or not isinstance(password, str):
        raise ValidationError("Password must be a non-empty string")
    
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character")


def validate_username(username: str) -> str:
    """
    Validate username format.
    
    Requirements:
    - 3-50 characters
    - Alphanumeric, underscore, hyphen only
    - Must start with letter
    
    Returns:
        Sanitized username
        
    Raises:
        ValidationError: If username is invalid
    """
    if not username or not isinstance(username, str):
        raise ValidationError("Username must be a non-empty string")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long")
    
    if len(username) > 50:
        raise ValidationError("Username must not exceed 50 characters")
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        raise ValidationError(
            "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
        )
    
    return username


def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
    """
    Validate string length to prevent DoS attacks.
    
    Args:
        value: String to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Stripped string
        
    Raises:
        ValidationError: If string length is invalid
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    value = value.strip()
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} must not exceed {max_length} characters")
    
    return value


def validate_event_type(event_type: str) -> str:
    """
    Validate event type is one of the allowed values.
    
    Allowed: create, modify, delete
    
    Returns:
        Lowercase event type
        
    Raises:
        ValidationError: If event type is invalid
    """
    if not event_type or not isinstance(event_type, str):
        raise ValidationError("Event type must be a non-empty string")
    
    event_type = event_type.strip().lower()
    
    allowed_types = {'create', 'modify', 'delete'}
    if event_type not in allowed_types:
        raise ValidationError(f"Event type must be one of: {', '.join(allowed_types)}")
    
    return event_type


def validate_severity_level(severity: str) -> str:
    """
    Validate severity level is one of the allowed values.
    
    Allowed: Low, Medium, High, Critical
    
    Returns:
        Capitalized severity level
        
    Raises:
        ValidationError: If severity is invalid
    """
    if not severity or not isinstance(severity, str):
        raise ValidationError("Severity level must be a non-empty string")
    
    severity = severity.strip().capitalize()
    
    allowed_levels = {'Low', 'Medium', 'High', 'Critical'}
    if severity not in allowed_levels:
        raise ValidationError(f"Severity level must be one of: {', '.join(allowed_levels)}")
    
    return severity


def validate_role(role: str) -> str:
    """
    Validate user role is one of the allowed values.
    
    Allowed: admin, user
    
    Returns:
        Lowercase role
        
    Raises:
        ValidationError: If role is invalid
    """
    if not role or not isinstance(role, str):
        raise ValidationError("Role must be a non-empty string")
    
    role = role.strip().lower()
    
    allowed_roles = {'admin', 'user'}
    if role not in allowed_roles:
        raise ValidationError(f"Role must be one of: {', '.join(allowed_roles)}")
    
    return role
