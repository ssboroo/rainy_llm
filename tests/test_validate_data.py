import json
import tempfile
import unittest
from pathlib import Path
from scripts.validate_data import validate


class ValidationTests(unittest.TestCase):
    def check_rows(self, rows):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "data.jsonl"
            path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
            return validate(path)

    def sample(self, **updates):
        return dict(dict(id="mn-1", instruction="Мэндчил.", output="Сайн байна уу!",
                         source="human-authored-example", license="CC0-1.0", split="train"), **updates)

    def test_valid_mongolian(self):
        self.assertEqual(self.check_rows([self.sample()]), (1, []))

    def test_duplicate_across_splits(self):
        _, errors = self.check_rows([self.sample(), self.sample(id="mn-2", split="test")])
        self.assertTrue(any("duplicate content" in error for error in errors))

    def test_missing_provenance(self):
        self.assertTrue(self.check_rows([self.sample(source="")])[1])

    def test_bad_types_and_split(self):
        for row in [[], self.sample(input=4), self.sample(split="other")]:
            with self.subTest(row=row):
                self.assertTrue(self.check_rows([row])[1])

    def test_empty(self):
        self.assertTrue(self.check_rows([])[1])

    def test_malformed_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.jsonl"
            path.write_text("{", encoding="utf-8")
            self.assertTrue(validate(path)[1])


if __name__ == "__main__":
    unittest.main()
