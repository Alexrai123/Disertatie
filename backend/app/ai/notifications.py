# Notification System
# References:
# - see docs/08_ai_behavior_rules.txt §3 Action Determination, §5 Escalation Rules, §7 Security & Access
# - see docs/14_ai_engine_design.txt §1(d) Notification System
# Enhanced with retry logic and batching

from __future__ import annotations
import time
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import BackgroundTasks

from ..models import Log
from ..config import settings


# Notification batching to prevent spam
_notification_batch: list[str] = []
_last_batch_send: Optional[float] = None
_batch_interval = 300  # 5 minutes


def _send_email_with_retry(subject: str, body: str, max_retries: int = 3) -> bool:
    """
    Send email with retry logic.
    Returns True if successful, False otherwise.
    """
    if not settings.smtp_host or not settings.smtp_sender or not settings.smtp_admin_recipients:
        return False
    
    recipients = [r.strip() for r in settings.smtp_admin_recipients.split(",") if r.strip()]
    if not recipients:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    context = ssl.create_default_context()
    
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_use_tls:
                    server.starttls(context=context)
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                # Wait before retry (exponential backoff)
                time.sleep(2 ** attempt)
            else:
                # Log final failure
                import logging
                logging.getLogger("app.notifications").error(
                    f"Failed to send email after {max_retries} attempts: {e}"
                )
    
    return False


def notify_admins(db: Session, message: str, immediate: bool = False) -> None:
    """
    Notify admins with optional batching.
    
    Args:
        db: Database session
        message: Notification message
        immediate: If True, send immediately. If False, batch notifications.
    """
    global _notification_batch, _last_batch_send
    
    # Always log to database
    log = Log(log_type="NOTIFY", message=message, related_event_id=None)
    db.add(log)
    db.commit()
    
    if immediate:
        # Send immediately
        _send_email_with_retry(
            subject="Secure AI Sandbox: Notification",
            body=message
        )
    else:
        # Add to batch
        _notification_batch.append(message)
        
        # Check if we should send batch
        now = time.time()
        if _last_batch_send is None or (now - _last_batch_send) >= _batch_interval:
            _send_batched_notifications()
            _last_batch_send = now


def _send_batched_notifications() -> None:
    """Send all batched notifications in a single email"""
    global _notification_batch
    
    if not _notification_batch:
        return
    
    # Combine all messages
    body = "Batched Notifications:\n\n" + "\n\n---\n\n".join(_notification_batch)
    subject = f"Secure AI Sandbox: {len(_notification_batch)} Notifications"
    
    _send_email_with_retry(subject=subject, body=body)
    
    # Clear batch
    _notification_batch = []


def _escalation_job(delay: int, severity: str, event_id: int) -> None:
    """Sleeps for delay seconds, then writes an ESCALATE log and sends email using a fresh DB session."""
    try:
        if delay > 0:
            time.sleep(delay)
        from ..db import SessionLocal  # local import to prevent circulars at module import time
        _db = SessionLocal()
        try:
            log = Log(
                log_type="ESCALATE",
                message=f"Escalation triggered for event {event_id} at severity {severity}",
                related_event_id=event_id,
            )
            _db.add(log)
            _db.commit()
        finally:
            _db.close()
    finally:
        # Escalations are always sent immediately (high priority)
        _send_email_with_retry(
            subject=f"Secure AI Sandbox: ESCALATION ({severity})",
            body=f"⚠️ Escalation triggered for event {event_id} at severity {severity}\n\nNo admin response received within the configured time window."
        )


def escalate_if_needed(db: Session, severity: str, event_id: int, background_tasks: BackgroundTasks | None = None) -> None:
    """
    Escalate notification if admin doesn't respond within configured time.
    """
    delay: int | None = None
    if severity == "High":
        delay = settings.escalation_high_delay_seconds
    elif severity == "Critical":
        delay = settings.escalation_critical_delay_seconds
    
    if delay is None:
        return
    
    try:
        if background_tasks is not None:
            background_tasks.add_task(_escalation_job, delay, severity, event_id)
        else:
            # Synchronous fallback (tests or non-request context)
            _escalation_job(delay, severity, event_id)
    except Exception:
        # Fallback: immediate escalation log if background task cannot be scheduled
        log = Log(
            log_type="ESCALATE",
            message=f"Escalation (immediate fallback) for event {event_id} at severity {severity}",
            related_event_id=event_id,
        )
        db.add(log)
        db.commit()


def get_notification_statistics(db: Session, hours: int = 24) -> dict:
    """Get notification statistics for the last N hours"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    notify_count = db.scalar(
        select(Log.id).where(
            Log.log_type == "NOTIFY",
            Log.timestamp >= cutoff
        )
    ) or 0
    
    escalate_count = db.scalar(
        select(Log.id).where(
            Log.log_type == "ESCALATE",
            Log.timestamp >= cutoff
        )
    ) or 0
    
    return {
        "period_hours": hours,
        "notifications_sent": notify_count,
        "escalations_triggered": escalate_count,
        "batched_pending": len(_notification_batch)
    }
