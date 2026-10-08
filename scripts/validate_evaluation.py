"""Validate held-out evaluation JSONL and block accidental training overlap."""
import argparse
import datetime
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


STATUSES = {"draft-needs-human-review", "human-reviewed"}
REQUIRED = {"id", "category", "prompt", "answers", "review_status", "source"}
REVIEW_CHECKS = {
    "mongolian_wording", "answer_correct", "unambiguous",
    "source_independent", "exact_match_suitable",
}
REVIEWER_ROLES = {"human-reviewer", "independent-human-reviewer"}


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def case_fingerprint(row):
    """Bind review evidence to the exact evaluation content, not its status."""
    content = {key: row[key] for key in ("id", "category", "prompt", "answers", "source")}
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate_review_evidence(row, label):
    evidence = row.get("review_evidence")
    if not isinstance(evidence, dict):
        return [f"{label}.review_evidence must be an object for human-reviewed cases"]
    errors = []
    if evidence.get("case_sha256") != case_fingerprint(row):
        errors.append(f"{label}.review_evidence.case_sha256 does not match case content")
    if evidence.get("reviewer_role") not in REVIEWER_ROLES:
        errors.append(f"{label}.review_evidence.reviewer_role is invalid")
    reviewed_at = evidence.get("reviewed_at")
    try:
        if not isinstance(reviewed_at, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_at):
            raise ValueError
        datetime.date.fromisoformat(reviewed_at)
    except ValueError:
        errors.append(f"{label}.review_evidence.reviewed_at must be an ISO date")
    if evidence.get("decision") != "accept":
        errors.append(f"{label}.review_evidence.decision must be accept")
    checks = evidence.get("checks")
    if not isinstance(checks, dict) or set(checks) != REVIEW_CHECKS or not all(
            checks.get(key) is True for key in REVIEW_CHECKS):
        errors.append(f"{label}.review_evidence.checks must contain all required true checks")
    return errors


def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected object")
            rows.append(row)
    return rows


def validate_cases(cases, training_rows=(), release=False, min_cases=100):
    errors, ids, prompts = [], set(), set()
    categories, statuses = Counter(), Counter()
    training_prompts = set()
    for row in training_rows:
        if isinstance(row, dict):
            value = row.get("instruction", row.get("prompt"))
            if isinstance(value, str) and value.strip():
                training_prompts.add(normalized(value))
    if not isinstance(min_cases, int) or min_cases < 1:
        errors.append("min_cases must be a positive integer")
    if not cases:
        errors.append("evaluation set is empty")
    for index, row in enumerate(cases):
        label = f"case[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = sorted(REQUIRED - row.keys())
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
            continue
        for key in ("id", "category", "prompt", "review_status", "source"):
            if not isinstance(row[key], str) or not row[key].strip():
                errors.append(f"{label}.{key} must be a non-empty string")
        if not isinstance(row["answers"], list) or not row["answers"] or not all(
                isinstance(answer, str) and answer.strip() for answer in row["answers"]):
            errors.append(f"{label}.answers must be a non-empty string list")
        case_id = row["id"] if isinstance(row["id"], str) else None
        if case_id in ids:
            errors.append(f"duplicate id: {case_id}")
        ids.add(case_id)
        if isinstance(row["prompt"], str):
            prompt = normalized(row["prompt"])
            if prompt in prompts:
                errors.append(f"duplicate normalized prompt: {case_id}")
            prompts.add(prompt)
            if prompt in training_prompts:
                errors.append(f"training overlap: {case_id}")
        status = row["review_status"]
        if status not in STATUSES:
            errors.append(f"{label}.review_status is invalid")
        else:
            statuses[status] += 1
            if status == "human-reviewed":
                errors.extend(validate_review_evidence(row, label))
        if isinstance(row["category"], str):
            categories[row["category"]] += 1
    if release:
        if len(cases) < min_cases:
            errors.append(f"release requires at least {min_cases} cases")
        if statuses.get("draft-needs-human-review", 0):
            errors.append("release contains draft cases")
        if statuses.get("human-reviewed", 0) != len(cases):
            errors.append("release requires every case to be human-reviewed")
    report = {
        "cases": len(cases),
        "categories": dict(sorted(categories.items())),
        "review_statuses": dict(sorted(statuses.items())),
        "training_prompts_checked": len(training_prompts),
        "release_ready": not errors and release,
    }
    return errors, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="?", default="evaluation/mn_smoke.jsonl")
    parser.add_argument("--training", action="append", default=[], help="Training JSONL; repeatable")
    parser.add_argument("--release", action="store_true", help="Require >= min-cases and human review")
    parser.add_argument("--min-cases", type=int, default=100)
    args = parser.parse_args()
    try:
        cases = read_jsonl(args.cases)
        training = []
        for path in args.training:
            training.extend(read_jsonl(path))
        errors, report = validate_cases(cases, training, args.release, args.min_cases)
        report["file_sha256"] = hashlib.sha256(Path(args.cases).read_bytes()).hexdigest()
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
