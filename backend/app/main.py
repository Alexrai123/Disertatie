# FastAPI application entrypoint
# References:
# - see docs/04_system_architecture.txt (FastAPI backend)
# - see docs/02_functional_req.txt (functional behaviors & RBAC)
# - see docs/07_database_design.txt and 08_database_design.txt (data model)

from __future__ import annotations
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Depends
from slowapi.errors import RateLimitExceeded

from .routers import auth, users, folders, files, events, logs, ai_rules, feedback, monitoring
from .config import settings
from .middleware.rate_limit import limiter, _rate_limit_exceeded_handler
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from .db import get_db
from sqlalchemy import text
from .services.file_monitor import start_monitoring, stop_monitoring

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger = logging.getLogger("app.startup")
    logger.info("Application starting up...")
    
    # Start file monitoring service if enabled
    if settings.enable_file_monitoring:
        try:
            logger.info("Starting file monitoring service...")
            start_monitoring()
            logger.info("File monitoring service started successfully")
        except Exception as e:
            logger.exception(f"Failed to start file monitoring service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    
    # Stop file monitoring service
    if settings.enable_file_monitoring:
        try:
            logger.info("Stopping file monitoring service...")
            stop_monitoring()
            logger.info("File monitoring service stopped")
        except Exception as e:
            logger.exception(f"Error stopping file monitoring service: {e}")

app = FastAPI(
    title="Secure AI Monitoring Sandbox API",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting
if settings.enable_rate_limiting:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: configurable via settings.cors_allow_origins (comma-separated or "*")
cors_origins = [o.strip() for o in settings.cors_allow_origins.split(",")] if settings.cors_allow_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if settings.enable_security_headers:
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("X-Frame-Options", "DENY")
            response.headers.setdefault("X-XSS-Protection", "1; mode=block")
            response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Structured request/response logging (redacts Authorization)
logger = logging.getLogger("app.access")
logging.basicConfig(level=logging.INFO)

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start = time.time()
        try:
            response = await call_next(request)
            duration = (time.time() - start) * 1000
            logger.info(
                "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
                request_id, request.method, request.url.path, response.status_code, duration
            )
            # Add request ID to response headers for debugging
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.exception(
                "request_id=%s Unhandled error method=%s path=%s duration_ms=%.2f error=%s",
                request_id, request.method, request.url.path, duration, str(e)
            )
            raise

app.add_middleware(AccessLogMiddleware)

# Global exception handlers (consistent JSON and logging)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        "request_id=%s HTTPException status=%s detail=%s path=%s",
        request_id, exc.status_code, exc.detail, request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status": exc.status_code, "request_id": request_id}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("request_id=%s Unhandled Exception at path=%s", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "request_id": request_id}
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(folders.router, prefix="/folders", tags=["folders"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])
app.include_router(ai_rules.router, prefix="/ai-rules", tags=["ai-rules"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])

# Chatbot endpoints (admin-only) are provided in dedicated router
try:
    from .routers import chatbot  # type: ignore
    app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
except Exception:
    # Router may not exist if not yet created; ignore in dev
    pass

# Health endpoint (API + DB)
@app.get("/health", tags=["ops"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "db": db_ok}


