import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path("scripts/checkpoint_resume_equivalence.py")


class CheckpointResumeEquivalenceTests(unittest.TestCase):
    def test_cli_help_does_not_require_optional_model_runtime(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--output", result.stdout)

    @unittest.skipUnless(
        importlib.util.find_spec("torch") and importlib.util.find_spec("safetensors"),
        "optional CPU Torch and safetensors backend",
    )
    def test_fresh_process_resume_matches_uninterrupted_state_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "equivalence"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(output)],
                capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stderr[-3000:])
            report = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(report["total_steps"], 4)
            self.assertEqual(report["resume_boundary"], 2)
            self.assertTrue(report["comparisons"]["all_exact"], report)
            self.assertEqual(
                set(report["comparisons"]) - {"all_exact"},
                {
                    "model_tensors_exact", "optimizer_exact", "scheduler_exact",
                    "rng_exact", "trainer_state_exact",
                },
            )
            self.assertFalse(report["model_quality_evaluated"])
            self.assertFalse(report["mongolian_quality_gain"])

    def test_output_symlink_is_refused_before_runtime_work(self):
        from scripts import checkpoint_resume_equivalence as experiment
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            target.mkdir()
            link = root / "link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable on this platform")
            with self.assertRaisesRegex(ValueError, "symlinks"):
                experiment.run_experiment(link)


    def test_peak_rss_is_nullable_without_resource_module(self):
        from scripts import checkpoint_resume_equivalence as experiment
        previous = experiment.resource
        try:
            experiment.resource = None
            self.assertIsNone(experiment._peak_rss_platform_units())
        finally:
            experiment.resource = previous


if __name__ == "__main__":
    unittest.main()
