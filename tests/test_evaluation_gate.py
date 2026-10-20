import unittest

from scripts.validate_evaluation import REVIEW_CHECKS, case_fingerprint, read_jsonl, validate_cases


def case(i="1", prompt="Асуулт", status="draft-needs-human-review"):
    row = {
        "id": i, "category": "test", "prompt": prompt, "answers": ["Хариу"],
        "review_status": status, "source": "project-authored-evaluation-draft",
    }
    if status == "human-reviewed":
        row["review_evidence"] = {
            "case_sha256": case_fingerprint(row), "reviewed_at": "2026-10-08",
            "reviewer_role": "independent-human-reviewer", "decision": "accept",
            "checks": {key: True for key in REVIEW_CHECKS},
        }
    return row


class EvaluationGateTests(unittest.TestCase):
    def test_repository_draft_is_valid_but_not_release_ready(self):
        rows = read_jsonl("evaluation/mn_smoke.jsonl")
        errors, report = validate_cases(rows)
        self.assertEqual(errors, [])
        self.assertEqual(report["cases"], 24)
        self.assertEqual(report["review_statuses"], {"draft-needs-human-review": 24})
        errors, report = validate_cases(rows, release=True)
        self.assertIn("release contains draft cases", errors)
        self.assertFalse(report["release_ready"])

    def test_release_accepts_reviewed_minimum(self):
        rows = [case(str(i), f"Асуулт {i}", "human-reviewed") for i in range(3)]
        errors, report = validate_cases(rows, release=True, min_cases=3)
        self.assertEqual(errors, [])
        self.assertTrue(report["release_ready"])

    def test_training_overlap_is_rejected_after_normalization(self):
        rows = [case(prompt="  Монгол   МЭНДЧИЛГЭЭ ")]
        training = [{"instruction": "монгол мэндчилгээ"}]
        errors, _ = validate_cases(rows, training)
        self.assertIn("training overlap: 1", errors)

    def test_duplicate_normalized_prompt_is_rejected(self):
        errors, _ = validate_cases([case("1", "Сайн уу"), case("2", " сайн  УУ ")])
        self.assertIn("duplicate normalized prompt: 2", errors)

    def test_bad_answer_and_status_are_rejected(self):
        row = case(status="approved-by-ai")
        row["answers"] = []
        errors, _ = validate_cases([row])
        self.assertTrue(any("answers" in error for error in errors))
        self.assertTrue(any("review_status" in error for error in errors))

    def test_human_review_requires_matching_evidence(self):
        row = case(status="human-reviewed")
        row["prompt"] = "Хяналтын дараа нууцаар өөрчилсөн"

        errors, _ = validate_cases([row])

        self.assertTrue(any("case_sha256" in error for error in errors))

    def test_empty_set_is_rejected(self):
        errors, _ = validate_cases([])
        self.assertEqual(errors, ["evaluation set is empty"])

    def test_invalid_minimum_is_rejected(self):
        errors, _ = validate_cases([case()], release=True, min_cases=0)
        self.assertIn("min_cases must be a positive integer", errors)


if __name__ == "__main__":
    unittest.main()
