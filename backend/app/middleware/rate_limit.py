# Rate limiting middleware
# References:
# - Prevents abuse and DoS attacks
# - Different limits for different endpoint types

from __future__ import annotations
from slowapi import Limiter
from slowapi.util import get_remote_address

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

# Rate limit exceeded handler
async def _rate_limit_exceeded_handler(request, exc):
    """Handler for rate limit exceeded errors"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "detail": str(exc)}
    )

