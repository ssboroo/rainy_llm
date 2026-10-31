#!/usr/bin/env python3
"""Run a hash-verified safetensors bundle with a local-only Transformers runtime."""
import argparse
import gc
import hashlib
import importlib.metadata as package_metadata
import json
import os
import platform
import re
import socket
import sys
import time
from contextlib import contextmanager
from pathlib import Path

try:
    from .export_offline_bundle import MANIFEST_NAME, verify_bundle
except ImportError:  # Direct execution: scripts/ is sys.path[0].
    from export_offline_bundle import MANIFEST_NAME, verify_bundle

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
GIB = 1024 ** 3
OFFLINE_ENV = {
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "HF_DATASETS_OFFLINE": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "TOKENIZERS_PARALLELISM": "false",
}


def _read_manifest(bundle, expected_bundle_id):
    if not isinstance(expected_bundle_id, str) or not HEX64.fullmatch(expected_bundle_id):
        raise ValueError("expected bundle ID must be a 64-character SHA-256 hex digest")
    bundle_path = Path(bundle).resolve(strict=True)
    report = verify_bundle(bundle_path)
    if report.get("bundle_id", "").lower() != expected_bundle_id.lower():
        raise ValueError("bundle ID does not match the trusted expected ID")
    manifest_path = bundle_path / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("bundle_id", "").lower() != expected_bundle_id.lower():
        raise ValueError("manifest bundle ID differs from verified bundle ID")
    if manifest.get("artifact_mode") not in ("merged", "base-plus-adapter"):
        raise ValueError("unsupported offline artifact mode")
    return bundle_path, manifest


def _validate_runtime_pins(manifest):
    pins = manifest.get("runtime_pins")
    if not isinstance(pins, list):
        raise ValueError("bundle runtime pins are missing")
    pinned = {}
    for item in pins:
        if not isinstance(item, dict):
            raise ValueError("malformed runtime pin")
        name, version = item.get("package"), item.get("version")
        if not isinstance(name, str) or not name.strip() or not isinstance(version, str) or not version.strip():
            raise ValueError("malformed runtime package/version")
        key = name.lower().replace("_", "-")
        if key in pinned:
            raise ValueError("duplicate runtime package pin")
        pinned[key] = version
    required = {"torch", "transformers"}
    if manifest["artifact_mode"] == "base-plus-adapter":
        required.add("peft")
    missing = sorted(required - set(pinned))
    if missing:
        raise ValueError("bundle does not pin required runtime packages: " + ", ".join(missing))
    for name, expected in sorted(pinned.items()):
        try:
            actual = package_metadata.version(name)
        except package_metadata.PackageNotFoundError as exc:
            raise RuntimeError(f"required pinned runtime package is not installed: {name}=={expected}") from exc
        if actual != expected:
            raise RuntimeError(f"runtime pin mismatch for {name}: expected {expected}, found {actual}")
    return {name: pinned[name] for name in sorted(pinned)}


