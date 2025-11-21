# Application settings
# References:
# - see docs/03_non_func_req.txt for portability and environment usage
# - see docs/04_system_architecture.txt for backend architecture selection (FastAPI)

from __future__ import annotations
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    secret_key: str = "CHANGE_ME_DEV_ONLY"  # Not documented in the provided files (value). Provide via env.
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 60

    # DB URL taken from env by app.db; included here for completeness
    database_url: str | None = None

    # Notifications (email)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_sender: str | None = None
    smtp_admin_recipients: str | None = None  # comma-separated list
    smtp_use_tls: bool = True

    # Escalation delays (seconds)
    escalation_high_delay_seconds: int = 300
    escalation_critical_delay_seconds: int = 120

    # CORS (comma-separated origins; * allowed only in dev)
    cors_allow_origins: str = "*"

    # Security headers toggles
    enable_security_headers: bool = True
    
    # File Monitoring
    enable_file_monitoring: bool = True
    file_monitor_poll_interval: int = 1  # seconds
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_auth: str = "5/minute"
    rate_limit_write: str = "30/minute"
    rate_limit_read: str = "100/minute"
    
    # Password Policy
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

