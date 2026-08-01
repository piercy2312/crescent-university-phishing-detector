"""
checks.py
---------
One small function per rule ID from rules_config.json.
"""

import re
from urllib.parse import urlsplit

from config import (
    ALLOWED_EMAIL_DOMAINS,
    ALLOWED_LANDING_DOMAINS,
    IMPERSONATION_KEYWORDS,
    SUSPICIOUS_TLDS,
    URGENCY_CREDENTIAL_PATTERN,
)

IP_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


def check_E1_sender_display_name_mismatch(sample):
    display_name = (sample.get("from_display_name") or "").lower()
    domain = sample.get("from_domain", "")
    implies_official = any(kw in display_name for kw in IMPERSONATION_KEYWORDS)
    domain_is_allowed = any(domain == d or domain.endswith("." + d) for d in ALLOWED_EMAIL_DOMAINS)
    return implies_official and not domain_is_allowed


def check_E2_urgency_credential_language(sample):
    text = f"{sample.get('subject', '')} {sample.get('body', '')}".lower()
    return re.search(URGENCY_CREDENTIAL_PATTERN, text, re.IGNORECASE) is not None


def check_E3_reply_to_mismatch(sample):
    reply_domain = sample.get("reply_to_domain", "")
    from_domain = sample.get("from_domain", "")
    if not reply_domain:
        return False
    return reply_domain != from_domain


def check_U1_ip_host(sample):
    return bool(IP_PATTERN.match(sample.get("host", "")))


def check_U2_at_sign(sample):
    return sample.get("has_at_sign", False)


def check_U3_lookalike_domain(sample):
    host = sample.get("host", "")
    domain_is_allowed = any(host == d or host.endswith("." + d) for d in ALLOWED_LANDING_DOMAINS)
    brand_token_present = "crescent" in host
    return brand_token_present and not domain_is_allowed


def check_U4_excessive_subdomains(sample):
    host = sample.get("host", "")
    if not host or IP_PATTERN.match(host):
        return False
    labels = host.split(".")
    return len(labels) > 3


def check_U5_no_https(sample):
    return sample.get("scheme", "") != "https"


def check_U6_suspicious_tld(sample):
    host = sample.get("host", "")
    return any(host.endswith(tld) for tld in SUSPICIOUS_TLDS)


def check_L1_cross_domain_form_action(sample):
    action_host = sample.get("form_action_host")
    if action_host is None:
        return False
    return action_host != sample.get("declared_host", "")


def check_L2_hidden_fields_present(sample):
    return len(sample.get("hidden_fields", [])) > 0


def check_L3_host_not_allowlisted(sample):
    host = sample.get("declared_host", "")
    return not any(host == d or host.endswith("." + d) for d in ALLOWED_LANDING_DOMAINS)


RULE_CHECKS = {
    "E1": check_E1_sender_display_name_mismatch,
    "E2": check_E2_urgency_credential_language,
    "E3": check_E3_reply_to_mismatch,
    "U1": check_U1_ip_host,
    "U2": check_U2_at_sign,
    "U3": check_U3_lookalike_domain,
    "U4": check_U4_excessive_subdomains,
    "U5": check_U5_no_https,
    "U6": check_U6_suspicious_tld,
    "L1": check_L1_cross_domain_form_action,
    "L2": check_L2_hidden_fields_present,
    "L3": check_L3_host_not_allowlisted,
}
