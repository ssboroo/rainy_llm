"""Offline exact-match scoring. Missing answers count as incorrect."""
import argparse
import json
import unicodedata
from pathlib import Path
try:
    from .prepare_data import read_rows
except ImportError:
    from prepare_data import read_rows


def normalized(value):
    return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


def score(cases, predictions):
    expected, responses = {}, {}
    for case in cases:
        if not isinstance(case.get('id'), str) or not case['id'].strip() or case['id'] in expected:
            raise ValueError('invalid/duplicate case ID')
        if not isinstance(case.get('prompt'), str) or not case['prompt'].strip():
            raise ValueError('invalid prompt')
        if not isinstance(case.get('category'), str) or not case['category'].strip():
            raise ValueError('invalid category')
        if not isinstance(case.get('answers'), list) or not case['answers'] or not all(isinstance(a, str) and a.strip() for a in case['answers']):
            raise ValueError('invalid accepted answers')
        expected[case['id']] = case
    if not expected:
        raise ValueError('empty evaluation')
    for row in predictions:
        key = row.get('id')
        if not isinstance(key, str) or key not in expected or key in responses or not isinstance(row.get('output'), str):
            raise ValueError('invalid/duplicate/unknown prediction')
        responses[key] = row['output']
    details, categories = [], {}
    for key, case in expected.items():
        correct = key in responses and normalized(responses[key]) in {normalized(a) for a in case['answers']}
        bucket = categories.setdefault(case['category'], dict(correct=0, total=0))
        bucket['total'] += 1
        bucket['correct'] += int(correct)
        details.append(dict(id=key, correct=correct, missing=key not in responses))
    correct = sum(d['correct'] for d in details)
    return dict(metric='normalized_exact_match', correct=correct, total=len(expected),
                accuracy=correct / len(expected), missing=len(expected)-len(responses),
                categories=categories, details=details)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', required=True)
    p.add_argument('--predictions', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        result = score(read_rows(args.cases), read_rows(args.predictions))
        # Exclusive create protects existing experiment reports.
        with Path(args.output).open('x', encoding='utf-8') as out:
            json.dump(result, out, ensure_ascii=False, indent=2)
            out.write('\n')
        print(f"accuracy={result['accuracy']:.3f}; missing={result['missing']}")
    except (ValueError, OSError, UnicodeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
