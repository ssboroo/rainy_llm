"""Validate the project's UTF-8 instruction JSONL format; no training occurs."""
import argparse
import json
import unicodedata
from pathlib import Path


def validate(path):
    errors, seen, count = [], set(), 0
    with Path(path).open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            count += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"line {line_no}: invalid JSON")
                continue
            if not isinstance(row, dict):
                errors.append(f"line {line_no}: expected an object")
                continue
            required = ("id", "instruction", "output", "source", "license", "split")
            bad = [key for key in required if not isinstance(row.get(key), str) or not row[key].strip()]
            if bad:
                errors.append(f"line {line_no}: missing/empty fields: {', '.join(bad)}")
                continue
            if row["split"] not in ("train", "validation", "test"):
                errors.append(f"line {line_no}: invalid split")
            if not isinstance(row.get("input", ""), str):
                errors.append(f"line {line_no}: input must be a string")
                continue
            for kind, value in (
                ("id", row["id"]),
                ("content", (row["instruction"], row.get("input", ""), row["output"])),
            ):
                if kind == "content":
                    value = tuple(unicodedata.normalize("NFC", item).strip() for item in value)
                key = (kind, value)
                if key in seen:
                    errors.append(f"line {line_no}: duplicate {kind}")
                seen.add(key)
    if not count:
        errors.append("dataset is empty")
    return count, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    args = parser.parse_args()
    try:
        count, errors = validate(args.path)
    except (OSError, UnicodeError) as exc:
        parser.exit(1, f"Cannot read dataset: {exc}\n")
    for error in errors:
        print(error)
    print(f"records={count}, errors={len(errors)}")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
