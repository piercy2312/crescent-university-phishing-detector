"""
run_experiment.py - Stage 4: full experiment with timing, multiple runs, mitigation.
Run from inside detector/: python run_experiment.py
"""

import csv
import json
import os
import time

from engine import evaluate_batch
from mitigation import apply_mitigation_batch
from parsers import load_emails_from_folder, load_landing_pages_from_manifest, load_urls_from_csv

HERE = os.path.dirname(os.path.abspath(__file__))
ATTACK_SIM_ROOT = os.path.dirname(HERE)  # PhishingProject/
NUM_RUNS = 20


def load_rule_base():
    with open(os.path.join(os.path.dirname(HERE), "rules", "rules_config.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def load_ground_truth(csv_path):
    truth = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            truth[row["filename"]] = row["label"]
    return truth


def to_binary(label):
    return "PHISHING" if label.lower() == "phishing" else "LEGITIMATE"


def load_all_samples():
    email_samples = load_emails_from_folder(os.path.join(ATTACK_SIM_ROOT, "samples", "emails"))
    url_samples, url_ground_truth = load_urls_from_csv(os.path.join(ATTACK_SIM_ROOT, "samples", "urls", "urls.csv"))
    landing_samples = load_landing_pages_from_manifest(
        os.path.join(ATTACK_SIM_ROOT, "samples", "pages"), os.path.join(os.path.dirname(HERE), "rules", "landing_pages_manifest.json"))
    email_ground_truth = load_ground_truth(os.path.join(ATTACK_SIM_ROOT, "samples", "emails", "labels.csv"))
    landing_ground_truth = load_ground_truth(os.path.join(ATTACK_SIM_ROOT, "samples", "pages", "labels.csv"))

    all_samples = email_samples + url_samples + landing_samples
    ground_truth_lookup = {}
    ground_truth_lookup.update({s["id"]: email_ground_truth.get(s["id"]) for s in email_samples})
    ground_truth_lookup.update(url_ground_truth)
    ground_truth_lookup.update({s["id"]: landing_ground_truth.get(s["id"]) for s in landing_samples})
    return all_samples, ground_truth_lookup


def run_one_pass(samples, rule_base, ground_truth_lookup, run_number):
    rows = []
    for sample in samples:
        time_in = time.perf_counter()
        result = evaluate_batch([sample], rule_base)[0]
        result = apply_mitigation_batch([result])[0]
        time_out = time.perf_counter()
        truth = ground_truth_lookup.get(result["id"])
        correct = (truth is not None) and (to_binary(truth) == result["verdict"])
        rows.append({
            "run": run_number, "stage": result["stage"], "id": result["id"], "true_label": truth,
            "verdict": result["verdict"], "score": result["score"], "threshold": result["threshold"],
            "fired_rules": ";".join(result["fired_rules"]), "blocked": result["blocked"], "action": result["action"],
            "correct": correct, "time_in": time_in, "time_out": time_out,
            "response_time_ms": (time_out - time_in) * 1000,
        })
    return rows


def main():
    rule_base = load_rule_base()
    samples, ground_truth_lookup = load_all_samples()

    all_rows = []
    for run_number in range(1, NUM_RUNS + 1):
        all_rows.extend(run_one_pass(samples, rule_base, ground_truth_lookup, run_number))

    raw_path = os.path.join(HERE, "results_raw.csv")
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["run", "stage", "id", "true_label", "verdict", "score", "threshold", "fired_rules", "blocked", "action", "correct", "time_in", "time_out", "response_time_ms"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    per_sample = {}
    for row in all_rows:
        sid = row["id"]
        if sid not in per_sample:
            per_sample[sid] = {k: row[k] for k in ["stage", "id", "true_label", "verdict", "score", "threshold", "fired_rules", "blocked", "action", "correct"]}
            per_sample[sid]["response_times_ms"] = []
        per_sample[sid]["response_times_ms"].append(row["response_time_ms"])

    results_path = os.path.join(HERE, "results.csv")
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["stage", "id", "true_label", "verdict", "score", "threshold", "fired_rules", "blocked", "action", "correct", "avg_response_time_ms", "num_runs"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sid, data in per_sample.items():
            times = data.pop("response_times_ms")
            data["avg_response_time_ms"] = sum(times) / len(times)
            data["num_runs"] = len(times)
            writer.writerow(data)

    print(f"Ran {NUM_RUNS} passes over {len(samples)} samples ({len(all_rows)} total evaluations).")
    print(f"Raw per-run data written to: {raw_path}")
    print(f"Aggregated per-sample data written to: {results_path}")
    print("\nNext: run 'python metrics.py' to compute Detection Rate, FPR, Response Time and Mitigation Success Rate.")


if __name__ == "__main__":
    main()
