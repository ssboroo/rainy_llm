import json
import unittest

from scripts.audit_evaluation_overlap import audit_overlap, shingles


def case(case_id="eval-1", prompt="Монгол Улсын нийслэл юу вэ?"):
    return {"id": case_id, "prompt": prompt}


def training(text, input_text="", file_index=1, row_number=1):
    return (file_index, row_number, {"instruction": text, "input": input_text})


class EvaluationOverlapTests(unittest.TestCase):
    def test_near_duplicate_is_reported_without_text(self):
        report = audit_overlap(
            [case()], [training("Монгол Улсын нийслэл хот юу вэ?")], threshold=0.7)

        self.assertEqual(report["candidate_count"], 1)
        self.assertEqual(report["findings"][0]["case_id"], "eval-1")
        self.assertGreaterEqual(report["findings"][0]["similarity"], 0.7)
        serialized = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("нийслэл хот", serialized)

    def test_distinct_prompt_is_not_reported(self):
        report = audit_overlap(
            [case()], [training("9-ийг 7-оор үржүүл.")], threshold=0.7)

        self.assertEqual(report["candidate_count"], 0)
        self.assertEqual(report["pairs_checked"], 1)

    def test_exact_match_has_similarity_one_and_location(self):
        report = audit_overlap(
            [case()], [training("Монгол Улсын нийслэл юу вэ?", file_index=2,
                                row_number=9)], threshold=1.0)

        self.assertEqual(report["findings"], [{
            "case_id": "eval-1", "training_file_index": 2,
            "training_row": 9, "similarity": 1.0,
        }])

    def test_pair_limit_and_invalid_options_are_rejected(self):
        rows = [training("Текст", row_number=1), training("Өөр", row_number=2)]
        with self.assertRaisesRegex(ValueError, "exceeds max_pairs"):
            audit_overlap([case(), case("eval-2", "Өөр асуулт")], rows, max_pairs=3)
        for kwargs in ({"threshold": float("nan")}, {"threshold": 0},
                       {"ngram": 0}, {"max_pairs": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                audit_overlap([case()], [training("Текст")], **kwargs)

    def test_short_strings_and_bad_training_schema(self):
        self.assertEqual(shingles("А", 3), {"а"})
        with self.assertRaisesRegex(ValueError, "input must be a string"):
            audit_overlap([case()], [(1, 1, {"instruction": "Текст", "input": 3})])


if __name__ == "__main__":
    unittest.main()