def _available_memory_bytes():
    try:
        import psutil
        return int(psutil.virtual_memory().available)
    except ImportError:
        pass
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
        except (OSError, ValueError, IndexError):
            pass
    if os.name == "nt":
        try:
            import ctypes
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            status = MemoryStatus()
            status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.ullAvailPhys)
        except (AttributeError, OSError, TypeError):
            pass
    if hasattr(os, "sysconf"):
        try:
            return int(os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE"))
        except (OSError, ValueError, TypeError):
            pass
    return None


def _minimum_memory_bytes(manifest):
    source_bytes = manifest.get("source_bytes")
    if type(source_bytes) is not int or source_bytes <= 0:
        raise ValueError("bundle manifest has no valid source_bytes size")
    # Conservative preflight only; not a measured peak-RSS prediction.
    return max(3 * source_bytes, 3 * GIB) + GIB


@contextmanager
def offline_network_guard():
    old_env = {key: os.environ.get(key) for key in OFFLINE_ENV}
    targets = [(socket, "create_connection"), (socket.socket, "connect"),
               (socket.socket, "connect_ex"), (socket.socket, "sendto")]
    old_methods = [(obj, name, getattr(obj, name)) for obj, name in targets]

    def denied(*args, **kwargs):
        raise RuntimeError("outbound networking is blocked by the offline model runner")

    try:
        os.environ.update(OFFLINE_ENV)
        for obj, name in targets:
            setattr(obj, name, denied)
        yield
    finally:
        for obj, name, original in old_methods:
            setattr(obj, name, original)
        for key, old in old_env.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def _load_template(model_root, manifest):
    source = manifest.get("chat_template", {}).get("source")
    expected = manifest.get("chat_template", {}).get("sha256")
    if not isinstance(source, str) or not isinstance(expected, str) or not HEX64.fullmatch(expected):
        raise ValueError("bundle chat-template identity is missing")
    root = Path(model_root)
    if source.startswith("base/"):
        root = root / "base"
        source = source[len("base/"):]
    if source == "tokenizer_config.json:chat_template":
        config_path = root / "tokenizer_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        template = config.get("chat_template") if isinstance(config, dict) else None
        if not isinstance(template, str) or not template.strip():
            raise ValueError("offline runner requires one explicit string chat template")
        canonical = json.dumps(template, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
    elif source == "tokenizer.chat_template.jinja":
        raw = (root / source).read_bytes()
        template = raw.decode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        if not template.strip():
            raise ValueError("chat template file is empty")
    else:
        raise ValueError("unsupported chat-template source in bundle manifest")
    if digest.lower() != expected.lower():
        raise ValueError("chat-template hash differs from the verified manifest")
    return template


def _peak_rss_bytes():
    try:
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == "darwin" else value * 1024)
    except (ImportError, AttributeError, OSError, ValueError):
        return None


def run_bundle(bundle, expected_bundle_id, prompt, max_new_tokens=128, threads=4):
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must not be empty")
    if type(max_new_tokens) is not int or not 1 <= max_new_tokens <= 2048:
        raise ValueError("max_new_tokens must be between 1 and 2048")
    if type(threads) is not int or not 1 <= threads <= 64:
        raise ValueError("threads must be between 1 and 64")
    bundle_path, manifest = _read_manifest(bundle, expected_bundle_id)
    runtime_pins = _validate_runtime_pins(manifest)
    available = _available_memory_bytes()
    minimum = _minimum_memory_bytes(manifest)
    if available is None:
        raise RuntimeError("available RAM could not be measured; refusing unbounded model loading")
    if available < minimum:
        raise RuntimeError(
            f"insufficient available RAM: need at least {minimum} bytes by conservative preflight, "
            f"available {available}; no model was loaded"
        )

    model_root = bundle_path / "model"
    mode = manifest["artifact_mode"]
    tokenizer_root = model_root / "base" if mode == "base-plus-adapter" else model_root
    expected_template = _load_template(model_root, manifest)
    started = time.perf_counter()
    with offline_network_guard():
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_num_threads(threads)
        load_started = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(
            str(tokenizer_root), local_files_only=True, trust_remote_code=False
        )
        loaded_template = getattr(tokenizer, "chat_template", None)
        if loaded_template not in (None, expected_template):
            raise ValueError("loaded tokenizer chat template differs from the verified bundle template")
        tokenizer.chat_template = expected_template
        if mode == "merged":
            model = AutoModelForCausalLM.from_pretrained(
                str(model_root), local_files_only=True, trust_remote_code=False,
                use_safetensors=True, torch_dtype="auto",
            )
        else:
            from peft import PeftModel
            base_model = AutoModelForCausalLM.from_pretrained(
                str(model_root / "base"), local_files_only=True, trust_remote_code=False,
                use_safetensors=True, torch_dtype="auto",
            )
            model = PeftModel.from_pretrained(
                base_model, str(model_root / "adapter"), is_trainable=False,
                local_files_only=True,
            )
        model.eval()
        load_seconds = time.perf_counter() - load_started
        rendered = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True
        )
        encoded = tokenizer(rendered, return_tensors="pt", add_special_tokens=False)
        input_ids = encoded["input_ids"]
        prompt_tokens = int(input_ids.shape[-1])
        context_limit = None
        config = getattr(model, "config", None)
        for key in ("max_position_embeddings", "n_positions", "max_seq_len"):
            value = getattr(config, key, None) if config is not None else None
            if type(value) is int and value > 0:
                context_limit = value
                break
        if context_limit is not None and prompt_tokens + max_new_tokens > context_limit:
            raise ValueError(
                f"prompt plus output budget ({prompt_tokens + max_new_tokens}) exceeds model context {context_limit}"
            )
        pad_id = getattr(tokenizer, "pad_token_id", None)
        if pad_id is None:
            pad_id = getattr(tokenizer, "eos_token_id", None)
        kwargs = {"input_ids": input_ids, "max_new_tokens": max_new_tokens, "do_sample": False}
        attention_mask = encoded.get("attention_mask")
        if attention_mask is not None:
            kwargs["attention_mask"] = attention_mask
        if pad_id is not None:
            kwargs["pad_token_id"] = pad_id
        generation_started = time.perf_counter()
        with torch.no_grad():
            generated = model.generate(**kwargs)
        generation_seconds = time.perf_counter() - generation_started
        new_tokens = generated[0, prompt_tokens:]
        completion_tokens = int(new_tokens.shape[-1])
        output_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        result = {
            "output": output_text,
            "bundle_id": manifest["bundle_id"],
            "model_id": manifest["model_id"],
            "base_revision": manifest["base_revision"],
            "artifact_mode": mode,
            "training_run_sha256": manifest.get("training_run_sha256"),
            "chat_template_sha256": manifest["chat_template"]["sha256"],
            "runtime_pins": runtime_pins,
            "device": "cpu",
            "threads": threads,
            "decoding": {"do_sample": False, "max_new_tokens": max_new_tokens},
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "model_load_seconds": round(load_seconds, 6),
            "generation_seconds": round(generation_seconds, 6),
            "tokens_per_second": round(completion_tokens / generation_seconds, 4) if generation_seconds > 0 else None,
            "total_seconds": round(time.perf_counter() - started, 6),
            "available_ram_before_load_bytes": available,
            "conservative_minimum_ram_bytes": minimum,
            "peak_rss_bytes": _peak_rss_bytes(),
            "network_policy": "offline environment flags + local_files_only + Python socket guard; OS egress not enforced",
            "model_quality_evaluated": False,
        }
        del model, tokenizer
        gc.collect()
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--expected-bundle-id", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    try:
        result = run_bundle(args.bundle, args.expected_bundle_id, args.prompt,
                            args.max_new_tokens, args.threads)
    except (OSError, ValueError, RuntimeError, ImportError, KeyError, TypeError) as exc:
        parser.exit(1, f"offline bundle inference error: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
