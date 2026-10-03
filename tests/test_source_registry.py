import json
import unittest
from pathlib import Path

from scripts.validate_source_registry import validate_registry


class SourceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(Path("data/source_registry.json").read_text())

    def test_project_registry_is_valid(self):
        self.assertEqual(validate_registry(self.registry), [])

    def test_duplicate_ids_fail(self):
        self.registry["sources"].append(dict(self.registry["sources"][0]))
        self.assertIn("duplicate id", "\n".join(validate_registry(self.registry)))

    def test_unknown_license_cannot_be_verified(self):
        self.registry["sources"][0]["license_id"] = "UNKNOWN"
        self.assertIn("disagree", "\n".join(validate_registry(self.registry)))

    def test_approved_source_requires_immutable_ref(self):
        self.registry["sources"][0]["immutable_ref"] = False
        self.assertIn("immutable ref", "\n".join(validate_registry(self.registry)))

    def test_evaluation_only_cannot_train(self):
        candidate = self.registry["sources"][1]
        candidate["training_allowed"] = True
        self.assertIn("cannot allow training", "\n".join(validate_registry(self.registry)))


if __name__ == "__main__":
    unittest.main()
