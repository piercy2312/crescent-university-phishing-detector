#!/usr/bin/env python3
"""
submission_logger.py
--------------------
LOCAL-ONLY mock portal + submission listener for the controlled lab.

Two jobs:
  1. Serves a fictional "Crescent University" student-portal login page in the
     browser (GET /), so you can SEE and screenshot the simulated site.
  2. Records the moment a "credential" is submitted (POST /collect) for the
     Mitigation Success Rate metric. It logs field NAMES, timestamp and source
     only - never the actual values typed.

Everything binds to 127.0.0.1 (this machine only). Nothing leaves the VM.

Run it, then open the printed URL in the VM's browser:

    python scripts/submission_logger.py
    ->  http://127.0.0.1:5000/
"""

import csv
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submission_log.csv")
HOST = "127.0.0.1"
PORT = 5000

# The mock portal page. Fictional university, lab use only. The form posts back
# to /collect on this same local server so a submission can be logged for metrics.
PORTAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crescent University - Student Portal Login</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; background:#0b3d2e; margin:0; }
    .bar { background:#08301f; color:#fff; padding:14px 22px; font-size:18px; font-weight:bold; }
    .wrap { max-width:380px; margin:60px auto; background:#fff; border-radius:8px;
            box-shadow:0 6px 24px rgba(0,0,0,.25); overflow:hidden; }
    .head { background:#0b3d2e; color:#fff; text-align:center; padding:22px 16px; }
    .head h1 { font-size:18px; margin:6px 0 2px; }
    .head p { font-size:12px; margin:0; opacity:.85; }
    form { padding:22px; }
    label { display:block; font-size:13px; color:#333; margin:12px 0 4px; }
    input { width:100%; padding:10px; border:1px solid #ccc; border-radius:4px; box-sizing:border-box; }
    button { width:100%; margin-top:18px; padding:11px; background:#c9a227; color:#08301f;
             font-weight:bold; border:0; border-radius:4px; cursor:pointer; font-size:15px; }
    .note { text-align:center; font-size:11px; color:#888; padding:0 22px 20px; }
    .lab { background:#fff8e1; color:#8a6d00; font-size:11px; text-align:center; padding:6px; }
  </style>
</head>
<body>
  <div class="bar">Crescent University</div>
  <div class="lab">LAB SIMULATION - fictional portal, synthetic data only, not a real login</div>
  <div class="wrap">
    <div class="head">
      <h1>Student Portal</h1>
      <p>Sign in with your matric number</p>
    </div>
    <form action="/collect" method="POST">
      <label>Matric Number</label>
      <input type="text" name="username" placeholder="e.g. CU/20/1234" autocomplete="off">
      <label>Password</label>
      <input type="password" name="password" autocomplete="off">
      <button type="submit">Sign in</button>
    </form>
    <div class="note">This page is part of a controlled final-year phishing-detection study.</div>
  </div>
</body>
</html>
"""

CONFIRM_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Recorded</title></head><body style="font-family:Arial;text-align:center;padding:60px;">
<h3>Submission recorded locally for lab metrics.</h3>
<p style="color:#888;font-size:13px;">No password value was stored - only the field names, time and source.</p>
<p><a href="/">Back to the portal</a></p></body></html>
"""


def ensure_log_header():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="") as f:
            csv.writer(f).writerow(
                ["timestamp_iso", "remote_addr", "path", "fields_received", "blocked_by_detector"])


class PortalHandler(BaseHTTPRequestHandler):
    def _send(self, body, status=200, ctype="text/html"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body.encode("utf-8") if isinstance(body, str) else body)

    def _log_row(self, fields_received, blocked_flag):
        with open(LOG_PATH, "a", newline="") as f:
            csv.writer(f).writerow(
                [datetime.now(timezone.utc).isoformat(), self.client_address[0],
                 self.path, fields_received, blocked_flag])

    def do_GET(self):
        if self.path in ("/", "/portal", "/index.html"):
            self._send(PORTAL_HTML)
        elif self.path == "/health":
            self._send("submission_logger.py is running.\n", ctype="text/plain")
        else:
            self._send("Not found. Open http://127.0.0.1:5000/ for the portal.\n",
                       status=404, ctype="text/plain")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        parsed = parse_qs(body)
        field_names = ",".join(sorted(parsed.keys()))
        blocked_flag = self.headers.get("X-Detector-Stage", "")
        self._log_row(field_names, blocked_flag)
        self._send(CONFIRM_HTML)

    def log_message(self, *args):
        pass


def main():
    ensure_log_header()
    server = ThreadingHTTPServer((HOST, PORT), PortalHandler)
    print(f"Mock portal running.  Open this in the VM browser:  http://{HOST}:{PORT}/")
    print(f"Submissions logged to: {LOG_PATH}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        server.server_close()


if __name__ == "__main__":
    main()
