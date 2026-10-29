import hashlib
import json
import tempfile
import types
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

from scripts import ask_offline_bundle as runner

BUNDLE_ID = "a" * 64
REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
TEMPLATE = "{{ messages }}"
RUNTIME = [
    {"package": "torch", "version": "2.6.0+cpu"},
    {"package": "transformers", "version": "4.51.3"},
    {"package": "peft", "version": "0.15.2"},
    {"package": "accelerate", "version": "1.6.0"},
]


class FakeTensor:
    def __init__(self, shape):
        self.shape = shape

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2 and isinstance(key[1], slice):
            start = key[1].start or 0
            stop = key[1].stop or self.shape[-1]
            return FakeTensor((max(0, stop - start),))
        return self


class FakeTokenizer:
    chat_template = TEMPLATE
    pad_token_id = 0
    eos_token_id = 1

    def apply_chat_template(self, messages, **kwargs):
        return "rendered prompt"

    def __call__(self, prompt, **kwargs):
        return {"input_ids": FakeTensor((1, 2)), "attention_mask": FakeTensor((1, 2))}

    def decode(self, tokens, **kwargs):
        return "Монгол хариу"


class FakeModel:
    config = types.SimpleNamespace(max_position_embeddings=32)

    def __init__(self):
        self.generate_kwargs = None

    def eval(self):
        return self

    def generate(self, **kwargs):
        self.generate_kwargs = kwargs
        return FakeTensor((1, 5))


