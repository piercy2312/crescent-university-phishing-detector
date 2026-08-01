"""
engine.py
---------
Part B: the rule execution engine.
"""

from checks import RULE_CHECKS
from config import THRESHOLDS


def evaluate_sample(sample, rule_base):
    stage = sample["stage"]
    score = 0
    fired = []

    for rule in rule_base:
        if rule["stage"] != stage:
            continue
        check_fn = RULE_CHECKS[rule["id"]]
        if check_fn(sample):
            score += rule["weight"]
            fired.append(rule["id"])

    threshold = THRESHOLDS[stage]
    verdict = "PHISHING" if score >= threshold else "LEGITIMATE"

    return {
        "id": sample["id"],
        "stage": stage,
        "score": score,
        "threshold": threshold,
        "fired_rules": fired,
        "verdict": verdict,
    }


def evaluate_batch(samples, rule_base):
    return [evaluate_sample(s, rule_base) for s in samples]
