import json
from pathlib import Path
from collections import Counter

def analyze_under_blocks():
    root = Path(__file__).resolve().parent.parent.parent.parent
    failure_path = root / "datasets" / "reports" / "v3" / "failure_analysis.jsonl"
    case_res_path = root / "datasets" / "reports" / "v3" / "case_results.jsonl"

    if not failure_path.exists():
        print(f"File not found: {failure_path}")
        return

    failures = []
    with failure_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                failures.append(json.loads(line))

    total_failures = len(failures)
    print(f"=== UNDER-BLOCK FAILURE ANALYSIS SUMMARY ===")
    print(f"Total Failure Cases Analyzed: {total_failures}\n")

    attack_types = Counter(f.get("attack_type", "unknown") for f in failures)
    print("--- Attack Type Breakdown ---")
    for at, cnt in attack_types.most_common():
        print(f"  - {at}: {cnt} ({cnt/total_failures*100:.1f}%)")

    actions = Counter(f.get("predicted_action", f.get("action", "unknown")) for f in failures)
    print("\n--- Predicted Action Breakdown ---")
    for act, cnt in actions.most_common():
        print(f"  - {act}: {cnt} ({cnt/total_failures*100:.1f}%)")

    risk_scores = [f.get("risk_score", 0.0) for f in failures]
    r_buckets = {
        "0.0 - 0.25 (Low)": sum(1 for r in risk_scores if r < 0.25),
        "0.25 - 0.45 (Medium)": sum(1 for r in risk_scores if 0.25 <= r < 0.45),
        "0.45 - 0.65 (High-Low)": sum(1 for r in risk_scores if 0.45 <= r < 0.65),
        "0.65 - 0.85 (High-Upper)": sum(1 for r in risk_scores if 0.65 <= r < 0.85),
    }
    print("\n--- Risk Score Buckets ---")
    for b, cnt in r_buckets.items():
        print(f"  - {b}: {cnt} ({cnt/total_failures*100:.1f}%)")

    print("\n--- Top 10 Sample Previews ---")
    for i, f in enumerate(failures[:10], 1):
        prev = f.get("text_preview", "")[:80].replace("\n", " ")
        print(f"  {i:2d}. [{f.get('attack_type', 'unknown')}] {prev}...")

if __name__ == "__main__":
    analyze_under_blocks()
