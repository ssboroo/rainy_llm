import tempfile
import unittest
from pathlib import Path

from scripts.review_evaluation import (
    apply_reviews, export_packet, summarize_reviews, write_jsonl,
)
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

    def test_summary_counts_progress_without_prompt_text(self):
        rows = cases() + [{
            "id": "mn-002", "category": "logic", "prompt": "Нууц prompt",
            "answers": ["тийм"], "review_status": "draft-needs-human-review",
            "source": "project-authored-evaluation-draft",
        }]
        packet = export_packet(rows)
        packet[0]["checks"] = {key: True for key in REVIEW_CHECKS}
        packet[0]["decision"] = "accept"

        report = summarize_reviews(rows, packet)

        self.assertEqual(report["statuses"], {"pending": 1, "ready-accept": 1})
        self.assertEqual(report["categories"]["logic"]["pending"], 1)
        self.assertFalse(report["ready_to_apply"])
        self.assertNotIn("Нууц prompt", str(report))

    def test_summary_reports_stale_missing_unknown_and_rejected(self):
        rows = cases() + [{
            "id": "mn-002", "category": "logic", "prompt": "Хоёр",
            "answers": ["2"], "review_status": "draft-needs-human-review",
            "source": "project-authored-evaluation-draft",
        }, {
            "id": "mn-003", "category": "logic", "prompt": "Гурав",
            "answers": ["3"], "review_status": "draft-needs-human-review",
            "source": "project-authored-evaluation-draft",
        }]
        packet = export_packet(rows)
        packet[0]["case_sha256"] = "0" * 64
        packet[1]["decision"] = "reject"
        packet.pop()
        packet.append({"id": "unknown"})

        report = summarize_reviews(rows, packet)

        self.assertEqual(report["statuses"], {
            "missing": 1, "rejected": 1, "stale": 1,
        })
        self.assertEqual(report["unknown_review_ids"], ["unknown"])
        self.assertFalse(report["ready_to_apply"])

    def test_summary_all_complete_is_ready(self):
        packet = export_packet(cases())
        packet[0]["checks"] = {key: True for key in REVIEW_CHECKS}
        packet[0]["decision"] = "accept"

        self.assertTrue(summarize_reviews(cases(), packet)["ready_to_apply"])


if __name__ == "__main__":
    unittest.main()
