"""Export a human-review packet and safely apply completed review evidence."""
import argparse
import copy
import datetime
import json
from collections import Counter
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


def summarize_reviews(cases, reviews):
    """Report review progress without copying prompts or claiming human review."""
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
    unknown = sorted(set(by_id) - case_ids)
    statuses = Counter()
    categories = {}
    for row in cases:
        review = by_id.get(row["id"])
        if review is None:
            status = "missing"
        elif review.get("case_sha256") != case_fingerprint(row):
            status = "stale"
        elif review.get("decision") not in {"pending", "accept", "reject"}:
            status = "invalid"
        elif review["decision"] == "reject":
            status = "rejected"
        elif review["decision"] == "pending":
            status = "pending"
        else:
            checks = review.get("checks")
            if (isinstance(checks, dict) and set(checks) == REVIEW_CHECKS
                    and all(checks.get(key) is True for key in REVIEW_CHECKS)):
                status = "ready-accept"
            else:
                status = "incomplete"
        statuses[status] += 1
        bucket = categories.setdefault(row["category"], Counter())
        bucket["total"] += 1
        bucket[status] += 1

    ready = (statuses.get("ready-accept", 0) == len(cases) and not unknown
             and len(by_id) == len(cases))
    return {
        "schema_version": 1,
        "total_cases": len(cases),
        "review_rows": len(reviews),
        "statuses": dict(sorted(statuses.items())),
        "categories": {
            key: dict(sorted(value.items()))
            for key, value in sorted(categories.items())
        },
        "unknown_review_ids": unknown,
        "ready_to_apply": ready,
        "note": (
            "Progress report only. ready-accept means packet structure is complete; "
            "it does not verify reviewer identity or substitute for human review."
        ),
    }


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
    summary = subparsers.add_parser("summary", help="Report review progress without prompt text")
    summary.add_argument("--cases", default="evaluation/mn_smoke.jsonl")
    summary.add_argument("--reviews", required=True)
    summary.add_argument("--output")
    summary.add_argument("--fail-unready", action="store_true")
    args = parser.parse_args()
    try:
        cases = read_jsonl(args.cases)
        if args.command == "export":
            rows = export_packet(cases)
        elif args.command == "summary":
            report = summarize_reviews(cases, read_jsonl(args.reviews))
            encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                with Path(args.output).open("x", encoding="utf-8") as stream:
                    stream.write(encoded)
            print(encoded, end="")
            if args.fail_unready and not report["ready_to_apply"]:
                parser.exit(1)
            return
        else:
            rows = apply_reviews(cases, read_jsonl(args.reviews),
                                 args.reviewed_at, args.reviewer_role)
        write_jsonl(args.output, rows)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"OK: {len(rows)} rows -> {args.output}")


if __name__ == "__main__":
    main()
