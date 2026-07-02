import os
import json
import pandas as pd
from pathlib import Path
from datasets import load_dataset


ROOT_DIR = Path(__file__).parent
RAW_DIR = ROOT_DIR / "raw"
PROCESSED_DIR = ROOT_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def download_hf_dataset(dataset_name: str, save_folder_name: str):
    print(f"--> Downloading HuggingFace dataset: {dataset_name}...")
    try:
        ds = load_dataset(dataset_name)
        target_dir = RAW_DIR / save_folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for split in ds.keys():
            df = ds[split].to_pandas()
            df.to_csv(target_dir / f"{split}.csv", index=False)
            print(f"    Saved {split}.csv ({len(df)} rows)")
        print(f"✓ Downloaded {dataset_name} successfully.")
    except Exception as e:
        print(f"✕ Failed to download {dataset_name}: {e}")


def main():
    print("=== GradingGuard AI Dataset Pull Pipeline ===")
    
    # 1. HuggingFace datasets
    download_hf_dataset("zachz/prompt-injection-benchmark", "zachz_prompt_injection_benchmark")
    download_hf_dataset("deepset/prompt-injections", "deepset_prompt_injections")
    download_hf_dataset("chillies/IELTS-writing-task-2-evaluation", "chillies_ielts_task2")
    
    print("\nDataset pull pipeline completed!")


if __name__ == "__main__":
    main()
