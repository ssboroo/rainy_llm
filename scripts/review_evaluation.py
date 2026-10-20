"""Export a human-review packet and safely apply completed review evidence."""
import argparse
import copy
import datetime
import json
from pathlib import Path

try:
    from validate_evaluation import (
        REVIEW_CHECKS, REVIEWER_ROLES, case_fingerprint, read_jsonl, validate_cases,
    )
except ModuleNotFoundError:  # imported as scripts.review_evaluation in tests
    from scripts.validate_evaluation import (
        REVIEW_CHECKS, REVIEWER_ROLES, case_fingerprint, read_jsonl, validate_cases,
    )


def export_packet(cases):
    errors, _ = validate_cases(cases)
    if errors:
        raise ValueError("invalid cases: " + "; ".join(errors))
    return [
        {
            "id": row["id"],
            "case_sha256": case_fingerprint(row),
            "category": row["category"],
            "prompt": row["prompt"],
            "proposed_answers": row["answers"],
            "source": row["source"],
            "checks": {key: False for key in sorted(REVIEW_CHECKS)},
            "decision": "pending",
            "notes": "",
        }
        for row in cases
    ]


def apply_reviews(cases, reviews, reviewed_at, reviewer_role):
    if reviewer_role not in REVIEWER_ROLES:
        raise ValueError("invalid reviewer role")
    try:
        datetime.date.fromisoformat(reviewed_at)
    except (TypeError, ValueError) as exc:
        raise ValueError("reviewed_at must be an ISO date") from exc
    errors, _ = validate_cases(cases)
    if errors:
        raise ValueError("invalid cases: " + "; ".join(errors))
    by_id = {}
    for index, review in enumerate(reviews):
        if not isinstance(review, dict) or not isinstance(review.get("id"), str):
            raise ValueError(f"review[{index}] must have a string id")
        if review["id"] in by_id:
            raise ValueError(f"duplicate review id: {review['id']}")
        by_id[review["id"]] = review
    case_ids = {row["id"] for row in cases}
    if set(by_id) != case_ids:
        missing = sorted(case_ids - set(by_id))
        unknown = sorted(set(by_id) - case_ids)
        raise ValueError(f"review ids must exactly match cases; missing={missing}, unknown={unknown}")
    output = []
    for row in cases:
        review = by_id[row["id"]]
        if review.get("case_sha256") != case_fingerprint(row):
            raise ValueError(f"stale or mismatched review: {row['id']}")
        checks = review.get("checks")
        if not isinstance(checks, dict) or set(checks) != REVIEW_CHECKS or not all(
                checks.get(key) is True for key in REVIEW_CHECKS):
            raise ValueError(f"incomplete checks: {row['id']}")
        if review.get("decision") != "accept":
            raise ValueError(f"review is not accepted: {row['id']}")
        updated = copy.deepcopy(row)
        updated["review_status"] = "human-reviewed"
        updated["review_evidence"] = {
            "case_sha256": case_fingerprint(row),
            "reviewed_at": reviewed_at,
            "reviewer_role": reviewer_role,
            "decision": "accept",
            "checks": {key: True for key in sorted(REVIEW_CHECKS)},
        }
        output.append(updated)
    final_errors, _ = validate_cases(output)
    if final_errors:
        raise ValueError("reviewed output is invalid: " + "; ".join(final_errors))
    return output


def write_jsonl(path, rows):
    target = Path(path)
    with target.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    export = subparsers.add_parser("export", help="Create an uncompleted review packet")
    export.add_argument("--cases", default="evaluation/mn_smoke.jsonl")
    export.add_argument("--output", required=True)
    apply = subparsers.add_parser("apply", help="Apply a completed review packet")
    apply.add_argument("--cases", default="evaluation/mn_smoke.jsonl")
    apply.add_argument("--reviews", required=True)
    apply.add_argument("--output", required=True)
    apply.add_argument("--reviewed-at", required=True)
    apply.add_argument("--reviewer-role", choices=sorted(REVIEWER_ROLES), required=True)
    args = parser.parse_args()
    try:
        cases = read_jsonl(args.cases)
        if args.command == "export":
            rows = export_packet(cases)
        else:
            rows = apply_reviews(cases, read_jsonl(args.reviews),
                                 args.reviewed_at, args.reviewer_role)
        write_jsonl(args.output, rows)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"OK: {len(rows)} rows -> {args.output}")


if __name__ == "__main__":
    main()
