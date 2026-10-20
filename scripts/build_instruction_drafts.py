"""Author extractive QA drafts while retaining frozen source splits; never approve training."""
import argparse
import json
from pathlib import Path

try:
    from .review_corpus import load_corpus, fingerprint, sha
    from .split_corpus import partition
except ImportError:
    from review_corpus import load_corpus, fingerprint, sha
    from split_corpus import partition


def check_manifest(rows, corpus_hash, manifest):
    if manifest.get('corpus_sha256') != corpus_hash:
        raise ValueError('stale corpus manifest')
    seed = manifest.get('seed')
    if not isinstance(seed, str):
        raise ValueError('missing split seed')
    _, expected = partition(rows, seed)
    for key in ('schema', 'algorithm', 'assignments', 'counts', 'group_count'):
        if manifest.get(key) != expected[key]:
            raise ValueError('split manifest mismatch: ' + key)
    return {a['id']: a['split'] for a in manifest['assignments']}


def template(rows):
    return [dict(id=r['id'] + '-qa-1', parent_id=r['id'],
                 parent_sha256=fingerprint(r), instruction='',
                 answer_start=None, answer_end=None) for r in sorted(rows, key=lambda r: r['id'])]


def build(rows, assignments, annotations):
    if not isinstance(annotations, list) or not 1 <= len(annotations) <= 1000:
        raise ValueError('annotations require 1..1000 records')
    parents = {r['id']: r for r in rows}
    result, seen = [], set()
    for a in annotations:
        if not isinstance(a, dict):
            raise ValueError('annotation must be an object')
        for key in ('id', 'parent_id', 'parent_sha256', 'instruction'):
            if not isinstance(a.get(key), str) or not a[key].strip():
                raise ValueError('incomplete annotation: ' + key)
        if a['id'] in seen:
            raise ValueError('duplicate instruction id')
        seen.add(a['id'])
        parent = parents.get(a['parent_id'])
        if parent is None or a['parent_sha256'] != fingerprint(parent):
            raise ValueError('unknown or changed parent document')
        start, end = a.get('answer_start'), a.get('answer_end')
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(parent['text']):
            raise ValueError('invalid Unicode character span')
        answer = parent['text'][start:end]
        if not answer.strip():
            raise ValueError('empty answer span')
        result.append(dict(id=a['id'], instruction=a['instruction'], input=parent['text'],
            output=answer, source=parent['source'], license=parent['license'],
            split=assignments[parent['id']], parent_id=parent['id'],
            parent_sha256=fingerprint(parent), provenance=dict(parent),
            answer_span=dict(start=start, end=end, unit='unicode-code-points'),
            review_status='draft-needs-human-review', training_ready=False))
    return sorted(result, key=lambda r: r['id'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['template', 'build'])
    p.add_argument('corpus', type=Path)
    p.add_argument('--splits', required=True, type=Path)
    p.add_argument('--annotations', type=Path)
    p.add_argument('--output-dir', required=True, type=Path)
    args = p.parse_args()
    try:
        rows, corpus_hash = load_corpus(args.corpus)
        split_bytes = args.splits.read_bytes()
        assignments = check_manifest(rows, corpus_hash, json.loads(split_bytes))
        if args.mode == 'template':
            if args.annotations:
                raise ValueError('template does not accept annotations')
            records, name = template(rows), 'annotations.pending.json'
            payload = json.dumps(records, ensure_ascii=False, indent=2) + '\n'
        else:
            if not args.annotations:
                raise ValueError('build requires annotations')
            records = build(rows, assignments, json.loads(args.annotations.read_text(encoding='utf-8')))
            name = 'instructions.draft.jsonl'
            payload = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in records)
        summary = dict(mode=args.mode, records=len(records), training_ready=False,
                       corpus_sha256=corpus_hash, split_manifest_sha256=sha(split_bytes),
                       output_sha256=sha(payload.encode('utf-8')))
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir / name).write_text(payload, encoding='utf-8')
        (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(summary))
    except (ValueError, OSError, UnicodeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
