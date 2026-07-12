import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_public_claims import REQUIRED_FRONTEND_ROUTES, build_report


class PublicClaimAuditTests(unittest.TestCase):
    def write_metric_artifact(self, root: Path) -> None:
        report_dir = root / "datasets" / "reports" / "v3"
        report_dir.mkdir(parents=True)
        payload = {
            "benchmark_report": {
                "benchmark_id": "gg_benchmark_v3",
                "total_cases": 662,
                "accuracy": 0.79,
                "precision": 1.0,
                "recall": 0.47,
                "macro_f1": 0.64,
                "false_positive_rate": 0.0,
                "under_block_rate": 0.21,
                "failure_analysis_count": 139,
            },
            "evidence_report": {
                "run_context": {"run_id": "test_run", "git_commit": "abc123"},
                "dataset": {"total_cases": 965, "dataset_sha256": "dataset_hash"},
                "detector": {
                    "config_sha256": "config_hash",
                    "enable_embedding_detector": False,
                    "embedding_runtime_state": "unavailable",
                },
            },
        }
        (report_dir / "benchmark_v3_combined.json").write_text(json.dumps(payload), encoding="utf-8")

    def write_frontend_routes(self, root: Path) -> None:
        app_dir = root / "frontend" / "src" / "app"
        for route in REQUIRED_FRONTEND_ROUTES:
            route_dir = app_dir if route == "/" else app_dir / route.lstrip("/")
            route_dir.mkdir(parents=True, exist_ok=True)
            (route_dir / "page.tsx").write_text("export default function Page() { return null; }\n", encoding="utf-8")

    def test_detects_stale_macro_f1_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_metric_artifact(root)
            self.write_frontend_routes(root)
            claim_file = root / "README.md"
            claim_file.write_text("Current Macro F1: 0.90\n", encoding="utf-8")

            report = build_report(root, ["README.md"])

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["findings"][0]["claim_type"], "stale_macro_f1")

    def test_allows_historical_stale_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_metric_artifact(root)
            self.write_frontend_routes(root)
            claim_file = root / "README.md"
            claim_file.write_text("Historical Macro F1: 0.90, not current.\n", encoding="utf-8")

            report = build_report(root, ["README.md"])

            self.assertEqual(report["status"], "PASS")

    def test_detects_unsupported_docker_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_metric_artifact(root)
            self.write_frontend_routes(root)
            claim_file = root / "README.md"
            claim_file.write_text("docker-compose.yml verified for docker compose up --build\n", encoding="utf-8")

            report = build_report(root, ["README.md"])

            self.assertTrue(any(f["claim_type"] == "unsupported_docker" for f in report["findings"]))


if __name__ == "__main__":
    unittest.main()
