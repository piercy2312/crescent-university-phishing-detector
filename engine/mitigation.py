"""
mitigation.py
-------------
Stage 3: the response layer.
"""

STAGE_ACTIONS = {
    "email": {"PHISHING": "warn_user", "LEGITIMATE": "allow"},
    "url": {"PHISHING": "block_redirect", "LEGITIMATE": "allow"},
    "landing_page": {"PHISHING": "reject_submission", "LEGITIMATE": "allow"},
}


def apply_mitigation(result):
    stage = result["stage"]
    verdict = result["verdict"]
    action = STAGE_ACTIONS[stage][verdict]
    blocked = verdict == "PHISHING"
    result["action"] = action
    result["blocked"] = blocked
    return result


def apply_mitigation_batch(results):
    return [apply_mitigation(r) for r in results]
