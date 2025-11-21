# Event Listener
# References:
# - see docs/14_ai_engine_design.txt §1(a) Event Listener
# - see docs/08_ai_behavior_rules.txt §2 Event Evaluation (downstream)
# Note: Actual OS-level filesystem watching is Not documented in the provided files.
#       This listener acts as an orchestrator invoked when an Event is recorded via the API.

from __future__ import annotations
from sqlalchemy.orm import Session
from ..models import Event, Log
from .rules_processor import evaluate_event
from .decision_maker import decide
from .notifications import notify_admins, escalate_if_needed
from .action_executor import prepare_automated_action
from fastapi import BackgroundTasks


def handle_event(db: Session, event: Event, background_tasks: BackgroundTasks | None = None) -> None:
    """
    Orchestrate event processing:
    - Evaluate severity via Rules Processor (08 §2)
    - Determine action via Decision Maker (08 §3)
    - Log the decision (14 §1(e) Logging Module; 02 §2 System Monitoring)
    - Notify Admins for Medium/High/Critical (08 §3)
    - Escalation flag for High/Critical (08 §5)
    - Prepare automated action for Critical if no response (record intent only) (08 §3)
    """
    eval_result = evaluate_event(db, event)
    decision = decide(eval_result.severity)

    log = Log(
        log_type="AI_DECISION",
        message=f"Event {event.id}: severity={eval_result.severity}; action={decision.action}; rule={eval_result.matched_rule_id}",
        related_event_id=event.id,
    )
    db.add(log)
    db.commit()

    # Mark event processed flag if only logging; notification/escalation handled in Step 4
    if eval_result.severity == "Low":
        event.processed_flag = True
        db.add(event)
        db.commit()
        return

    # Medium and above: notify admins
    if eval_result.severity in ("Medium", "High", "Critical"):
        notify_admins(db, f"Event {event.id} severity {eval_result.severity}: {decision.action}")
        escalate_if_needed(db, eval_result.severity, event.id, background_tasks=background_tasks)

    # Critical: prepare automated action (no OS effects as per docs)
    if eval_result.severity == "Critical":
        prepare_automated_action(db, event.id, "Automated safe action placeholder")

