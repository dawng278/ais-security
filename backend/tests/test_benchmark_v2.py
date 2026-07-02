import unittest
from app.benchmark.transforms.injectors import generate_ielts_injected_samples
from app.benchmark.runner_v2 import run_benchmark_v2


class TestBenchmarkV2(unittest.TestCase):
    def test_runner_v2(self):
        base_essays = [
            {
                "text": "Education improves career opportunities.",
                "band": 6.0
            }
        ]
        samples = generate_ielts_injected_samples(base_essays)
        self.assertEqual(len(samples), 6)  # clean, vi, en, role, obf, benign

        report = run_benchmark_v2(samples)
        self.assertGreaterEqual(report.accuracy, 0.8)
        self.assertIn("direct_vietnamese", report.by_attack_type)
        self.assertIn("en", report.by_language)


if __name__ == "__main__":
    unittest.main()
