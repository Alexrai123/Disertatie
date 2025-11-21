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
)


class TestPathValidation:
    """Test path validation and sanitization."""
    
    def test_valid_absolute_path(self):
        """Test that valid absolute paths are accepted."""
        assert validate_path("C:\\Users\\Alex\\Documents") is True
        assert validate_path("/home/user/documents") is True
    
    def test_reject_relative_path(self):
        """Test that relative paths are rejected."""
        with pytest.raises(ValueError, match="must be absolute"):
            validate_path("../documents")
        with pytest.raises(ValueError, match="must be absolute"):
            validate_path("./folder")
    
    def test_reject_directory_traversal(self):
        """Test that directory traversal attempts are rejected."""
        with pytest.raises(ValueError, match="Directory traversal"):
            validate_path("C:\\Users\\..\\..\\Windows\\System32")
        with pytest.raises(ValueError, match="Directory traversal"):
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
        assert validate_password_strength("SecurePass123!") is True
        assert validate_password_strength("MyP@ssw0rd") is True
    
    def test_reject_short_password(self):
        """Test that short passwords are rejected."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            validate_password_strength("Short1!")
    
    def test_reject_no_uppercase(self):
        """Test that passwords without uppercase are rejected."""
        with pytest.raises(ValueError, match="uppercase letter"):
            validate_password_strength("password123!")
    
    def test_reject_no_lowercase(self):
        """Test that passwords without lowercase are rejected."""
        with pytest.raises(ValueError, match="lowercase letter"):
            validate_password_strength("PASSWORD123!")
    
    def test_reject_no_digit(self):
        """Test that passwords without digits are rejected."""
        with pytest.raises(ValueError, match="digit"):
            validate_password_strength("Password!")
    
    def test_reject_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        with pytest.raises(ValueError, match="special character"):
            validate_password_strength("Password123")


class TestUsernameValidation:
    """Test username validation."""
    
    def test_valid_username(self):
        """Test that valid usernames are accepted."""
        assert validate_username("admin") is True
        assert validate_username("user123") is True
        assert validate_username("test_user") is True
    
    def test_reject_short_username(self):
        """Test that short usernames are rejected."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            validate_username("ab")
    
    def test_reject_long_username(self):
        """Test that long usernames are rejected."""
        with pytest.raises(ValueError, match="at most 50 characters"):
            validate_username("a" * 51)
    
    def test_reject_invalid_characters(self):
        """Test that usernames with invalid characters are rejected."""
        with pytest.raises(ValueError, match="alphanumeric"):
            validate_username("user@name")
        with pytest.raises(ValueError, match="alphanumeric"):
            validate_username("user name")


class TestStringLengthValidation:
    """Test string length validation."""
    
    def test_valid_length(self):
        """Test that strings within limits are accepted."""
        assert validate_string_length("test", "field", 1, 10) is True
        assert validate_string_length("hello world", "field", 1, 20) is True
    
    def test_reject_too_short(self):
        """Test that strings below minimum are rejected."""
        with pytest.raises(ValueError, match="at least 5 characters"):
            validate_string_length("hi", "field", 5, 10)
    
    def test_reject_too_long(self):
        """Test that strings above maximum are rejected."""
        with pytest.raises(ValueError, match="at most 5 characters"):
            validate_string_length("too long string", "field", 1, 5)


class TestEventTypeValidation:
    """Test event type validation."""
    
    def test_valid_event_types(self):
        """Test that valid event types are accepted."""
        assert validate_event_type("create") is True
        assert validate_event_type("modify") is True
        assert validate_event_type("delete") is True
    
    def test_reject_invalid_event_type(self):
        """Test that invalid event types are rejected."""
        with pytest.raises(ValueError, match="Invalid event_type"):
            validate_event_type("invalid")
        with pytest.raises(ValueError, match="Invalid event_type"):
            validate_event_type("update")


class TestSeverityLevelValidation:
    """Test severity level validation."""
    
    def test_valid_severity_levels(self):
        """Test that valid severity levels are accepted."""
        assert validate_severity_level("Low") is True
        assert validate_severity_level("Medium") is True
        assert validate_severity_level("High") is True
        assert validate_severity_level("Critical") is True
    
    def test_reject_invalid_severity(self):
        """Test that invalid severity levels are rejected."""
        with pytest.raises(ValueError, match="Invalid severity_level"):
            validate_severity_level("Extreme")
        with pytest.raises(ValueError, match="Invalid severity_level"):
            validate_severity_level("low")  # Case sensitive


class TestRoleValidation:
    """Test role validation."""
    
    def test_valid_roles(self):
        """Test that valid roles are accepted."""
        assert validate_role("admin") is True
        assert validate_role("user") is True
    
    def test_reject_invalid_role(self):
        """Test that invalid roles are rejected."""
        with pytest.raises(ValueError, match="Invalid role"):
            validate_role("superuser")
        with pytest.raises(ValueError, match="Invalid role"):
            validate_role("guest")
