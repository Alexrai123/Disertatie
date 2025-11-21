# Action Executor
# References:
# - see docs/08_ai_behavior_rules.txt §3 Action Determination (automated for Critical if no response)
# - see docs/14_ai_engine_design.txt §1(c) Decision Maker (actions include quarantine, alerts, logging)
# Note: Concrete system actions (quarantine, backups) are Not documented in the provided files.
#       We record intended actions in the Logs table without performing host-level mutations.

from __future__ import annotations
from sqlalchemy.orm import Session
from ..models import Log


def prepare_automated_action(db: Session, event_id: int, description: str) -> None:
    """
    Record a preparation for an automated action. This does not execute OS-level changes.
    """
    log = Log(
        log_type="ACTION_PREPARED",
        message=f"Prepared automated action for event {event_id}: {description}",
        related_event_id=event_id,
    )
    db.add(log)
    db.commit()
