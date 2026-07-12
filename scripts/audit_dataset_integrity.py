#!/usr/bin/env python3
"""Read-only Phase 2 dataset/evidence integrity gate."""

from __future__ import annotations

from phase2_dataset_tools import validate_integrity


def main() -> int:
    ok, errors = validate_integrity()
    if ok:
        print("Phase 2 dataset integrity audit: PASS")
        return 0
    print("Phase 2 dataset integrity audit: FAIL")
    for error in errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
