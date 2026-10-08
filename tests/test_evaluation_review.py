import tempfile
import unittest
from pathlib import Path

from scripts.review_evaluation import apply_reviews, export_packet, write_jsonl
from scripts.validate_evaluation import REVIEW_CHECKS, case_fingerprint, validate_cases


def cases():
    return [{
        "id": "mn-001", "category": "comprehension", "prompt": "Асуулт",
        "answers": ["Хариу"], "review_status": "draft-needs-human-review",
        "source": "project-authored-evaluation-draft",
    }]


class EvaluationReviewTests(unittest.TestCase):
    def test_export_is_pending_and_bound_to_content(self):
        packet = export_packet(cases())

        self.assertEqual(packet[0]["case_sha256"], case_fingerprint(cases()[0]))
        self.assertEqual(packet[0]["decision"], "pending")
        self.assertTrue(all(value is False for value in packet[0]["checks"].values()))

    def test_completed_review_applies_valid_evidence(self):
        packet = export_packet(cases())
        packet[0]["checks"] = {key: True for key in REVIEW_CHECKS}
        packet[0]["decision"] = "accept"

        output = apply_reviews(cases(), packet, "2026-10-08", "independent-human-reviewer")

        self.assertEqual(output[0]["review_status"], "human-reviewed")
        self.assertEqual(validate_cases(output)[0], [])

    def test_rejects_stale_case_fingerprint(self):
        packet = export_packet(cases())
        packet[0]["checks"] = {key: True for key in REVIEW_CHECKS}
        packet[0]["decision"] = "accept"
        changed = cases()
        changed[0]["prompt"] = "Өөр асуулт"

        with self.assertRaisesRegex(ValueError, "stale or mismatched"):
            apply_reviews(changed, packet, "2026-10-08", "human-reviewer")

    def test_rejects_incomplete_or_missing_reviews(self):
        packet = export_packet(cases())
        with self.assertRaisesRegex(ValueError, "incomplete checks"):
            apply_reviews(cases(), packet, "2026-10-08", "human-reviewer")
        with self.assertRaisesRegex(ValueError, "exactly match"):
            apply_reviews(cases(), [], "2026-10-08", "human-reviewer")

    def test_writer_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.jsonl"
            write_jsonl(path, [{"id": "one"}])
            with self.assertRaises(FileExistsError):
                write_jsonl(path, [{"id": "two"}])


if __name__ == "__main__":
    unittest.main()