def fixture_bundle(root, mode="merged"):
    bundle = root / "bundle"
    model = bundle / "model"
    model.mkdir(parents=True)
    target = model
    if mode == "base-plus-adapter":
        target = model / "base"
        target.mkdir()
        adapter = model / "adapter"
        adapter.mkdir()
        (adapter / "adapter_config.json").write_text(
            json.dumps({"base_model_name_or_path": "Qwen/Qwen3-0.6B"}), encoding="utf-8"
        )
        (adapter / "adapter_model.safetensors").write_bytes(b"fixture")
    (target / "config.json").write_text("{}", encoding="utf-8")
    (target / "model.safetensors").write_bytes(b"fixture-weights")
    (target / "tokenizer.json").write_text("{}", encoding="utf-8")
    (target / "tokenizer_config.json").write_text(
        json.dumps({"chat_template": TEMPLATE}), encoding="utf-8"
    )
    digest = hashlib.sha256(
        json.dumps(TEMPLATE, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    template_source = ("base/" if mode == "base-plus-adapter" else "") + "tokenizer_config.json:chat_template"
    manifest = {
        "bundle_id": BUNDLE_ID, "model_id": "Qwen/Qwen3-0.6B", "base_revision": REVISION,
        "artifact_mode": mode, "runtime_pins": RUNTIME, "source_bytes": 100,
        "chat_template": {"source": template_source, "sha256": digest},
        "training_run_sha256": None,
    }
    (bundle / runner.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    report = {
        "verified": True, "bundle_id": BUNDLE_ID, "model_id": manifest["model_id"],
        "base_revision": REVISION, "artifact_mode": mode,
    }
    return bundle, report


class OfflineBundleRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle, self.report = fixture_bundle(self.root)

    def _runtime_versions(self, name):
        return {x["package"]: x["version"] for x in RUNTIME}[name]

    def test_merged_bundle_runs_with_local_only_flags_and_records_measurements(self):
        model = FakeModel()
        tokenizer = FakeTokenizer()
        auto_tokenizer = types.SimpleNamespace(from_pretrained=unittest.mock.Mock(return_value=tokenizer))
        auto_model = types.SimpleNamespace(from_pretrained=unittest.mock.Mock(return_value=model))
        fake_transformers = types.SimpleNamespace(
            AutoTokenizer=auto_tokenizer, AutoModelForCausalLM=auto_model
        )
        fake_torch = types.SimpleNamespace(set_num_threads=unittest.mock.Mock(), no_grad=nullcontext)
        with patch.object(runner, "verify_bundle", return_value=self.report), \
             patch.object(runner.package_metadata, "version", side_effect=self._runtime_versions), \
             patch.object(runner, "_available_memory_bytes", return_value=16 * runner.GIB), \
             patch.dict("sys.modules", {"torch": fake_torch, "transformers": fake_transformers}):
            result = runner.run_bundle(self.bundle, BUNDLE_ID, "Сайн уу", 8, 2)
        self.assertEqual(result["output"], "Монгол хариу")
        self.assertEqual(result["completion_tokens"], 3)
        self.assertEqual(result["artifact_mode"], "merged")
        self.assertFalse(result["model_quality_evaluated"])
        self.assertIn("OS egress not enforced", result["network_policy"])
        kwargs = auto_model.from_pretrained.call_args.kwargs
        self.assertTrue(kwargs["local_files_only"])
        self.assertFalse(kwargs["trust_remote_code"])
        self.assertTrue(kwargs["use_safetensors"])
        self.assertEqual(auto_model.from_pretrained.call_args.args[0], str(self.bundle / "model"))
        self.assertEqual(auto_tokenizer.from_pretrained.call_args.kwargs["local_files_only"], True)
        self.assertEqual(model.generate_kwargs["do_sample"], False)
        self.assertEqual(model.generate_kwargs["max_new_tokens"], 8)

    def test_bundle_id_mismatch_refuses_before_runtime_import(self):
        with patch.object(runner, "verify_bundle", return_value=self.report):
            with self.assertRaisesRegex(ValueError, "trusted expected ID"):
                runner.run_bundle(self.bundle, "b" * 64, "Сайн уу")

    def test_runtime_pin_mismatch_refuses(self):
        with patch.object(runner, "verify_bundle", return_value=self.report), \
             patch.object(runner.package_metadata, "version", return_value="999.0"):
            with self.assertRaisesRegex(RuntimeError, "runtime pin mismatch"):
                runner.run_bundle(self.bundle, BUNDLE_ID, "Сайн уу")

    def test_insufficient_ram_fails_before_loading_model(self):
        with patch.object(runner, "verify_bundle", return_value=self.report), \
             patch.object(runner.package_metadata, "version", side_effect=self._runtime_versions), \
             patch.object(runner, "_available_memory_bytes", return_value=1 * runner.GIB):
            with self.assertRaisesRegex(RuntimeError, "insufficient available RAM"):
                runner.run_bundle(self.bundle, BUNDLE_ID, "Сайн уу")

    def test_python_network_guard_blocks_socket_and_restores_environment(self):
        import os
        import socket
        old = os.environ.get("HF_HUB_OFFLINE")
        original = socket.socket.connect
        with runner.offline_network_guard():
            self.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
            sock = socket.socket()
            try:
                with self.assertRaisesRegex(RuntimeError, "outbound networking is blocked"):
                    sock.connect(("127.0.0.1", 1))
            finally:
                sock.close()
        self.assertIs(socket.socket.connect, original)
        self.assertEqual(os.environ.get("HF_HUB_OFFLINE"), old)

    def test_base_plus_adapter_requires_and_uses_peft_pin(self):
        bundle, report = fixture_bundle(self.root / "adapter-case", mode="base-plus-adapter")
        model = FakeModel()
        tokenizer = FakeTokenizer()
        auto_tokenizer = types.SimpleNamespace(from_pretrained=unittest.mock.Mock(return_value=tokenizer))
        auto_model = types.SimpleNamespace(from_pretrained=unittest.mock.Mock(return_value=model))
        peft_model = types.SimpleNamespace(from_pretrained=unittest.mock.Mock(return_value=model))
        fake_transformers = types.SimpleNamespace(
            AutoTokenizer=auto_tokenizer, AutoModelForCausalLM=auto_model
        )
        fake_torch = types.SimpleNamespace(set_num_threads=unittest.mock.Mock(), no_grad=nullcontext)
        fake_peft = types.SimpleNamespace(PeftModel=peft_model)
        with patch.object(runner, "verify_bundle", return_value=report), \
             patch.object(runner.package_metadata, "version", side_effect=self._runtime_versions), \
             patch.object(runner, "_available_memory_bytes", return_value=16 * runner.GIB), \
             patch.dict("sys.modules", {
                 "torch": fake_torch, "transformers": fake_transformers, "peft": fake_peft
             }):
            result = runner.run_bundle(bundle, BUNDLE_ID, "Сайн уу", 8, 2)
        self.assertEqual(result["artifact_mode"], "base-plus-adapter")
        self.assertEqual(auto_model.from_pretrained.call_args.args[0], str(bundle / "model" / "base"))
        self.assertEqual(peft_model.from_pretrained.call_args.args[1], str(bundle / "model" / "adapter"))
        self.assertTrue(peft_model.from_pretrained.call_args.kwargs["local_files_only"])


if __name__ == "__main__":
    unittest.main()
