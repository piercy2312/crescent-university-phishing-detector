"""
metrics.py - Stage 5: compute the four metrics from results.csv, produce table + charts.
Run from inside detector/: python metrics.py
"""

import csv
import os

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(HERE, "results.csv")


def load_results():
    rows = []
    with open(RESULTS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["score"] = int(row["score"])
            row["threshold"] = int(row["threshold"])
            row["correct"] = row["correct"] == "True"
            row["blocked"] = row["blocked"] == "True"
            row["avg_response_time_ms"] = float(row["avg_response_time_ms"])
            rows.append(row)
    return rows


def compute_metrics(rows):
    actual_phishing = [r for r in rows if r["true_label"] == "phishing"]
    actual_legitimate = [r for r in rows if r["true_label"] == "legitimate"]
    correctly_flagged_phishing = [r for r in actual_phishing if r["verdict"] == "PHISHING"]
    legitimate_wrongly_flagged = [r for r in actual_legitimate if r["verdict"] == "PHISHING"]
    attacks_blocked = [r for r in actual_phishing if r["blocked"]]

    detection_rate = len(correctly_flagged_phishing) / len(actual_phishing) if actual_phishing else 0.0
    false_positive_rate = len(legitimate_wrongly_flagged) / len(actual_legitimate) if actual_legitimate else 0.0
    response_time_ms = sum(r["avg_response_time_ms"] for r in rows) / len(rows) if rows else 0.0
    mitigation_success_rate = len(attacks_blocked) / len(actual_phishing) if actual_phishing else 0.0

    return {
        "detection_rate": detection_rate, "false_positive_rate": false_positive_rate,
        "response_time_ms": response_time_ms, "mitigation_success_rate": mitigation_success_rate,
        "total_actual_phishing": len(actual_phishing), "total_actual_legitimate": len(actual_legitimate),
        "correctly_flagged_phishing": len(correctly_flagged_phishing),
        "legitimate_wrongly_flagged": len(legitimate_wrongly_flagged), "attacks_blocked": len(attacks_blocked),
    }


def compute_per_stage(rows):
    return {stage: compute_metrics([r for r in rows if r["stage"] == stage]) for stage in ["email", "url", "landing_page"]}


def print_table(overall, per_stage):
    print("\n=== Chapter 5 metrics (overall, all stages combined) ===")
    print(f"{'Metric':<28}{'Value':>10}")
    print("-" * 38)
    print(f"{'Detection Rate':<28}{overall['detection_rate']*100:>9.1f}%")
    print(f"{'False Positive Rate':<28}{overall['false_positive_rate']*100:>9.1f}%")
    print(f"{'Response Time (ms)':<28}{overall['response_time_ms']:>10.3f}")
    print(f"{'Mitigation Success Rate':<28}{overall['mitigation_success_rate']*100:>9.1f}%")
    print(f"\n(Detection Rate = {overall['correctly_flagged_phishing']}/{overall['total_actual_phishing']} actual phishing correctly flagged)")
    print(f"(False Positive Rate = {overall['legitimate_wrongly_flagged']}/{overall['total_actual_legitimate']} legitimate items wrongly flagged)")
    print(f"(Mitigation Success Rate = {overall['attacks_blocked']}/{overall['total_actual_phishing']} attacks blocked)")
    print("\n=== Per-stage breakdown ===")
    print(f"{'Stage':<14}{'Detection':>11}{'FPR':>8}{'Resp(ms)':>11}{'Mitigation':>12}")
    for stage, m in per_stage.items():
        print(f"{stage:<14}{m['detection_rate']*100:>10.1f}%{m['false_positive_rate']*100:>7.1f}%{m['response_time_ms']:>11.3f}{m['mitigation_success_rate']*100:>11.1f}%")


def make_charts(overall, per_stage):
    labels = ["Overall"] + list(per_stage.keys())
    detection = [overall["detection_rate"] * 100] + [per_stage[s]["detection_rate"] * 100 for s in per_stage]
    fpr = [overall["false_positive_rate"] * 100] + [per_stage[s]["false_positive_rate"] * 100 for s in per_stage]

    x = range(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([i - width / 2 for i in x], detection, width, label="Detection Rate (%)")
    ax.bar([i + width / 2 for i in x], fpr, width, label="False Positive Rate (%)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("%")
    ax.set_title("Detection Rate vs False Positive Rate")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "chart_detection_vs_fpr.png"), dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].bar(["Response Time"], [overall["response_time_ms"]], color="tab:orange")
    axes[0].set_ylabel("milliseconds")
    axes[0].set_title("Average Response Time")
    axes[1].bar(["Mitigation Success Rate"], [overall["mitigation_success_rate"] * 100], color="tab:green")
    axes[1].set_ylabel("%")
    axes[1].set_ylim(0, 100)
    axes[1].set_title("Mitigation Success Rate")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "chart_response_and_mitigation.png"), dpi=150)
    plt.close(fig)

    print(f"\nCharts saved to:")
    print(f"  {os.path.join(HERE, 'chart_detection_vs_fpr.png')}")
    print(f"  {os.path.join(HERE, 'chart_response_and_mitigation.png')}")


def main():
    rows = load_results()
    overall = compute_metrics(rows)
    per_stage = compute_per_stage(rows)
    print_table(overall, per_stage)
    make_charts(overall, per_stage)


if __name__ == "__main__":
    main()
