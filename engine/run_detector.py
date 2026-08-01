"""
run_detector.py - loads Stage-1 samples, runs the engine, writes results + accuracy summary.
Run from inside detector/: python run_detector.py
"""

import csv
import json
import os

from engine import evaluate_batch
from parsers import load_emails_from_folder, load_landing_pages_from_manifest, load_urls_from_csv

HERE = os.path.dirname(os.path.abspath(__file__))
ATTACK_SIM_ROOT = os.path.dirname(HERE)  # PhishingProject/


def load_rule_base():
    with open(os.path.join(os.path.dirname(HERE), "rules", "rules_config.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_email_ground_truth():
    truth = {}
    with open(os.path.join(ATTACK_SIM_ROOT, "samples", "emails", "labels.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            truth[row["filename"]] = row["label"]
    return truth


def load_landing_page_ground_truth():
    truth = {}
    with open(os.path.join(ATTACK_SIM_ROOT, "samples", "pages", "labels.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            truth[row["filename"]] = row["label"]
    return truth


def to_binary(label):
    return "PHISHING" if label.lower() == "phishing" else "LEGITIMATE"


def main():
    rule_base = load_rule_base()
    email_samples = load_emails_from_folder(os.path.join(ATTACK_SIM_ROOT, "samples", "emails"))
    url_samples, url_ground_truth = load_urls_from_csv(os.path.join(ATTACK_SIM_ROOT, "samples", "urls", "urls.csv"))
    landing_samples = load_landing_pages_from_manifest(
        os.path.join(ATTACK_SIM_ROOT, "samples", "pages"), os.path.join(os.path.dirname(HERE), "rules", "landing_pages_manifest.json"))

    email_ground_truth = load_email_ground_truth()
    landing_ground_truth = load_landing_page_ground_truth()

    all_samples = email_samples + url_samples + landing_samples
    results = evaluate_batch(all_samples, rule_base)

    for r in results:
        if r["stage"] == "email":
            truth = email_ground_truth.get(r["id"])
        elif r["stage"] == "url":
            truth = url_ground_truth.get(r["id"])
        else:
            truth = landing_ground_truth.get(r["id"])
        r["ground_truth"] = truth
        r["correct"] = (truth is not None) and (to_binary(truth) == r["verdict"])

    out_path = os.path.join(HERE, "results.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["stage", "id", "score", "threshold", "verdict", "ground_truth", "correct", "fired_rules"])
        for r in results:
            writer.writerow([r["stage"], r["id"], r["score"], r["threshold"], r["verdict"], r["ground_truth"], r["correct"], ";".join(r["fired_rules"])])

    print(f"Evaluated {len(results)} samples. Full log written to results.csv\n")
    for stage in ["email", "url", "landing_page"]:
        stage_results = [r for r in results if r["stage"] == stage]
        labelled = [r for r in stage_results if r["ground_truth"] is not None]
        correct = sum(1 for r in labelled if r["correct"])
        total = len(labelled)
        acc = (correct / total * 100) if total else 0
        print(f"[{stage}] {correct}/{total} correct ({acc:.0f}%)")

    print("\nDetail:")
    for r in results:
        print(f"  {r['stage']:<14} {r['id']:<45} score={r['score']:<3} -> {r['verdict']:<10} (truth: {r['ground_truth']}) fired={r['fired_rules']}")


if __name__ == "__main__":
    main()
