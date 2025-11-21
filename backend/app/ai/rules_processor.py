# Rules Processor
# References:
# - see docs/08_ai_behavior_rules.txt §2 Event Evaluation, §3 Action Determination
# - see docs/14_ai_engine_design.txt §1(b) Rules Processor
# Enhanced with caching and weighted severity calculation

from __future__ import annotations
import time
from typing import Optional
from sqlalchemy.orm import Session
from ..models import AIRule, Event
from .persistence import load_rules


class RuleEvaluationResult:
    def __init__(self, severity: str = "Low", matched_rule_id: Optional[int] = None, confidence: float = 0.5):
        self.severity = severity
        self.matched_rule_id = matched_rule_id
        self.confidence = confidence  # 0.0 to 1.0


# Rule cache with TTL
_rule_cache: dict[str, tuple[list[AIRule], float]] = {}
_cache_ttl = 60  # seconds


def _get_cached_rules(db: Session) -> list[AIRule]:
    """Get rules from cache or database with TTL"""
    cache_key = "all_rules"
    now = time.time()
    
    if cache_key in _rule_cache:
        rules, timestamp = _rule_cache[cache_key]
        if now - timestamp < _cache_ttl:
            # Merge cached rules into current session to avoid DetachedInstanceError
            return [db.merge(rule) for rule in rules]
    
    # Cache miss or expired - reload from database
    rules = load_rules(db)
    _rule_cache[cache_key] = (rules, now)
    return rules


def clear_rule_cache():
    """Clear the rule cache (call when rules are updated)"""
    _rule_cache.clear()


def evaluate_event(db: Session, event: Event) -> RuleEvaluationResult:
    """
    Evaluate event against rules to determine severity with weighted scoring.
    
    Enhanced algorithm:
    - Uses cached rules for performance
    - Calculates weighted severity based on multiple factors
    - Considers event type, adaptive rules, and rule priority
    - Returns confidence score for the decision
    """
    rules: list[AIRule] = _get_cached_rules(db)
    
    # Severity order and weights
    severity_order = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    
    # Default result
    best_result = RuleEvaluationResult(severity="Medium", matched_rule_id=None, confidence=0.3)
    
    if not rules:
        return best_result
    
    # Score each rule
    scores: list[tuple[AIRule, float]] = []
    
    for rule in rules:
        if not rule.severity_level or rule.severity_level not in severity_order:
            continue
        
        # Base score from severity level
        base_score = severity_order[rule.severity_level]
        
        # Boost for adaptive rules (they've been trained)
        adaptive_boost = 1.2 if rule.adaptive_flag else 1.0
        
        # Event type matching (if rule has action_type that matches event type)
        event_match_boost = 1.1 if (rule.action_type and event.event_type in rule.action_type.lower()) else 1.0
        
        # Calculate final score
        final_score = base_score * adaptive_boost * event_match_boost
        scores.append((rule, final_score))
    
    if not scores:
        return best_result
    
    # Get the highest scoring rule
    best_rule, best_score = max(scores, key=lambda x: x[1])
    
    # Calculate confidence based on score distribution
    max_possible_score = 4 * 1.2 * 1.1  # Critical * adaptive * event_match
    confidence = min(best_score / max_possible_score, 1.0)
    
    return RuleEvaluationResult(
        severity=best_rule.severity_level or "Medium",
        matched_rule_id=best_rule.id,
        confidence=confidence
    )


def get_rule_statistics(db: Session) -> dict:
    """Get statistics about rules for monitoring"""
    rules = _get_cached_rules(db)
    
    severity_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    adaptive_count = 0
    
    for rule in rules:
        if rule.severity_level in severity_counts:
            severity_counts[rule.severity_level] += 1
        if rule.adaptive_flag:
            adaptive_count += 1
    
    return {
        "total_rules": len(rules),
        "adaptive_rules": adaptive_count,
        "severity_distribution": severity_counts,
        "cache_size": len(_rule_cache)
    }
