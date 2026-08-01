"""
config.py
---------
Ground-truth reference data the rules check against, and the score
thresholds that decide PHISHING vs LEGITIMATE per stage.
"""

ALLOWED_EMAIL_DOMAINS = [
    "crescentuniversity.edu.ng",
]

ALLOWED_LANDING_DOMAINS = [
    "crescentuniversity.edu.ng",
]

SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".work"]

IMPERSONATION_KEYWORDS = [
    "ict", "it-", "security", "bursary", "registrar", "support", "crescent", "exam",
    "scholarship", "hostel", "chancellor", "academic", "library", "affairs",
    "convocation", "union", "records", "office", "student", "portal", "helpdesk",
]

URGENCY_CREDENTIAL_PATTERN = (
    r"(verify|suspend|confirm your password|urgent|immediately|"
    r"24 hours|re-?confirm|reset your (password|mfa)|sign in (immediately|now)|"
    r"account will be (suspended|locked)|login credentials)"
)

THRESHOLDS = {
    "email": 4,
    "url": 4,
    "landing_page": 4,
}
