"""Compare two benchmark directories without hiding comparability gaps."""
import argparse
import json
import re
from pathlib import Path


HEX40_64 = re.compile(r"^[0-9a-f]{40,64}$")
DECODE_KEYS = ("seed", "do_sample", "max_new_tokens", "thinking")


def load_run(folder):
    path = Path(folder)
    return (
        json.loads((path / "metadata.json").read_text(encoding="utf-8")),
        json.loads((path / "scores.json").read_text(encoding="utf-8")),
    )


def validate_run(metadata, scores):
    errors = []
    for key in ("model", "revision", "device", "dtype", "cases_sha256", "status",
                "total_generation_seconds") + DECODE_KEYS:
        if key not in metadata:
            errors.append(f"metadata missing: {key}")
    if not HEX40_64.fullmatch(str(metadata.get("revision", ""))):
        errors.append("revision must be an immutable 40-64 character lowercase hex hash")
    if not re.fullmatch(r"[0-9a-f]{64}", str(metadata.get("cases_sha256", ""))):
        errors.append("cases_sha256 must be a SHA-256 hex digest")
    if metadata.get("status") != "completed":
        errors.append("run status must be completed")
    seconds = metadata.get("total_generation_seconds")
    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or seconds <= 0:
        errors.append("total_generation_seconds must be positive")
    for key in ("metric", "correct", "total", "accuracy", "missing"):
        if key not in scores:
            errors.append(f"scores missing: {key}")
    total, correct, accuracy = scores.get("total"), scores.get("correct"), scores.get("accuracy")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        errors.append("scores.total must be a positive integer")
    if not isinstance(correct, int) or isinstance(correct, bool) or not isinstance(total, int) or not 0 <= correct <= total:
        errors.append("scores.correct must be between zero and total")
    if isinstance(total, int) and total > 0 and isinstance(correct, int) and isinstance(accuracy, (int, float)):
        if abs(accuracy - correct / total) > 1e-12:
            errors.append("accuracy disagrees with correct/total")
    else:
        errors.append("scores.accuracy must be numeric")
    adapter = metadata.get("adapter")
    if adapter is not None:
        if not isinstance(adapter, dict):
            errors.append("adapter must be an object")
        else:
            for key in ("base_model", "base_revision"):
                if not adapter.get(key):
                    errors.append(f"adapter missing: {key}")
            if not HEX40_64.fullmatch(str(adapter.get("base_revision", ""))):
                errors.append("adapter base_revision must be immutable")
    return errors


def compare_runs(baseline, candidate):
    base_meta, base_scores = baseline
    cand_meta, cand_scores = candidate
    errors = [f"baseline: {e}" for e in validate_run(base_meta, base_scores)]
    errors += [f"candidate: {e}" for e in validate_run(cand_meta, cand_scores)]
    mismatches = []
    if base_meta.get("cases_sha256") != cand_meta.get("cases_sha256"):
        mismatches.append("cases_sha256")
    if base_scores.get("metric") != cand_scores.get("metric"):
        mismatches.append("metric")
    if base_scores.get("total") != cand_scores.get("total"):
        mismatches.append("total")
    for key in DECODE_KEYS:
        if base_meta.get(key) != cand_meta.get(key):
            mismatches.append(key)
    base_total, cand_total = base_scores.get("total", 0), cand_scores.get("total", 0)
    base_latency = base_meta.get("total_generation_seconds", 0) / base_total if base_total else None
    cand_latency = cand_meta.get("total_generation_seconds", 0) / cand_total if cand_total else None
    resource_fields = ("hardware", "peak_vram_gb", "estimated_cost_usd")
    def resource_missing(meta, key):
        value = meta.get(key)
        if key == "hardware":
            return not isinstance(value, str) or not value.strip()
        return not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
    missing_resources = [
        f"{side}.{key}"
        for side, meta in (("baseline", base_meta), ("candidate", cand_meta))
        for key in resource_fields if resource_missing(meta, key)
    ]
    comparable = not errors and not mismatches
    quality_improved = comparable and cand_scores["accuracy"] > base_scores["accuracy"]
    promotion_eligible = bool(
        quality_improved and not missing_resources and cand_scores.get("missing") == 0)
    return {
        "comparable": comparable,
        "validation_errors": errors,
        "comparability_mismatches": mismatches,
        "baseline": {
            "model": base_meta.get("model"), "revision": base_meta.get("revision"),
            "accuracy": base_scores.get("accuracy"), "seconds_per_case": base_latency,
        },
        "candidate": {
            "model": cand_meta.get("model"), "revision": cand_meta.get("revision"),
            "accuracy": cand_scores.get("accuracy"), "seconds_per_case": cand_latency,
        },
        "accuracy_delta": (cand_scores.get("accuracy", 0) - base_scores.get("accuracy", 0)) if comparable else None,
        "seconds_per_case_delta": (cand_latency - base_latency) if comparable else None,
        "missing_resource_measurements": missing_resources,
        "quality_improved": quality_improved,
        "promotion_eligible": promotion_eligible,
        "note": "Promotion requires comparable settings, higher measured accuracy, no missing predictions, and recorded hardware/VRAM/cost. Human review is separate.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    args = parser.parse_args()
    try:
        report = compare_runs(load_run(args.baseline), load_run(args.candidate))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["comparable"]:
        parser.exit(1)


if __name__ == "__main__":
    main()
