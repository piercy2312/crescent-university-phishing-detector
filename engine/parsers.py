"""
parsers.py
----------
Turns each raw Stage-1 artefact into a plain dict with a consistent shape.
"""

import csv
import email
import os
from email import policy
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


def parse_email_file(filepath):
    with open(filepath, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    from_header = msg.get("From", "")
    from_name, from_addr = email.utils.parseaddr(from_header)
    from_domain = from_addr.split("@")[-1].lower() if "@" in from_addr else ""

    reply_to_header = msg.get("Reply-To", "")
    _, reply_to_addr = email.utils.parseaddr(reply_to_header)
    reply_to_domain = reply_to_addr.split("@")[-1].lower() if "@" in reply_to_addr else ""

    subject = msg.get("Subject", "") or ""

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
    else:
        body = msg.get_content()

    return {
        "id": os.path.basename(filepath),
        "stage": "email",
        "from_display_name": from_name,
        "from_address": from_addr,
        "from_domain": from_domain,
        "reply_to_domain": reply_to_domain,
        "subject": subject,
        "body": body,
    }


def load_emails_from_folder(folder):
    samples = []
    for fname in sorted(os.listdir(folder)):
        if fname.endswith(".eml"):
            samples.append(parse_email_file(os.path.join(folder, fname)))
    return samples


def parse_url(raw_url):
    parts = urlsplit(raw_url)
    netloc = parts.netloc
    host_and_port = netloc.split("@")[-1]
    host = host_and_port.split(":")[0].lower()

    return {
        "id": raw_url,
        "stage": "url",
        "raw_url": raw_url,
        "scheme": parts.scheme.lower(),
        "netloc": netloc,
        "host": host,
        "has_at_sign": "@" in netloc,
    }


def load_urls_from_csv(csv_path):
    samples = []
    ground_truth = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample = parse_url(row["url"])
            samples.append(sample)
            ground_truth[sample["id"]] = row["label"]
    return samples, ground_truth


def parse_landing_page(filepath, declared_host):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")

    action_host = None
    if form is not None:
        action = form.get("action", "") or ""
        if action.startswith("http://") or action.startswith("https://"):
            action_host = urlsplit(action).netloc.split(":")[0].lower()

    hidden_fields = []
    if form is not None:
        for inp in form.find_all("input", attrs={"type": "hidden"}):
            hidden_fields.append(inp.get("name", ""))

    return {
        "id": os.path.basename(filepath),
        "stage": "landing_page",
        "declared_host": declared_host.lower(),
        "form_action_host": action_host,
        "hidden_fields": hidden_fields,
    }


def load_landing_pages_from_manifest(folder, manifest_path):
    import json
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    samples = []
    for entry in manifest:
        filepath = os.path.join(folder, entry["filename"])
        samples.append(parse_landing_page(filepath, entry["declared_host"]))
    return samples
