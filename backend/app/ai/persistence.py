# AI Persistence utilities
# References:
# - see docs/08_ai_behavior_rules.txt §6 Rule Persistence
# - see docs/14_ai_engine_design.txt §1(b) Rules Processor, §1(f) Feedback Processor
# - see docs/07_database_design.txt §2(d) AI_Rules

from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import AIRule
from typing import Any, cast


def load_rules(db: Session) -> list[AIRule]:
    # 08 §6: Rules are stored in PostgreSQL and loaded at startup/when needed
    return db.query(AIRule).all()


def update_rule_timestamp(db: Session, rule: AIRule) -> None:
    rule.last_updated = cast(Any, datetime.now(tz=timezone.utc))
    db.add(rule)
    db.commit()


def persist_rule(db: Session, rule: AIRule) -> AIRule:
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
