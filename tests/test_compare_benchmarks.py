import json
import tempfile
import unittest
from pathlib import Path

from scripts.compare_benchmarks import compare_runs, load_run, validate_run


REV = "a" * 40
SHA = "b" * 64


def run(accuracy=0.25, seconds=24.0, model="org/model"):
    metadata = {
        "model": model, "revision": REV, "device": "cpu", "dtype": "float32",
        "seed": 42, "do_sample": False, "max_new_tokens": 64, "thinking": False,
        "cases_sha256": SHA, "status": "completed", "total_generation_seconds": seconds,
        "hardware": "test-cpu", "peak_vram_gb": 0.0, "estimated_cost_usd": 0.0,
    }
    scores = {
        "metric": "normalized_exact_match", "correct": int(accuracy * 4),
        "total": 4, "accuracy": accuracy, "missing": 0,
    }
    return metadata, scores


class CompareBenchmarkTests(unittest.TestCase):
    def test_higher_comparable_score_is_promotion_eligible(self):
        report = compare_runs(run(0.25), run(0.5, 20, "org/new"))
        self.assertTrue(report["comparable"])
        self.assertEqual(report["accuracy_delta"], 0.25)
        self.assertTrue(report["promotion_eligible"])

    def test_changed_eval_hash_blocks_comparison(self):
        baseline, candidate = run(), run(0.5)
        candidate[0]["cases_sha256"] = "c" * 64
        report = compare_runs(baseline, candidate)
        self.assertFalse(report["comparable"])
        self.assertIn("cases_sha256", report["comparability_mismatches"])

    def test_changed_decoding_blocks_comparison(self):
        baseline, candidate = run(), run(0.5)
        candidate[0]["max_new_tokens"] = 128
        self.assertIn("max_new_tokens", compare_runs(baseline, candidate)["comparability_mismatches"])

    def test_changed_runtime_blocks_comparison(self):
        for key, value in (("dtype", "bfloat16"), ("device", "cuda"),
                           ("threads", 8), ("torch", "different"),
                           ("transformers", "different")):
            with self.subTest(key=key):
                baseline, candidate = run(), run(0.5)
                candidate[0][key] = value
                self.assertFalse(compare_runs(baseline, candidate)["comparable"])
                self.assertIn(key, compare_runs(baseline, candidate)["comparability_mismatches"])

    def test_missing_resources_blocks_promotion_not_comparison(self):
        baseline, candidate = run(), run(0.5)
        del candidate[0]["peak_vram_gb"]
        report = compare_runs(baseline, candidate)
        self.assertTrue(report["comparable"])
        self.assertFalse(report["promotion_eligible"])

    def test_null_resource_measurement_blocks_promotion(self):
        baseline, candidate = run(), run(0.5)
        candidate[0]["estimated_cost_usd"] = None
        report = compare_runs(baseline, candidate)
        self.assertIn("candidate.estimated_cost_usd", report["missing_resource_measurements"])
        self.assertFalse(report["promotion_eligible"])

    def test_mutable_revision_is_invalid(self):
        metadata, scores = run()
        metadata["revision"] = "main"
        self.assertTrue(any("immutable" in error for error in validate_run(metadata, scores)))

    def test_adapter_requires_pinned_base(self):
        metadata, scores = run()
        metadata["adapter"] = {"base_model": "org/model", "base_revision": "main"}
        self.assertIn("adapter base_revision must be immutable", validate_run(metadata, scores))

    def test_load_run_reads_expected_files(self):
        metadata, scores = run()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "metadata.json").write_text(json.dumps(metadata))
            (path / "scores.json").write_text(json.dumps(scores))
            self.assertEqual(load_run(path), (metadata, scores))


if __name__ == "__main__":
    unittest.main()
