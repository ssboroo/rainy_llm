import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate import score
from scripts.verify_experiment import verify_experiment


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class VerifyExperimentTests(unittest.TestCase):
    def make_run(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        cases = root / "cases.jsonl"
        case_rows = [{"id": "one", "category": "test", "prompt": "Асуулт", "answers": ["42"]}]
        cases.write_text(json.dumps(case_rows[0], ensure_ascii=False) + "\n", encoding="utf-8")
        run = root / "run"
        run.mkdir()
        predictions = [{"id": "one", "output": "42", "seconds": 1.25,
                        "generated_tokens": 2, "hit_token_limit": False}]
        (run / "predictions.jsonl").write_text(
            json.dumps(predictions[0], ensure_ascii=False) + "\n", encoding="utf-8")
        write_json(run / "scores.json", score(case_rows, predictions))
        write_json(run / "metadata.json", {
            "status": "completed",
            "cases_sha256": hashlib.sha256(cases.read_bytes()).hexdigest(),
            "total_generation_seconds": 1.25,
            "generated_tokens": 2,
            "token_limit_hits": 0,
        })
        return temporary, run, cases

    def test_valid_run_recomputes_all_aggregates(self):
        temporary, run, cases = self.make_run()
        self.addCleanup(temporary.cleanup)

        report = verify_experiment(run, cases)

        self.assertTrue(report["valid"])
        self.assertEqual(report["measurements"]["correct"], 1)
        self.assertEqual(report["errors"], [])

    def test_tampered_score_is_rejected(self):
        temporary, run, cases = self.make_run()
        self.addCleanup(temporary.cleanup)
        scores = json.loads((run / "scores.json").read_text())
        scores["correct"] = 0
        write_json(run / "scores.json", scores)

        report = verify_experiment(run, cases)

        self.assertFalse(report["valid"])
        self.assertTrue(any("recomputed" in error for error in report["errors"]))

    def test_case_hash_and_aggregate_mismatch_are_rejected(self):
        temporary, run, cases = self.make_run()
        self.addCleanup(temporary.cleanup)
        metadata = json.loads((run / "metadata.json").read_text())
        metadata["cases_sha256"] = "0" * 64
        metadata["generated_tokens"] = 99
        write_json(run / "metadata.json", metadata)

        report = verify_experiment(run, cases)

        self.assertFalse(report["valid"])
        self.assertTrue(any("cases_sha256" in error for error in report["errors"]))
        self.assertTrue(any("generated_tokens" in error for error in report["errors"]))

    def test_invalid_prediction_measurement_is_rejected(self):
        temporary, run, cases = self.make_run()
        self.addCleanup(temporary.cleanup)
        prediction = json.loads((run / "predictions.jsonl").read_text())
        prediction["seconds"] = True
        (run / "predictions.jsonl").write_text(json.dumps(prediction) + "\n")

        report = verify_experiment(run, cases)

        self.assertFalse(report["valid"])
        self.assertTrue(any("seconds" in error for error in report["errors"]))

    def test_legacy_missing_aggregates_are_warnings(self):
        temporary, run, cases = self.make_run()
        self.addCleanup(temporary.cleanup)
        metadata = json.loads((run / "metadata.json").read_text())
        del metadata["generated_tokens"]
        del metadata["token_limit_hits"]
        write_json(run / "metadata.json", metadata)

        report = verify_experiment(run, cases)

        self.assertTrue(report["valid"])
        self.assertEqual(len(report["warnings"]), 2)


if __name__ == "__main__":
    unittest.main()
