"""Partition raw documents without separating source or normalized-text groups."""
import argparse
import json
from pathlib import Path
import unicodedata

try:
    from .review_corpus import load_corpus, sha, fingerprint
except ImportError:
    from review_corpus import load_corpus, sha, fingerprint


def normalized(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def partition(rows, seed='rainy-corpus-v1'):
    rows = sorted(rows, key=lambda r: r['id'])
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('nonempty corpus with unique IDs required')
    parent = list(range(len(rows)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen = {}
    for i, row in enumerate(rows):
        for key in (('source', unicodedata.normalize('NFC', row['source']).strip()),
                    ('text', normalized(row['text']))):
            if key in seen:
                parent[root(i)] = root(seen[key])
            else:
                seen[key] = i
    groups = {}
    for i, row in enumerate(rows):
        groups.setdefault(root(i), []).append(row)
    outputs = {k: [] for k in ('train', 'validation', 'test')}
    assignments = []
    for group in groups.values():
        sources = sorted({unicodedata.normalize('NFC', r['source']).strip() for r in group})
        identity = json.dumps(sources, ensure_ascii=False, separators=(',', ':'))
        group_hash = sha(identity.encode())
        bucket = int(sha((seed + '\0' + identity).encode()), 16) % 100
        split = 'train' if bucket < 80 else 'validation' if bucket < 90 else 'test'
        outputs[split].extend(group)
        assignments.extend(dict(id=r['id'], split=split, group_sha256=group_hash,
                                record_sha256=fingerprint(r)) for r in group)
    for values in outputs.values():
        values.sort(key=lambda r: r['id'])
    manifest = dict(schema=1, algorithm='source-text-components-sha256-v1', seed=seed,
        group_count=len(groups), counts={k: len(v) for k, v in outputs.items()},
        training_ready=False, assignments=sorted(assignments, key=lambda r: r['id']),
        warnings=['Raw documents only; human review and instruction conversion still required.',
                  '80/10/10 hash buckets are approximate, not balanced quotas.',
                  'URL aliases, semantic duplicates and pretraining contamination are not detected.'])
    manifest['empty_splits'] = [k for k, v in outputs.items() if not v]
    return outputs, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('corpus', type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--seed', default='rainy-corpus-v1')
    args = parser.parse_args()
    rows, corpus_hash = load_corpus(args.corpus)
    outputs, manifest = partition(rows, args.seed)
    manifest['corpus_sha256'] = corpus_hash
    payloads = {k: ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n'
                         for r in values).encode('utf-8') for k, values in outputs.items()}
    manifest['output_sha256'] = {k: sha(v) for k, v in payloads.items()}
    args.output_dir.mkdir(parents=True, exist_ok=False)
    for split, payload in payloads.items():
        (args.output_dir / (split + '.jsonl')).write_bytes(payload)
    (args.output_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest['counts']))


if __name__ == '__main__':
    main()
