# AI Rules router
# References:
# - see docs/02_functional_req.txt §1 (Admin manages rules)
# - see docs/08_ai_behavior_rules.txt (rules semantics and adaptation)
# - see docs/07_database_design.txt §2(d) AI_Rules

from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import AIRule
from ..schemas import AIRuleCreate, AIRuleOut
from ..auth import require_admin
from typing import Any, cast

router = APIRouter()


@router.get("/", response_model=list[AIRuleOut])
def list_ai_rules(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(AIRule).all()


@router.post("/", response_model=AIRuleOut)
def create_ai_rule(payload: AIRuleCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rule = AIRule(
        rule_name=payload.rule_name,
        description=payload.description,
        severity_level=payload.severity_level,
        action_type=payload.action_type,
        adaptive_flag=payload.adaptive_flag,
        stored_in_engine=False,
        last_updated=cast(Any, datetime.now(tz=timezone.utc)),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=AIRuleOut)
def update_ai_rule(rule_id: int, payload: AIRuleCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rule = db.get(AIRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.rule_name = payload.rule_name
    rule.description = payload.description
    rule.severity_level = payload.severity_level
    rule.action_type = payload.action_type
    rule.adaptive_flag = payload.adaptive_flag
    rule.last_updated = cast(Any, datetime.now(tz=timezone.utc))
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
def delete_ai_rule(rule_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    rule = db.get(AIRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"status": "deleted"}
