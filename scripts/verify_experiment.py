"""Recompute an experiment from raw predictions and verify recorded aggregates."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

try:
    from evaluate import score
    from prepare_data import read_rows
except ImportError:  # imported as scripts.verify_experiment in tests
    from scripts.evaluate import score
    from scripts.prepare_data import read_rows


SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def verify_experiment(experiment, cases_path):
    folder = Path(experiment)
    metadata_path = folder / "metadata.json"
    predictions_path = folder / "predictions.jsonl"
    scores_path = folder / "scores.json"
    errors, warnings = [], []
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    recorded_scores = json.loads(scores_path.read_text(encoding="utf-8"))
    cases = read_rows(cases_path)
    predictions = read_rows(predictions_path)
    if not isinstance(metadata, dict):
        errors.append("metadata.json must contain an object")
        metadata = {}
    if not isinstance(recorded_scores, dict):
        errors.append("scores.json must contain an object")
        recorded_scores = {}
    case_hash = sha256(cases_path)
    if metadata.get("cases_sha256") != case_hash:
        errors.append("metadata cases_sha256 does not match the cases file")
    if metadata.get("status") != "completed":
        errors.append("metadata status must be completed")
    row_seconds, row_tokens, row_limits = 0.0, 0, 0
    for index, row in enumerate(predictions):
        label = f"prediction[{index}]"
        seconds = row.get("seconds") if isinstance(row, dict) else None
        tokens = row.get("generated_tokens") if isinstance(row, dict) else None
        hit_limit = row.get("hit_token_limit") if isinstance(row, dict) else None
        if not finite_number(seconds) or seconds < 0:
            errors.append(f"{label}.seconds must be finite and non-negative")
        else:
            row_seconds += seconds
        if type(tokens) is not int or tokens < 0:
            errors.append(f"{label}.generated_tokens must be a non-negative integer")
        else:
            row_tokens += tokens
        if type(hit_limit) is not bool:
            errors.append(f"{label}.hit_token_limit must be boolean")
        else:
            row_limits += int(hit_limit)
        prompt_hash = row.get("prompt_sha256") if isinstance(row, dict) else None
        if prompt_hash is not None and not SHA256.fullmatch(str(prompt_hash)):
            errors.append(f"{label}.prompt_sha256 must be a SHA-256 digest")
    try:
        recomputed = score(cases, predictions)
    except ValueError as exc:
        errors.append(f"prediction scoring failed: {exc}")
        recomputed = None
    if recomputed is not None:
        if recomputed != recorded_scores:
            errors.append("scores.json does not match scores recomputed from predictions")
        if recomputed["missing"]:
            errors.append("completed experiment has missing predictions")
    recorded_seconds = metadata.get("total_generation_seconds")
    if not finite_number(recorded_seconds) or recorded_seconds <= 0:
        errors.append("metadata total_generation_seconds must be finite and positive")
    elif abs(recorded_seconds - row_seconds) > 1e-6:
        errors.append("metadata total_generation_seconds does not equal prediction rows")
    for key, actual in (("generated_tokens", row_tokens), ("token_limit_hits", row_limits)):
        if key not in metadata:
            warnings.append(f"legacy metadata missing aggregate: {key}")
        elif metadata[key] != actual:
            errors.append(f"metadata {key} does not equal prediction rows")
    report = {
        "valid": not errors,
        "experiment": folder.name,
        "errors": errors,
        "warnings": warnings,
        "files": {
            "cases_sha256": case_hash,
            "metadata_sha256": sha256(metadata_path),
            "predictions_sha256": sha256(predictions_path),
            "scores_sha256": sha256(scores_path),
        },
        "measurements": {
            "cases": len(cases),
            "predictions": len(predictions),
            "correct": recomputed.get("correct") if recomputed else None,
            "total_generation_seconds": round(row_seconds, 10),
            "generated_tokens": row_tokens,
            "token_limit_hits": row_limits,
        },
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment")
    parser.add_argument("--cases", default="evaluation/mn_smoke.jsonl")
    parser.add_argument("--output", help="Write a new JSON report; never overwrite")
    args = parser.parse_args()
    try:
        report = verify_experiment(args.experiment, args.cases)
        encoded = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        print(encoded, end="")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, str(exc) + "\n")
    if not report["valid"]:
        parser.exit(1)


if __name__ == "__main__":
    main()
