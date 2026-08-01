"""
generate_emails.py - generates a larger SYNTHETIC email dataset via templates,
for Crescent University (fictional). No real people, no scraped content.
"""

import os
import random

random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "emails")
LEGIT_DOMAIN = "crescentuniversity.edu.ng"

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

    reply_to_line = ""
    if idx % 5 == 0:
        reply_to_line = f"Reply-To: {category.lower()}@attacker-relay-{idx}.tk\n"

    content = (
        f'From: "{display_name}" <{from_addr}>\n'
        f"To: student{idx}@{LEGIT_DOMAIN}\n"
        f"Subject: {subject}\n"
        f"{reply_to_line}"
        f"Date: Mon, 01 Jul 2024 09:00:{idx % 60:02d} +0000\n"
        f"Message-ID: <gen-phish-{idx}@{domain}>\n\n"
        f"Dear Student,\n\n{body}\n\nRegards,\n{display_name}\n"
    )
    fname = f"gen_phish_{idx:03d}_{category.lower()}.eml"
    return fname, content


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
    fname = f"gen_legit_{idx:03d}_{category.lower()}.eml"
    return fname, content


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    label_rows = []
    idx = 1
    for _pass in range(2):
        for scenario in PHISH_SCENARIOS:
            fname, content = make_phish_email(idx, scenario)
            with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
                f.write(content)
            label_rows.append((fname, "phishing"))
            idx += 1
        for scenario in LEGIT_SCENARIOS:
            fname, content = make_legit_email(idx, scenario)
            with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
                f.write(content)
            label_rows.append((fname, "legitimate"))
            idx += 1

    labels_path = os.path.join(OUT_DIR, "labels.csv")
    with open(labels_path, "a", encoding="utf-8") as f:
        for fname, label in label_rows:
            f.write(f"{fname},{label},generated (templated synthetic sample)\n")

    print(f"Generated {len(label_rows)} new email samples in {OUT_DIR}")


if __name__ == "__main__":
    main()
