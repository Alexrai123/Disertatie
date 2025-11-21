# Decision Maker
# References:
# - see docs/08_ai_behavior_rules.txt §3 Action Determination, §5 Escalation Rules
# - see docs/14_ai_engine_design.txt §1(c) Decision Maker
# Note: Escalation timing and automated actions are Not documented in the provided files.

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Decision:
    severity: str
    action: str  # descriptive action per docs (log, notify, suggest, automated if critical)


def decide(severity: str) -> Decision:
    # Map severity to actions as per 08_ai_behavior_rules.txt §3
    if severity == "Low":
        return Decision(severity=severity, action="Log event only")
    if severity == "Medium":
        return Decision(severity=severity, action="Notify Admin")
    if severity == "High":
        return Decision(severity=severity, action="Notify Admin and suggest action")
    if severity == "Critical":
        return Decision(severity=severity, action="Notify Admin and prepare automated action if no response")
    # Default safe fallback
    return Decision(severity="Low", action="Log event only")
