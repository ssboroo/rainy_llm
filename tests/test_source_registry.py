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
        self.assertIn("concrete license_id", "\n".join(validate_registry(self.registry)))

    def test_conflicting_license_cannot_be_verified(self):
        source = self.registry["sources"][-1]
        source["license_status"] = "conflict"
        source["license_verified"] = True
        self.assertIn("license_status and license_verified disagree",
                      "\n".join(validate_registry(self.registry)))

    def test_unresolved_license_cannot_be_training_candidate(self):
        source = self.registry["sources"][-1]
        source["decision"] = "pilot-approved"
        source["training_allowed"] = True
        self.assertIn("unresolved license must be held and training-blocked",
                      "\n".join(validate_registry(self.registry)))

    def test_bad_license_status_type_is_reported(self):
        self.registry["sources"][-1]["license_status"] = []
        self.assertIn("license_status is invalid",
                      "\n".join(validate_registry(self.registry)))

    def test_approved_source_requires_immutable_ref(self):
        self.registry["sources"][0]["immutable_ref"] = False
        self.assertIn("immutable ref", "\n".join(validate_registry(self.registry)))

    def test_evaluation_only_cannot_train(self):
        candidate = self.registry["sources"][1]
        candidate["training_allowed"] = True
        self.assertIn("cannot allow training", "\n".join(validate_registry(self.registry)))


if __name__ == "__main__":
    unittest.main()
