"""
stress_test/run_stress_test.py - hand-crafted samples designed to evade the current rule base.
Run from inside detector/: python stress_test/run_stress_test.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import evaluate_sample
from parsers import parse_landing_page, parse_url

HERE = os.path.dirname(os.path.abspath(__file__))
DETECTOR_DIR = os.path.dirname(HERE)


def load_rule_base():
    rules_path = os.path.join(os.path.dirname(DETECTOR_DIR), "rules", "rules_config.json")
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    rule_base = load_rule_base()

    email_sample = {
        "id": "evasion_email_soft_impersonation", "stage": "email",
        "from_display_name": "Crescent ICT", "from_address": "helpdesk@crescent-support-desk.io",
        "from_domain": "crescent-support-desk.io", "reply_to_domain": "",
        "subject": "Course document ready for your review",
        "body": ("Hi, when you have a moment, could you take a look at the "
                  "attached course document and let me know your thoughts? No rush - whenever suits you this week."),
    }

    url_sample = parse_url("https://secure-student-login.io/account")

    landing_sample = parse_landing_page(
        os.path.join(HERE, "evasion_js_exfil.html"), declared_host="portal.crescentuniversity.edu.ng")

    print("=== Stress test: samples designed to EVADE the current rules ===\n")
    for sample in [email_sample, url_sample, landing_sample]:
        result = evaluate_sample(sample, rule_base)
        print(f"[{result['stage']}] {result['id']}")
        print(f"    score={result['score']}  threshold={result['threshold']}  verdict={result['verdict']}  fired={result['fired_rules']}")
        print(f"    (this sample IS phishing, but the rule base was scored/weighted before seeing it)\n")


if __name__ == "__main__":
    main()
