"""
generate_urls.py - generates a larger SYNTHETIC URL dataset for Crescent University.
"""

import os
import random

random.seed(42)

OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "urls", "urls.csv")

SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".work"]
BRAND_TOKENS = ["crescent", "crescentuni", "crescent-uni"]
LOOKALIKE_PREFIXES = ["secure-", "login-", "verify-", "student-", "id-", "portal-", ""]
LOOKALIKE_SUFFIXES = ["-login", "-verify", "-portal", "-secure", "-alerts", ""]

LEGIT_SUBDOMAINS = ["portal", "drive", "support", "registrar", "bursary", "library", "exams", "hostel", "mail", "elearning"]
LEGIT_DOMAIN = "crescentuniversity.edu.ng"
LEGIT_EXTERNAL = [
    "https://www.wikipedia.org/wiki/Security", "https://accounts.google.com/signin",
    "https://outlook.office.com/mail", "https://www.microsoft.com/en-us/security",
    "https://slack.com/signin", "https://zoom.us/signin",
]


def rand_ip():
    base = random.choice(["198.51.100.", "203.0.113."])
    return base + str(random.randint(2, 250))


def make_phishing_url(idx):
    pattern = idx % 6
    brand = random.choice(BRAND_TOKENS)
    if pattern == 0:
        return f"http://{rand_ip()}/login/verify?id={idx}", "ip_address_host"
    elif pattern == 1:
        return f"http://{LEGIT_DOMAIN}@{brand}-verify-{idx}.tk/reset", "at_sign_obfuscation"
    elif pattern == 2:
        prefix = random.choice(LOOKALIKE_PREFIXES)
        suffix = random.choice(LOOKALIKE_SUFFIXES)
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"http://{prefix}{brand}{suffix}{tld}/account", "lookalike_domain"
    elif pattern == 3:
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"https://{brand}-portal{tld}/docs/view?id={idx}", "lookalike_domain"
    elif pattern == 4:
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"http://login.secure.{brand}-id{tld}/verify", "excessive_subdomains"
    else:
        return f"http://{rand_ip()}:{random.choice([8080, 8443, 9090])}/verify", "ip_address_host"


def make_legit_url(idx):
    if idx % 4 == 0:
        return random.choice(LEGIT_EXTERNAL), "external_reputable"
    sub = random.choice(LEGIT_SUBDOMAINS)
    return f"https://{sub}.{LEGIT_DOMAIN}/resource/{idx}", "internal_domain"


def main():
    rows = []
    for idx in range(1, 51):
        url, pattern = make_phishing_url(idx)
        rows.append((url, "phishing", pattern, "generated synthetic sample"))
    for idx in range(1, 41):
        url, pattern = make_legit_url(idx)
        rows.append((url, "legitimate", pattern, "generated synthetic sample"))

    with open(OUT_PATH, "a", encoding="utf-8") as f:
        for url, label, pattern, note in rows:
            f.write(f'{url},{label},{pattern},"{note}"\n')

    print(f"Appended {len(rows)} new URL rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
