import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_offline_bundle import create_bundle, verify_bundle


REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
MODEL_ID = "Qwen/Qwen3-0.6B"
RUNTIME = ["torch==2.6.0+cpu", "transformers==4.51.3", "peft==0.15.2", "accelerate==1.6.0"]
MODEL_CARD = f"https://huggingface.co/{MODEL_ID}/tree/{REVISION}"
LICENSE_URL = f"https://huggingface.co/{MODEL_ID}/blob/{REVISION}/LICENSE"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))


def make_merged(root, *, template=True):
    write(root / "config.json", '{"model_type":"fixture"}')
    write(root / "model.safetensors", b"not-real-tensor-fixture")
    write(root / "tokenizer.json", '{"version":"fixture"}')
    config = {"tokenizer_class": "FixtureTokenizer"}
    if template:
        config["chat_template"] = "{{ messages }}"
    write(root / "tokenizer_config.json", json.dumps(config))
    return root


def make_base_plus_adapter(root):
    base = root / "base"
    adapter = root / "adapter"
    make_merged(base)
    write(adapter / "adapter_config.json", json.dumps({
        "base_model_name_or_path": MODEL_ID, "peft_type": "LORA"
    }))
    write(adapter / "adapter_model.safetensors", b"not-real-adapter-fixture")
    return root


def create(source, destination, *, mode="merged", **overrides):
    values = dict(
        mode=mode, model_id=MODEL_ID, revision=REVISION,
        weights_license="Apache-2.0", code_license="Apache-2.0",
        model_card_url=MODEL_CARD, license_url=LICENSE_URL,
        runtime=RUNTIME, max_bytes=1024 * 1024,
    )
    values.update(overrides)
    return create_bundle(source, destination, **values)


class OfflineBundleTests(unittest.TestCase):
    def test_merged_bundle_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source")
            bundle = root / "bundle"
            manifest = create(source, bundle)
            result = verify_bundle(bundle)
            self.assertEqual(result["bundle_id"], manifest["bundle_id"])
            self.assertTrue(result["verified"])
            self.assertEqual(result["artifact_mode"], "merged")
            self.assertEqual(result["network_access"], "none")
            self.assertFalse(result["inference_performed"])
            self.assertEqual(result["files"], 4)

    def test_base_plus_adapter_bundle_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_base_plus_adapter(root / "source")
            bundle = root / "bundle"
            create(source, bundle, mode="base-plus-adapter")
            result = verify_bundle(bundle)
            self.assertEqual(result["artifact_mode"], "base-plus-adapter")
            self.assertEqual(result["files"], 6)

    def test_tampered_weight_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create(make_merged(root / "source"), root / "bundle")
            (root / "bundle" / "model" / "model.safetensors").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "hash/size mismatch"):
                verify_bundle(root / "bundle")

    def test_manifest_identity_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create(make_merged(root / "source"), root / "bundle")
            path = root / "bundle" / "bundle-manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["model_id"] = "attacker/model"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identity hash mismatch"):
                verify_bundle(root / "bundle")

    def test_missing_chat_template_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source", template=False)
            with self.assertRaisesRegex(ValueError, "chat template"):
                create(source, root / "bundle")
            self.assertFalse((root / "bundle").exists())

    def test_mutable_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source")
            with self.assertRaisesRegex(ValueError, "immutable 40-character"):
                create(source, root / "bundle", revision="main")

    def test_runtime_range_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source")
            with self.assertRaisesRegex(ValueError, "exact"):
                create(source, root / "bundle", runtime=["torch>=2.6"])

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source")
            destination = root / "bundle"
            destination.mkdir()
            sentinel = destination / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create(source, destination)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_source_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = make_merged(root / "actual")
            link = root / "link"
            link.symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                create(link, root / "bundle")

    def test_nested_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source")
            (source / "linked.safetensors").symlink_to(source / "model.safetensors")
            with self.assertRaisesRegex(ValueError, "symlinks"):
                create(source, root / "bundle")

    def test_source_inside_git_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            source = make_merged(root / "source")
            with self.assertRaisesRegex(ValueError, "outside every Git checkout"):
                create(source, root / "bundle")

    def test_size_cap_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = make_merged(root / "source")
            with self.assertRaisesRegex(ValueError, "exceeds the configured byte cap"):
                create(source, root / "bundle", max_bytes=1)

    def test_incomplete_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            (bundle / "BUNDLE_INCOMPLETE").write_text("interrupted", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "incomplete-publication"):
                verify_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
