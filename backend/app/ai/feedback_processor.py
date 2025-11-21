# Feedback Processor
# References:
# - see docs/08_ai_behavior_rules.txt §4 Feedback Adaptation
# - see docs/14_ai_engine_design.txt §1(f) Feedback Processor
# - see docs/07_database_design.txt §2(f) AI_Feedback
# Enhanced with actual adaptive learning

from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from ..models import AIFeedback, Event, AIRule, Log
from .persistence import update_rule_timestamp
from .rules_processor import clear_rule_cache


def submit_feedback(
    db: Session,
    *,
    event: Event,
    admin_id: int,
    feedback_type: str,  # approve/reject/modify per docs
    comment: Optional[str] = None,
    rule: Optional[AIRule] = None,
    suggested_severity: Optional[str] = None,
) -> AIFeedback:
    """
    Submit admin feedback and adapt AI rules based on the feedback.
    
    Adaptive learning:
    - If admin approves: Mark rule as adaptive (trusted)
    - If admin rejects: Adjust rule or create counter-example
    - If admin modifies: Update rule severity based on suggestion
    """
    # Persist feedback (07 §2(f))
    fb = AIFeedback(
        event_id=event.id,
        admin_id=admin_id,
        feedback_type=feedback_type,
        comment=comment,
        timestamp=datetime.now(tz=timezone.utc),
        suggested_severity=suggested_severity,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    # Log feedback (08 §8 Logging, 14 §1(e) Logging Module)
    log = Log(
        log_type="AI_FEEDBACK",
        message=f"Feedback on event {event.id}: type={feedback_type}; comment={comment}; rule={(rule.id if rule else None)}",
        related_event_id=event.id,
    )
    db.add(log)
    db.commit()

    # Adaptive learning based on feedback type
    if rule is not None:
        _adapt_rule(db, rule, feedback_type, suggested_severity, event)
        update_rule_timestamp(db, rule)
        
        # Clear cache so new rules take effect immediately
        clear_rule_cache()

    return fb


def _adapt_rule(
    db: Session,
    rule: AIRule,
    feedback_type: str,
    suggested_severity: Optional[str],
    event: Event
):
    """
    Adapt rule based on admin feedback.
    
    Learning strategy:
    - approve: Mark rule as adaptive (increase confidence)
    - reject: Decrease rule priority or create exception
    - modify: Update rule severity to suggested value
    """
    if feedback_type == "approve":
        # Admin approved the decision - mark rule as adaptive
        if not rule.adaptive_flag:
            rule.adaptive_flag = True
            db.add(Log(
                log_type="AI_LEARNING",
                message=f"Rule {rule.id} marked as adaptive after approval",
                related_event_id=event.id
            ))
            db.commit()
    
    elif feedback_type == "reject":
        # Admin rejected the decision - this rule may be too aggressive
        # Create a log for analysis, but don't auto-disable (admin should review)
        db.add(Log(
            log_type="AI_LEARNING",
            message=f"Rule {rule.id} rejected by admin - may need adjustment",
            related_event_id=event.id
        ))
        db.commit()
        
        # If this rule has been rejected multiple times, consider lowering severity
        rejection_count = db.scalar(
            select(func.count()).select_from(AIFeedback).where(
                AIFeedback.feedback_type == "reject"
            )
        ) or 0
        
        if rejection_count >= 3 and rule.severity_level in ["High", "Critical"]:
            # Auto-adjust: Lower severity one level
            severity_downgrade = {
                "Critical": "High",
                "High": "Medium",
                "Medium": "Low"
            }
            old_severity = rule.severity_level
            rule.severity_level = severity_downgrade.get(old_severity, old_severity)
            
            db.add(Log(
                log_type="AI_LEARNING",
                message=f"Rule {rule.id} severity auto-adjusted from {old_severity} to {rule.severity_level} after multiple rejections",
                related_event_id=event.id
            ))
            db.commit()
    
    elif feedback_type == "modify" and suggested_severity:
        # Admin provided a better severity level - learn from it
        old_severity = rule.severity_level
        rule.severity_level = suggested_severity
        rule.adaptive_flag = True  # Mark as adaptive since admin corrected it
        
        db.add(Log(
            log_type="AI_LEARNING",
            message=f"Rule {rule.id} severity updated from {old_severity} to {suggested_severity} based on admin feedback",
            related_event_id=event.id
        ))
        db.commit()


def get_feedback_statistics(db: Session) -> dict:
    """Get statistics about feedback for monitoring AI learning"""
    total_feedback = db.scalar(select(func.count()).select_from(AIFeedback)) or 0
    
    approve_count = db.scalar(
        select(func.count()).select_from(AIFeedback).where(AIFeedback.feedback_type == "approve")
    ) or 0
    
    reject_count = db.scalar(
        select(func.count()).select_from(AIFeedback).where(AIFeedback.feedback_type == "reject")
    ) or 0
    
    modify_count = db.scalar(
        select(func.count()).select_from(AIFeedback).where(AIFeedback.feedback_type == "modify")
    ) or 0
    
    # Calculate approval rate (AI accuracy)
    approval_rate = (approve_count / total_feedback * 100) if total_feedback > 0 else 0
    
    return {
        "total_feedback": total_feedback,
        "approvals": approve_count,
        "rejections": reject_count,
        "modifications": modify_count,
        "approval_rate": round(approval_rate, 2)
    }
