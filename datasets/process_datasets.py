import json
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent
RAW_DIR = ROOT_DIR / "raw"
PROCESSED_DIR = ROOT_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def process_zachz():
    path = RAW_DIR / "zachz_prompt_injection_benchmark" / "train.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    samples = []
    for idx, row in df.iterrows():
        label_str = str(row.get("label", "")).lower()
        is_inj = "injection" in label_str or label_str == "1"
        samples.append({
            "id": f"zachz_{idx+1:04d}",
            "source": "zachz/prompt-injection-benchmark",
            "task_type": "generic",
            "domain": "generic_llm_security",
            "language": "en",
            "text": str(row.get("prompt", "")),
            "label": "injection" if is_inj else "clean",
            "attack_type": str(row.get("category", "generic_injection")),
            "expected_action": "secure_grade" if is_inj else "allow",
            "expected_risk_level": "high" if is_inj else "low",
            "split": "public_test",
            "group_id": f"zachz_group_{idx+1:04d}"
        })
    return samples


def process_deepset():
    train_path = RAW_DIR / "deepset_prompt_injections" / "train.csv"
    test_path = RAW_DIR / "deepset_prompt_injections" / "test.csv"
    samples = []
    
    for split_name, path in [("train", train_path), ("test", test_path)]:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for idx, row in df.iterrows():
            is_inj = int(row.get("label", 0)) == 1
            samples.append({
                "id": f"deepset_{split_name}_{idx+1:04d}",
                "source": "deepset/prompt-injections",
                "task_type": "generic",
                "domain": "generic_llm_security",
                "language": "en",
                "text": str(row.get("text", "")),
                "label": "injection" if is_inj else "clean",
                "attack_type": "direct_english" if is_inj else "clean",
                "expected_action": "secure_grade" if is_inj else "allow",
                "expected_risk_level": "high" if is_inj else "low",
                "split": "public_test" if split_name == "test" else "train",
                "group_id": f"deepset_group_{split_name}_{idx+1:04d}"
            })
    return samples


def main():
    print("=== Processing & Building Canonical JSONL Benchmark ===")
    all_samples = []
    
    z_samples = process_zachz()
    print(f"Processed zachz: {len(z_samples)} rows")
    all_samples.extend(z_samples)
    
    d_samples = process_deepset()
    print(f"Processed deepset: {len(d_samples)} rows")
    all_samples.extend(d_samples)
    
    out_file = PROCESSED_DIR / "canonical_prompt_injection.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for item in all_samples:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"✓ Saved canonical dataset: {out_file} ({len(all_samples)} total samples)")


if __name__ == "__main__":
    main()
