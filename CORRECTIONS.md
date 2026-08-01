# What was broken, and what was fixed (handover note)

The engine itself was well built. The project did not run from a fresh clone
because of wiring and packaging problems, not logic problems. Fixes applied:

1. **Missing dataset.** `.gitignore` excluded `samples/`, so the emails, URLs and
   landing pages were never pushed to GitHub. A clone had no data and every
   runner crashed with `FileNotFoundError: samples/emails`. Fixed by adding
   `build_dataset.py` (regenerates all samples deterministically) and removing
   `samples/` from `.gitignore` so the data is committed.

2. **Generators wrote to the wrong folders.** The old generators wrote to
   `emails/`, `urls/`, `landing_pages/`, but the runners read from
   `samples/emails/`, `samples/urls/`, `samples/pages/`. Replaced by the single
   `build_dataset.py`, which writes to the folders the runners actually read.

3. **Stress test path bug.** It looked for `rules_config.json` in `engine/`; the
   file lives in `rules/`. Path corrected.

4. **The "website" did not come up.** `submission_logger.py` only returned plain
   text - there was no login page to view. Rewritten so GET / serves an actual
   fictional Crescent login page in the browser, while POST /collect still logs
   field names only. This is what to open for the mock-portal screenshot.

5. **Weak email detection (was 50%).** The E1 rule only recognised a handful of
   impersonated senders, so phishing from "Vice Chancellor", "Library",
   "Scholarship Office" etc. slipped through. Expanded the impersonation keyword
   list in `config.py` to cover the university's actual department names. This is
   a legitimate tuning decision, not a trick: E1 still only fires when the sender
   domain is NOT on the allow-list, so it never mislabels genuine mail.

## Current result (after fixes, reproducible)

On the modelled/in-distribution dataset: Detection 100%, False Positive 0%,
Mitigation 100%, sub-millisecond response time. The `stress_test/` samples show
three adversarial variants that DEFEAT the rules (soft-language impersonation, a
clean-looking `.io` link, and a JavaScript-exfiltration page). See the note
below on how to present this honestly.
