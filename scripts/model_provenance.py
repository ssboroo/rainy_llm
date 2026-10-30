"""Build explicit, hash-bound provenance for a local pretrained model snapshot."""
import hashlib
import json
import re
from pathlib import PurePosixPath
from urllib.parse import urlparse

MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*$")
REVISION_RE = re.compile(r"^[0-9a-fA-F]{40}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
TOKENIZER_FILES = frozenset({
    "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
    "added_tokens.json", "vocab.json", "merges.txt", "vocab.txt",
    "spiece.model", "sentencepiece.bpe.model", "tokenizer.model",
    "chat_template.jinja",
})


def _required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be stated explicitly")
    return value.strip()


def _https_url(value, label):
    value = _required_text(value, label)
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{label} must be an HTTPS URL without embedded credentials")
    return value


def _canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_model_provenance(*, model_id, revision, weights_license, code_license,
                           model_card_url, license_url, model_files, chat_template):
    """Validate declarations and fingerprint tokenizer/template/model snapshot bytes.

    Model ID, revision, license labels and URLs are supplied by the operator. The
    returned hashes bind the local snapshot but do not independently authenticate
    upstream provenance or establish legal redistribution rights.
    """
    model_id = _required_text(model_id, "model ID")
    if not MODEL_ID_RE.fullmatch(model_id):
        raise ValueError("model ID must be an exact namespace/name identifier")
    revision = _required_text(revision, "model revision")
    if not REVISION_RE.fullmatch(revision):
        raise ValueError("model revision must be an immutable 40-character Git commit SHA")
    weights_license = _required_text(weights_license, "weights license")
    code_license = _required_text(code_license, "code license")
    model_card_url = _https_url(model_card_url, "model card URL")
    license_url = _https_url(license_url, "license URL")

    if not isinstance(model_files, dict) or not model_files:
        raise ValueError("local model file hashes are required")
    files = {}
    for name, digest in model_files.items():
        if not isinstance(name, str) or not name or "\\" in name:
            raise ValueError("model file names must be normalized relative paths")
        parts = name.split("/")
        path = PurePosixPath(name)
        if path.is_absolute() or any(part in ("", ".", "..") for part in parts):
            raise ValueError("model file names must not escape the local snapshot")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ValueError(f"invalid SHA-256 for model file: {name}")
        files[name] = digest.lower()

    tokenizer_files = {
        name: files[name] for name in sorted(files)
        if PurePosixPath(name).name in TOKENIZER_FILES
    }
    if not tokenizer_files:
        raise ValueError("local snapshot has no recognized tokenizer files")
    if isinstance(chat_template, str) and chat_template.strip():
        template_bytes = chat_template.encode("utf-8")
        template_format = "jinja-string"
    elif isinstance(chat_template, dict) and chat_template:
        template_bytes = _canonical_json(chat_template)
        template_format = "named-templates-json"
    else:
        raise ValueError("an explicit non-empty tokenizer chat template is required")

    return {
        "schema": 1,
        "model_id": model_id,
        "revision": revision.lower(),
        "weights_license": weights_license,
        "code_license": code_license,
        "model_card_url": model_card_url,
        "license_url": license_url,
        "model_files_sha256": hashlib.sha256(_canonical_json(files)).hexdigest(),
        "tokenizer_files": tokenizer_files,
        "tokenizer_sha256": hashlib.sha256(_canonical_json(tokenizer_files)).hexdigest(),
        "chat_template_format": template_format,
        "chat_template_sha256": hashlib.sha256(template_bytes).hexdigest(),
        "provenance_status": (
            "operator-supplied declarations; hashes bind local files; URLs and license "
            "claims are recorded but not independently authenticated"
        ),
    }
