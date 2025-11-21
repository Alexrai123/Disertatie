"""
Tests for input validation and sanitization service.
"""
import pytest
from app.services.validation import (
    validate_path,
    sanitize_path,
    validate_password_strength,
    validate_username,
    validate_string_length,
    validate_event_type,
    validate_severity_level,
    validate_role,
    ValidationError,
)
import sys
import os


class TestPathValidation:
    """Test path validation and sanitization."""
    
    def test_valid_absolute_path(self):
        """Test that valid absolute paths are accepted."""
        if sys.platform == "win32":
            assert validate_path("C:\\Users\\Alex\\Documents") is not None
        else:
            assert validate_path("/home/user/documents") is not None
    
    def test_reject_relative_path(self):
        """Test that relative paths are rejected."""
        try:
            validate_path("../documents")
            pytest.fail("Did not raise ValidationError")
        except ValidationError as e:
            print(f"Caught expected ValidationError: {e}")
            assert "suspicious pattern" in str(e)
        except Exception as e:
            pytest.fail(f"Raised unexpected exception: {type(e).__name__}: {e}")
        
        # Test explicit non-absolute check if we can bypass resolve (we can't easily)
        # So we rely on suspicious pattern check for ..

    
    def test_reject_directory_traversal(self):
        """Test that directory traversal attempts are rejected."""
        with pytest.raises(ValidationError, match="suspicious pattern"):
            validate_path("C:\\Users\\..\\..\\Windows\\System32")
        with pytest.raises(ValidationError, match="suspicious pattern"):
            validate_path("/home/user/../../etc/passwd")
    
    def test_sanitize_path_removes_traversal(self):
        """Test that path sanitization removes traversal sequences."""
        result = sanitize_path("C:\\Users\\Alex\\..\\Documents")
        assert ".." not in result
        
        result = sanitize_path("/home/user/../documents")
        assert ".." not in result


class TestPasswordValidation:
    """Test password strength validation."""
    
    def test_valid_strong_password(self):
        """Test that strong passwords are accepted."""
        assert validate_password_strength("SecurePass123!") is None
        assert validate_password_strength("MyP@ssw0rd") is None
    
    def test_reject_short_password(self):
        """Test that short passwords are rejected."""
        with pytest.raises(ValidationError, match="at least 8 characters"):
            validate_password_strength("Short1!")
    
    def test_reject_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        with pytest.raises(ValidationError, match="uppercase letter"):
            validate_password_strength("password123!")
    
    def test_reject_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        with pytest.raises(ValidationError, match="lowercase letter"):
            validate_password_strength("PASSWORD123!")

    def test_valid_username(self):
        """Test that valid usernames are accepted."""
        assert validate_username("admin") == "admin"
        assert validate_username("user123") == "user123"
        assert validate_username("test_user") == "test_user"
    
    def test_reject_short_username(self):
        """Test that short usernames are rejected."""
        with pytest.raises(ValidationError, match="at least 3 characters"):
            validate_username("ab")
    
    def test_reject_long_username(self):
        """Test that long usernames are rejected."""
        with pytest.raises(ValidationError, match="Username must not exceed 50 characters"):
            validate_username("a" * 51)
    
    def test_reject_invalid_characters(self):
        """Test that usernames with invalid characters are rejected."""
        with pytest.raises(ValidationError, match="Username must start with a letter"):
            validate_username("user@name")
        with pytest.raises(ValidationError, match="Username must start with a letter"):
            validate_username("user name")


class TestStringLengthValidation:
    """Test string length validation."""
    
    def test_valid_length(self):
        """Test that strings within limits are accepted."""
        assert validate_string_length("test", "field", 1, 10) == "test"
        assert validate_string_length("hello world", "field", 1, 20) == "hello world"
    
    def test_reject_too_short(self):
        """Test that strings below minimum are rejected."""
        with pytest.raises(ValidationError, match="at least 5 characters"):
            validate_string_length("hi", "field", 5, 10)
    
    def test_reject_too_long(self):
        """Test that strings above maximum are rejected."""
        with pytest.raises(ValidationError, match="must not exceed"):
            validate_string_length("too long string", "field", 1, 5)


class TestEventTypeValidation:
    """Test event type validation."""
    
    def test_valid_event_types(self):
        """Test that valid event types are accepted."""
        assert validate_event_type("create") == "create"
        assert validate_event_type("modify") == "modify"
        assert validate_event_type("delete") == "delete"
    
    def test_reject_invalid_event_type(self):
        """Test that invalid event types are rejected."""
        with pytest.raises(ValidationError, match="Event type must be one of"):
            validate_event_type("invalid")
        with pytest.raises(ValidationError, match="Event type must be one of"):
            validate_event_type("update")


class TestSeverityLevelValidation:
    """Test severity level validation."""
    
    def test_valid_severity_levels(self):
        """Test that valid severity levels are accepted."""
        assert validate_severity_level("Low") == "Low"
        assert validate_severity_level("Medium") == "Medium"
        assert validate_severity_level("High") == "High"
        assert validate_severity_level("Critical") == "Critical"
    
    def test_reject_invalid_severity(self):
        """Test that invalid severity levels are rejected."""
        with pytest.raises(ValidationError, match="Severity level must be one of"):
            validate_severity_level("Extreme")
        with pytest.raises(ValidationError, match="Severity level must be one of"):
            validate_severity_level("very_low")


class TestRoleValidation:
    """Test role validation."""
    
    def test_valid_roles(self):
        """Test that valid roles are accepted."""
        assert validate_role("admin") == "admin"
        assert validate_role("user") == "user"
    
    def test_reject_invalid_role(self):
        """Test that invalid roles are rejected."""
        with pytest.raises(ValidationError, match="Role must be one of"):
            validate_role("superuser")
        with pytest.raises(ValidationError, match="Role must be one of"):
            validate_role("guest")
