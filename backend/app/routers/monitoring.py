# Monitoring status router
# Provides endpoints to check file monitoring service status

from __future__ import annotations
from fastapi import APIRouter, Depends

from ..auth import require_admin
from ..services.file_monitor import get_monitor_service

router = APIRouter()


@router.get("/status")
def get_monitoring_status(admin=Depends(require_admin)):
    """Get current file monitoring service status (admin only)"""
    service = get_monitor_service()
    return service.get_status()
