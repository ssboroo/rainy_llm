"""Heuristic data audit; reports positions rather than private text."""
import argparse
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
try:
    from .prepare_data import read_rows, norm
except ImportError:
    from prepare_data import read_rows, norm

PATTERNS = {
    'possible_email': re.compile(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b'),
    'possible_phone': re.compile(r'(?<!\d)(?:\+976[ -]?)?\d{8}(?!\d)'),
    'possible_secret': re.compile(r'(?:api[_-]?key|password|token)\s*[:=]\s*\S+', re.I),
}


def audit(rows, threshold=.9, max_rows=1000):
    if not 0 < threshold <= 1:
        raise ValueError('threshold must be in (0, 1]')
    if not rows or len(rows) > max_rows:
        raise ValueError(f'require 1..{max_rows} rows; audit runs pairwise comparisons')
    findings, texts = [], []
    sources, licenses, splits = Counter(), Counter(), Counter()
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f'row {index}: expected object')
        for field in ('instruction', 'output', 'source', 'license', 'split'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'row {index}: invalid {field}')
        if not isinstance(row.get('input', ''), str):
            raise ValueError(f'row {index}: invalid input')
        if row['split'] not in ('train', 'validation', 'test'):
            raise ValueError(f'row {index}: invalid split')
        text = '\n'.join(row.get(k, '') for k in ('instruction', 'input', 'output'))
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(dict(row=index, kind=name))
        letters = [c for c in text if c.isalpha()]
        cyrillic = sum('\u0400' <= c <= '\u052f' for c in letters)
        if letters and cyrillic / len(letters) < .3:
            findings.append(dict(row=index, kind='low_cyrillic_ratio'))
        # Counts only: source/license strings might themselves contain private data.
        sources[row['source']] += 1
        licenses[row['license']] += 1
        splits[row['split']] += 1
        texts.append(' '.join(norm(row['instruction'] + '\n' + row.get('input', '')).casefold().split()))
    for i, left in enumerate(texts):
        for j in range(i + 1, len(texts)):
            similarity = SequenceMatcher(None, left, texts[j], autojunk=False).ratio()
            if similarity >= threshold:
                findings.append(dict(row=i+1, other_row=j+1, kind='similar_prompt',
                                     similarity=round(similarity, 4),
                                     cross_split=rows[i]['split'] != rows[j]['split']))
    return dict(records=len(rows), source_count=len(sources), license_label_count=len(licenses),
                splits=dict(splits), findings=findings, threshold=threshold,
                warning='Heuristics only; no legal, privacy, semantic or language-quality certification.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--output', required=True)
    p.add_argument('--threshold', type=float, default=.9)
    args = p.parse_args()
    try:
        report = audit(read_rows(args.input), args.threshold)
        with Path(args.output).open('x', encoding='utf-8') as out:
            json.dump(report, out, ensure_ascii=False, indent=2)
            out.write('\n')
        print(f"records={report['records']}; findings={len(report['findings'])}")
    except (ValueError, OSError, UnicodeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
