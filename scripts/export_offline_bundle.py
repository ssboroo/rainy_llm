#!/usr/bin/env python3
"""Build and verify a local-only RAINY model bundle; no model loading or network access."""
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCHEMA_VERSION = 1
MANIFEST_NAME = "bundle-manifest.json"
INCOMPLETE_NAME = "BUNDLE_INCOMPLETE"
REVISION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside_git(path):
    path = Path(path).resolve()
    return any((parent / ".git").exists() for parent in (path, *path.parents))


def _collect_files(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("artifact root must be a real directory")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlinks are not accepted in offline bundles")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("bundle may contain only regular files")
        relative = path.relative_to(root).as_posix()
        if ".git" in Path(relative).parts:
            raise ValueError("Git metadata must not be packaged")
        files[relative] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    if not files:
        raise ValueError("artifact directory is empty")
    return files


def _require_file(path, description):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing required {description}: {path.name}")
    return path


def _chat_template_info(model_root):
    model_root = Path(model_root)
    config_path = model_root / "tokenizer_config.json"
    if config_path.is_file() and not config_path.is_symlink():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("tokenizer_config.json is not valid UTF-8 JSON") from exc
        if not isinstance(config, dict):
            raise ValueError("tokenizer_config.json must contain a JSON object")
        template = config.get("chat_template")
        if template:
            canonical = json.dumps(
                template, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            return {
                "source": "tokenizer_config.json:chat_template",
                "sha256": sha256_bytes(canonical),
            }
    template_path = model_root / "tokenizer.chat_template.jinja"
    if template_path.is_file() and not template_path.is_symlink():
        return {
            "source": template_path.name,
            "sha256": sha256_file(template_path),
        }
    raise ValueError("explicit chat template is required; implicit runtime fallback is refused")


def _validate_model_layout(root, mode):
    root = Path(root)
    if mode == "merged":
        model_root = root
        _require_file(model_root / "config.json", "model config")
        if not list(model_root.rglob("*.safetensors")):
            raise ValueError("merged model requires safetensors weights; pickle weights are refused")
        if not any((model_root / name).is_file() for name in ("tokenizer.json", "tokenizer.model", "vocab.json")):
            raise ValueError("merged model is missing tokenizer vocabulary files")
        template = _chat_template_info(model_root)
        return {"chat_template": template, "adapter_base_model_name_or_path": None}

    if mode == "base-plus-adapter":
        base = root / "base"
        adapter = root / "adapter"
        _require_file(base / "config.json", "base model config")
        if not list(base.rglob("*.safetensors")):
            raise ValueError("base model requires safetensors weights")
        if not any((base / name).is_file() for name in ("tokenizer.json", "tokenizer.model", "vocab.json")):
            raise ValueError("base model is missing tokenizer vocabulary files")
        _require_file(adapter / "adapter_config.json", "adapter config")
        _require_file(adapter / "adapter_model.safetensors", "adapter safetensors")
        try:
            adapter_config = json.loads((adapter / "adapter_config.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("adapter_config.json is not valid UTF-8 JSON") from exc
        template = _chat_template_info(base)
        base_name = adapter_config.get("base_model_name_or_path")
        return {
            "chat_template": {"source": "base/" + template["source"], "sha256": template["sha256"]},
            "adapter_base_model_name_or_path": base_name if isinstance(base_name, str) else None,
        }

    raise ValueError("unsupported artifact mode")


def _validate_url(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an explicit HTTP(S) URL")
    parsed = urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise ValueError(f"{field} must be an explicit HTTP(S) URL")


def _parse_runtime_pins(runtime):
    parsed = {}
    for pin in runtime:
        if "==" not in pin:
            raise ValueError("runtime pins must use exact package==version syntax")
        package, version = pin.split("==", 1)
        if not package.strip() or not version.strip() or version.strip().lower() in ("latest", "*"):
            raise ValueError("runtime pins must have a concrete version")
        if any(operator in version for operator in (">", "<", "~", "*", ";")):
            raise ValueError("runtime versions must be exact, not ranges")
        key = package.strip().lower().replace("_", "-")
        if key in parsed:
            raise ValueError(f"duplicate runtime package: {package}")
        parsed[key] = version.strip()
    if not parsed:
        raise ValueError("at least one exact runtime pin is required")
    return [{"package": name, "version": parsed[name]} for name in sorted(parsed)]


def _validate_metadata(model_id, revision, weights_license, code_license,
                       model_card_url, license_url, runtime, training_run_sha256=None):
    if not isinstance(model_id, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", model_id):
        raise ValueError("model ID must be an exact namespace/name identifier")
    if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
        raise ValueError("revision must be an immutable 40-character Git commit SHA")
    if (not isinstance(weights_license, str) or not weights_license.strip()
            or not isinstance(code_license, str) or not code_license.strip()):
        raise ValueError("weights and code licenses must be stated separately")
    _validate_url(model_card_url, "model card URL")
    _validate_url(license_url, "license URL")
    pins = _parse_runtime_pins(runtime)
    if training_run_sha256 is not None and (
            not isinstance(training_run_sha256, str)
            or not SHA256_RE.fullmatch(training_run_sha256)):
        raise ValueError("training-run identity must be a 64-character SHA-256")
    return pins


def _canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _bundle_id(manifest):
    content = {key: value for key, value in manifest.items() if key != "bundle_id"}
    return sha256_bytes(_canonical_json(content))


def _write_json_exclusive(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _fsync_directory(path):
    if hasattr(os, "O_DIRECTORY"):
        descriptor = os.open(str(path), os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _verify_bundle_root(bundle):
    bundle = Path(bundle)
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValueError("bundle must be a real directory")
    if (bundle / INCOMPLETE_NAME).exists():
        raise ValueError("bundle has an incomplete-publication marker")
    manifest_path = bundle / MANIFEST_NAME
    _require_file(manifest_path, "bundle manifest")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("bundle manifest is not valid UTF-8 JSON") from exc
    required = {
        "schema_version", "artifact_mode", "model_id", "base_revision",
        "weights_license", "code_license", "model_card_url", "license_url",
        "runtime_pins", "chat_template", "files", "created_at_utc", "bundle_id",
        "license_evidence_status",
    }
    if not isinstance(manifest, dict) or not required.issubset(manifest):
        raise ValueError("bundle manifest is missing required fields")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported bundle manifest schema")
    if manifest["bundle_id"] != _bundle_id(manifest):
        raise ValueError("bundle manifest identity hash mismatch")
    pins = manifest["runtime_pins"]
    if not isinstance(pins, list) or any(
            not isinstance(pin, dict)
            or not isinstance(pin.get("package"), str)
            or not isinstance(pin.get("version"), str) for pin in pins):
        raise ValueError("bundle runtime pins must be a list of exact package/version objects")
    _validate_metadata(
        manifest["model_id"], manifest["base_revision"], manifest["weights_license"],
        manifest["code_license"], manifest["model_card_url"], manifest["license_url"],
        [f'{pin["package"]}=={pin["version"]}' for pin in pins],
        manifest.get("training_run_sha256"),
    )
    model_root = bundle / "model"
    actual = _collect_files(model_root)
    expected = manifest["files"]
    if not isinstance(expected, dict) or set(expected) != set(actual):
        raise ValueError("bundle file inventory does not match the manifest")
    for relative, metadata in expected.items():
        if metadata != actual[relative]:
            raise ValueError(f"bundle file hash/size mismatch: {relative}")
    layout = _validate_model_layout(model_root, manifest["artifact_mode"])
    if layout["chat_template"] != manifest["chat_template"]:
        raise ValueError("chat-template identity mismatch")
    return manifest


def create_bundle(source, destination, *, mode, model_id, revision, weights_license,
                  code_license, model_card_url, license_url, runtime,
                  max_bytes=16 * 1024**3, training_run_sha256=None):
    source_input = Path(source)
    if source_input.is_symlink():
        raise ValueError("source directory symlink is refused")
    source_root = source_input.resolve(strict=True)
    if not source_root.is_dir() or _inside_git(source_root):
        raise ValueError("source model must be a directory outside every Git checkout")
    source_files = _collect_files(source_root)
    total_bytes = sum(item["bytes"] for item in source_files.values())
    if type(max_bytes) is not int or max_bytes <= 0 or total_bytes > max_bytes:
        raise ValueError(f"source size {total_bytes} exceeds the configured byte cap {max_bytes}")
    layout = _validate_model_layout(source_root, mode)
    pins = _validate_metadata(
        model_id, revision, weights_license, code_license,
        model_card_url, license_url, runtime, training_run_sha256,
    )

    destination_path = Path(destination).resolve()
    if (source_root == destination_path or source_root in destination_path.parents
            or destination_path in source_root.parents):
        raise ValueError("source and destination must be disjoint")
    if destination_path.exists():
        raise FileExistsError(f"destination already exists: {destination_path}")
    if not destination_path.parent.is_dir() or _inside_git(destination_path):
        raise ValueError("destination parent must exist and be outside every Git checkout")

    staging = Path(tempfile.mkdtemp(prefix=f".{destination_path.name}.staging-", dir=str(destination_path.parent)))
    try:
        shutil.copytree(source_root, staging / "model", symlinks=False)
        copied_files = _collect_files(staging / "model")
        if copied_files != source_files:
            raise ValueError("copied artifact differs from the source snapshot")
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "artifact_mode": mode,
            "model_id": model_id,
            "base_revision": revision.lower(),
            "weights_license": weights_license.strip(),
            "code_license": code_license.strip(),
            "model_card_url": model_card_url,
            "license_url": license_url,
            "runtime_pins": pins,
            "chat_template": layout["chat_template"],
            "adapter_base_model_name_or_path": layout["adapter_base_model_name_or_path"],
            "training_run_sha256": training_run_sha256,
            "source_file_count": len(copied_files),
            "source_bytes": total_bytes,
            "files": copied_files,
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "license_evidence_status": "metadata supplied; legal permission and redistribution scope are not independently verified",
            "verification_scope": "file inventory, SHA-256, declared revision, tokenizer template presence; not tensor compatibility, inference, quality, or OS-level network isolation",
        }
        manifest["bundle_id"] = _bundle_id(manifest)
        _write_json_exclusive(staging / MANIFEST_NAME, manifest)
        _verify_bundle_root(staging)

        # Claim the final path exclusively before moving verified content into it.
        destination_path.mkdir(mode=0o700)
        _write_json_exclusive(destination_path / INCOMPLETE_NAME, {"reason": "publication in progress"})
        os.replace(staging / "model", destination_path / "model")
        os.replace(staging / MANIFEST_NAME, destination_path / MANIFEST_NAME)
        (destination_path / INCOMPLETE_NAME).unlink()
        _fsync_directory(destination_path)
        _fsync_directory(destination_path.parent)
        staging.rmdir()
        return _verify_bundle_root(destination_path)
    except Exception:
        if staging.exists() and not (staging / INCOMPLETE_NAME).exists():
            try:
                _write_json_exclusive(staging / INCOMPLETE_NAME, {"reason": "creation failed; inspect before retry"})
            except OSError:
                pass
        raise


def verify_bundle(bundle):
    bundle_path = Path(bundle)
    if bundle_path.is_symlink():
        raise ValueError("bundle directory symlink is refused")
    bundle_path = bundle_path.resolve(strict=True)
    if _inside_git(bundle_path):
        raise ValueError("model bundles must remain outside Git checkouts")
    manifest = _verify_bundle_root(bundle_path)
    return {
        "verified": True,
        "bundle_id": manifest["bundle_id"],
        "model_id": manifest["model_id"],
        "base_revision": manifest["base_revision"],
        "artifact_mode": manifest["artifact_mode"],
        "files": len(manifest["files"]),
        "bytes": manifest["source_bytes"],
        "chat_template_sha256": manifest["chat_template"]["sha256"],
        "network_access": "none",
        "inference_performed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="copy an existing local model artifact to a new private bundle directory")
    create.add_argument("--source", required=True)
    create.add_argument("--destination", required=True)
    create.add_argument("--mode", choices=("merged", "base-plus-adapter"), required=True)
    create.add_argument("--model-id", required=True)
    create.add_argument("--revision", required=True, help="immutable 40-character upstream base commit SHA")
    create.add_argument("--weights-license", required=True)
    create.add_argument("--code-license", required=True)
    create.add_argument("--model-card-url", required=True)
    create.add_argument("--license-url", required=True)
    create.add_argument("--runtime", action="append", default=[], metavar="PACKAGE==VERSION")
    create.add_argument("--max-bytes", type=int, default=16 * 1024**3)
    create.add_argument("--training-run-sha256")
    verify = commands.add_parser("verify", help="re-hash a previously created bundle without loading weights")
    verify.add_argument("--bundle", required=True)
    args = parser.parse_args()
    try:
        if args.command == "create":
            manifest = create_bundle(
                args.source, args.destination, mode=args.mode, model_id=args.model_id,
                revision=args.revision, weights_license=args.weights_license,
                code_license=args.code_license, model_card_url=args.model_card_url,
                license_url=args.license_url, runtime=args.runtime,
                max_bytes=args.max_bytes, training_run_sha256=args.training_run_sha256,
            )
            print(json.dumps({"created": True, "bundle_id": manifest["bundle_id"],
                              "path": str(Path(args.destination).resolve()),
                              "files": len(manifest["files"]), "bytes": manifest["source_bytes"]},
                             ensure_ascii=False, indent=2))
        else:
            print(json.dumps(verify_bundle(args.bundle), ensure_ascii=False, indent=2))
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"offline bundle error: {exc}\n")


if __name__ == "__main__":
    main()
