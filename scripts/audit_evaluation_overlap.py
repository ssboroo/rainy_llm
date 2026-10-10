"""Find fuzzy evaluation/training prompt overlaps without copying prompt text."""
import argparse
import hashlib
import json
import math
from pathlib import Path

try:
    from validate_evaluation import normalized, read_jsonl
except ImportError:  # imported as scripts.audit_evaluation_overlap in tests
    from scripts.validate_evaluation import normalized, read_jsonl


def shingles(value, size):
    text = normalized(value)
    if not text:
        return set()
    if len(text) < size:
        return {text}
    return {text[index:index + size] for index in range(len(text) - size + 1)}


def jaccard(left, right):
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def training_prompt(row, label):
    if not isinstance(row, dict):
        raise ValueError(f"{label}: expected object")
    prompt = row.get("instruction", row.get("prompt"))
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError(f"{label}: missing instruction/prompt")
    extra = row.get("input", "")
    if not isinstance(extra, str):
        raise ValueError(f"{label}: input must be a string")
    return prompt + ("\n" + extra if extra.strip() else "")


def audit_overlap(cases, training_records, threshold=0.75, ngram=3,
                  max_pairs=1_000_000):
    if (not isinstance(threshold, (int, float)) or isinstance(threshold, bool)
            or not math.isfinite(threshold) or not 0 < threshold <= 1):
        raise ValueError("threshold must be finite and in (0, 1]")
    if type(ngram) is not int or not 1 <= ngram <= 8:
        raise ValueError("ngram must be an integer from 1 to 8")
    if type(max_pairs) is not int or max_pairs < 1:
        raise ValueError("max_pairs must be a positive integer")
    if not cases:
        raise ValueError("evaluation set is empty")
    if not training_records:
        raise ValueError("training set is empty")
    pairs = len(cases) * len(training_records)
    if pairs > max_pairs:
        raise ValueError(f"pair count {pairs} exceeds max_pairs {max_pairs}")

    prepared_cases = []
    seen_ids = set()
    for index, row in enumerate(cases, 1):
        if not isinstance(row, dict):
            raise ValueError(f"case[{index}]: expected object")
        case_id, prompt = row.get("id"), row.get("prompt")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in seen_ids:
            raise ValueError(f"case[{index}]: invalid/duplicate id")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"case[{index}]: invalid prompt")
        seen_ids.add(case_id)
        prepared_cases.append((case_id, shingles(prompt, ngram)))

    prepared_training = []
    for file_index, row_number, row in training_records:
        if type(file_index) is not int or file_index < 1:
            raise ValueError("training file index must be a positive integer")
        if type(row_number) is not int or row_number < 1:
            raise ValueError("training row number must be a positive integer")
        label = f"training[{file_index}:{row_number}]"
        prepared_training.append(
            (file_index, row_number, shingles(training_prompt(row, label), ngram)))

    findings = []
    for case_id, case_shingles in prepared_cases:
        for file_index, row_number, train_shingles in prepared_training:
            similarity = jaccard(case_shingles, train_shingles)
            if similarity >= threshold:
                findings.append({
                    "case_id": case_id,
                    "training_file_index": file_index,
                    "training_row": row_number,
                    "similarity": round(similarity, 6),
                })
    findings.sort(key=lambda item: (-item["similarity"], item["case_id"],
                                    item["training_file_index"], item["training_row"]))
    return {
        "method": "normalized_character_ngram_jaccard",
        "ngram": ngram,
        "threshold": threshold,
        "evaluation_cases": len(cases),
        "training_records": len(training_records),
        "pairs_checked": pairs,
        "candidate_count": len(findings),
        "findings": findings,
        "warning": (
            "Heuristic candidate list only; human review is required. This does not detect "
            "all paraphrases, translations, semantic overlap or base-model contamination."
        ),
    }


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="?", default="evaluation/mn_smoke.jsonl")
    parser.add_argument("--training", action="append", required=True,
                        help="Training JSONL; repeatable")
    parser.add_argument("--threshold", type=float, default=0.75)
    parser.add_argument("--ngram", type=int, default=3)
    parser.add_argument("--max-pairs", type=int, default=1_000_000)
    parser.add_argument("--output", help="Write a new JSON report; never overwrite")
    parser.add_argument("--fail-on-match", action="store_true")
    args = parser.parse_args()
    try:
        cases = read_jsonl(args.cases)
        records, files = [], []
        for file_index, path in enumerate(args.training, 1):
            rows = read_jsonl(path)
            files.append({"file_index": file_index, "records": len(rows),
                          "sha256": sha256(path)})
            records.extend((file_index, row_number, row)
                           for row_number, row in enumerate(rows, 1))
        report = audit_overlap(cases, records, args.threshold, args.ngram, args.max_pairs)
        report["cases_sha256"] = sha256(args.cases)
        report["training_files"] = files
        encoded = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        print(encoded, end="")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, str(exc) + "\n")
    if args.fail_on_match and report["findings"]:
        parser.exit(1)


if __name__ == "__main__":
    main()
