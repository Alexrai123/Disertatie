# Rate limiting middleware
# References:
# - Prevents abuse and DoS attacks
# - Different limits for different endpoint types

from __future__ import annotations
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
# Format: "number/time_period" e.g., "5/minute", "100/hour"

# Strict limits for authentication endpoints (prevent brute force)
AUTH_RATE_LIMIT = "5/minute"

# Moderate limits for write operations
WRITE_RATE_LIMIT = "30/minute"

# Generous limits for read operations
READ_RATE_LIMIT = "100/minute"

# Very generous for health checks
HEALTH_RATE_LIMIT = "1000/minute"
