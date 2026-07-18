#!/usr/bin/env python3
import os
from pathlib import Path

# Paths to include (relative to repository root)
INCLUDE_PATHS = [
    "README.md",
    "docker-compose.yml",
    "scripts/final_check.sh",
    "docs",
    "datasets/reports/v3",
    "datasets/registry",
    "datasets/scenarios/gradingguard_case_library.jsonl",
    "backend/app/firewall",
    "backend/app/benchmark",
    "backend/app/grader",
    "backend/app/student_auth",
    "backend/app/api/student_auth_v1.py",
    "backend/app/operational",
    "backend/app/config.py",
    "backend/scripts/seed_demo_students.py",
    "backend/tests",
    "frontend/src"
]

# Excluded directory names or files
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", "venv", ".git"}
EXCLUDE_FILES = {".DS_Store"}

# Supported text extensions
TEXT_EXTENSIONS = {
    ".py", ".md", ".json", ".jsonl", ".yaml", ".yml", 
    ".sh", ".example", ".txt", ".ts", ".tsx", ".css", ".conf"
}

def get_language(extension: str) -> str:
    mapping = {
        ".py": "python",
        ".md": "markdown",
        ".json": "json",
        ".jsonl": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sh": "bash",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".css": "css",
        ".example": "text",
        ".txt": "text"
    }
    return mapping.get(extension, "text")

def should_process(path: Path) -> bool:
    if path.name in EXCLUDE_FILES:
        return False
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if path.suffix not in TEXT_EXTENSIONS:
        return False
    return True

def main():
    root = Path(__file__).resolve().parents[1]
    output_file = root / "CONSOLIDATED_RESEARCH_DATA.md"
    
    print(f"Repository Root: {root}")
    print(f"Output File: {output_file}")
    
    markdown_content = []
    markdown_content.append("# GradingGuard AI — Consolidated Research and Implementation Data\n")
    markdown_content.append("This document consolidates key files, reports, documentation, backend modules, and verification tests from the GradingGuard AI project workspace.\n")
    
    processed_count = 0
    
    for rel_path_str in INCLUDE_PATHS:
        target = root / rel_path_str
        if not target.exists():
            print(f"Warning: Target path does not exist: {rel_path_str}")
            continue
            
        # Collect files
        files_to_process = []
        if target.is_file():
            files_to_process.append(target)
        else:
            for p in target.rglob("*"):
                if p.is_file() and should_process(p):
                    files_to_process.append(p)
                    
        # Sort files to ensure stable output order
        files_to_process.sort()
        
        for file_path in files_to_process:
            relative_to_root = file_path.relative_to(root)
            lang = get_language(file_path.suffix)
            
            print(f"Processing: {relative_to_root}")
            
            markdown_content.append(f"## File: `{relative_to_root}`\n")
            
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                
                # Check for nested code block delimiters in content to prevent markdown syntax breakage
                # If they exist, we use a different block or escape them
                escaped_content = content
                if "```" in content:
                    # We can use four backticks or more if the file contains three backticks
                    markdown_content.append("````" + lang + "\n")
                    markdown_content.append(escaped_content)
                    if not escaped_content.endswith("\n"):
                        markdown_content.append("\n")
                    markdown_content.append("````\n\n")
                else:
                    markdown_content.append("```" + lang + "\n")
                    markdown_content.append(escaped_content)
                    if not escaped_content.endswith("\n"):
                        markdown_content.append("\n")
                    markdown_content.append("```\n\n")
                    
                processed_count += 1
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                markdown_content.append(f"*Error reading file: {e}*\n\n")
                
    output_file.write_text("".join(markdown_content), encoding="utf-8")
    print(f"Success! Processed {processed_count} files and wrote output to: {output_file}")

if __name__ == "__main__":
    main()
