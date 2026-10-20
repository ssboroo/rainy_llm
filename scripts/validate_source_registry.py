"""Validate the machine-readable dataset decision registry using stdlib only."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = {
    "id", "name", "languages", "purpose", "decision", "source_url",
    "license_id", "license_evidence_url", "license_verified", "snapshot_ref",
    "immutable_ref", "training_allowed", "evaluation_only",
    "attribution_required", "notes",
}
DECISIONS = {"pilot-approved", "evaluation-candidate", "hold"}


def _https(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme == "https" and parsed.netloc)


def validate_registry(document):
    errors = []
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        return ["schema_version must be 1"]
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["sources must be a non-empty list"]
    seen = set()
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = sorted(REQUIRED - source.keys())
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
            continue
        source_id = source["id"]
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"{label}.id must be non-empty")
        elif source_id in seen:
            errors.append(f"duplicate id: {source_id}")
        seen.add(source_id)
        if source["decision"] not in DECISIONS:
            errors.append(f"{label}.decision is invalid")
        for key in ("languages", "purpose"):
            if not isinstance(source[key], list) or not source[key] or not all(
                    isinstance(item, str) and item.strip() for item in source[key]):
                errors.append(f"{label}.{key} must be a non-empty string list")
        for key in ("source_url", "license_evidence_url"):
            if not _https(source[key]):
                errors.append(f"{label}.{key} must be an HTTPS URL")
        for key in ("license_verified", "immutable_ref", "training_allowed",
                    "evaluation_only", "attribution_required"):
            if not isinstance(source[key], bool):
                errors.append(f"{label}.{key} must be boolean")
        if source["license_verified"] != (source["license_id"] != "UNKNOWN"):
            errors.append(f"{label} license_id and license_verified disagree")
        if source["decision"] == "pilot-approved" and not (
                source["license_verified"] and source["immutable_ref"]):
            errors.append(f"{label} approved sources need verified license and immutable ref")
        if source["decision"] == "hold" and source["training_allowed"]:
            errors.append(f"{label} held sources cannot allow training")
        if source["evaluation_only"] and source["training_allowed"]:
            errors.append(f"{label} evaluation-only source cannot allow training")
        if source["evaluation_only"] and "evaluation" not in source["purpose"]:
            errors.append(f"{label} evaluation-only source needs evaluation purpose")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="data/source_registry.json")
    args = parser.parse_args()
    try:
        document = json.loads(Path(args.path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(1, f"{exc}\n")
    errors = validate_registry(document)
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(f"OK: {len(document['sources'])} sources")


if __name__ == "__main__":
    main()
