import unittest

from scripts.model_provenance import build_model_provenance


class ModelProvenanceTests(unittest.TestCase):
    def valid(self, **overrides):
        values = dict(
            model_id="Qwen/Qwen3-0.6B",
            revision="c1899de289a04d12100db370d81485cdf75e47ca",
            weights_license="Apache-2.0",
            code_license="not separately specified",
            model_card_url="https://huggingface.co/Qwen/Qwen3-0.6B",
            license_url="https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/LICENSE",
            model_files={"config.json": "a" * 64, "tokenizer.json": "b" * 64,
                         "tokenizer_config.json": "c" * 64, "model.safetensors": "d" * 64},
            chat_template="{{ messages }}",
        )
        values.update(overrides)
        return build_model_provenance(**values)

    def test_records_exact_identity_and_hashes(self):
        result = self.valid()
        self.assertEqual(result["model_id"], "Qwen/Qwen3-0.6B")
        self.assertEqual(result["revision"], "c1899de289a04d12100db370d81485cdf75e47ca")
        self.assertEqual(len(result["tokenizer_sha256"]), 64)
        self.assertEqual(len(result["chat_template_sha256"]), 64)
        self.assertEqual(result["code_license"], "not separately specified")
        self.assertIn("not independently authenticated", result["provenance_status"])

    def test_named_templates_are_canonicalized(self):
        left = self.valid(chat_template={"default": "{{ messages }}", "tools": "{{ tools }}"})
        right = self.valid(chat_template={"tools": "{{ tools }}", "default": "{{ messages }}"})
        self.assertEqual(left["chat_template_sha256"], right["chat_template_sha256"])
        self.assertEqual(left["chat_template_format"], "named-templates-json")

    def test_rejects_mutable_or_short_revision(self):
        for revision in ("main", "c1899de", "z" * 40):
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, "revision"):
                self.valid(revision=revision)

    def test_rejects_invalid_model_id(self):
        with self.assertRaisesRegex(ValueError, "namespace/name"):
            self.valid(model_id="Qwen3-0.6B")

    def test_requires_separate_license_labels(self):
        with self.assertRaisesRegex(ValueError, "code license"):
            self.valid(code_license="  ")

    def test_requires_https_source_urls(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            self.valid(model_card_url="http://huggingface.co/Qwen/Qwen3-0.6B")

    def test_requires_tokenizer_files(self):
        with self.assertRaisesRegex(ValueError, "tokenizer files"):
            self.valid(model_files={"config.json": "a" * 64, "model.safetensors": "b" * 64})

    def test_requires_explicit_template(self):
        for template in (None, "  ", []):
            with self.subTest(template=template), self.assertRaisesRegex(ValueError, "chat template"):
                self.valid(chat_template=template)

    def test_rejects_bad_hash_and_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.valid(model_files={"tokenizer.json": "bad"})
        with self.assertRaisesRegex(ValueError, "escape"):
            self.valid(model_files={"../tokenizer.json": "a" * 64})


if __name__ == "__main__":
    unittest.main()
