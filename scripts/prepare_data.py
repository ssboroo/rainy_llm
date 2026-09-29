"""Normalize, deduplicate and split instruction data without model dependencies."""
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path


def norm(value):
    return unicodedata.normalize('NFC', value).strip()


def read_rows(path):
    rows = []
    with Path(path).open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'{path}:{number}: invalid JSON') from exc
                if not isinstance(row, dict):
                    raise ValueError(f'{path}:{number}: expected object')
                rows.append(row)
    return rows


def prepare(rows, seed='rainy-v1', heldout=()):
    # Group by source AND prompt using connected components.
    # Do this BEFORE removing duplicates, preserving every source connection.
    # This prevents identical prompts appearing in different splits even across sources.
    clean, ids = [], set()
    blocked = {norm(q) for q in heldout}
    for original in rows:
        row = dict(original)
        if "duplicate_provenance" in row:
            raise ValueError("prepare expects raw rows without duplicate_provenance")
        for key in ('id', 'instruction', 'output', 'source', 'license'):
            if not isinstance(row.get(key), str) or not norm(row[key]):
                raise ValueError(f'invalid field: {key}')
            row[key] = norm(row[key])
        if not isinstance(row.get('input', ''), str):
            raise ValueError('input must be a string')
        row['input'] = norm(row.get('input', ''))
        if row['id'] in ids:
            raise ValueError('duplicate ID: ' + row['id'])
        ids.add(row['id'])
        if row['instruction'] in blocked:
            raise ValueError('held-out prompt found: ' + row['id'])
        clean.append(row)
    if not clean:
        raise ValueError('dataset is empty')
    clean.sort(key=lambda r: r['id'])
    parent = list(range(len(clean)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    groups = {}
    for i, row in enumerate(clean):
        for key in [('source', row['source']), ('prompt', row['instruction'], row['input'])]:
            if key in groups:
                parent[root(i)] = root(groups[key])
            else:
                groups[key] = i
    components = {}
    for i, row in enumerate(clean):
        components.setdefault(root(i), []).append(row)
    counts = dict(train=0, validation=0, test=0)
    retained, duplicates = [], {}
    removed = 0
    for members in components.values():
        identity = json.dumps(sorted({r['source'] for r in members}), ensure_ascii=False)
        bucket = int(hashlib.sha256((seed + '\0' + identity).encode()).hexdigest(), 16) % 100
        split = 'train' if bucket < 80 else 'validation' if bucket < 90 else 'test'
        for row in members:
            row['split'] = split
            signature = tuple(row[k] for k in ('instruction', 'input', 'output'))
            if signature in duplicates:
                canonical = duplicates[signature]
                if 'duplicate_provenance' not in canonical:
                    canonical['duplicate_provenance'] = [
                        {k: canonical[k] for k in ('id', 'source', 'license')}]
                canonical['duplicate_provenance'].append(
                    {k: row[k] for k in ('id', 'source', 'license')})
                removed += 1
            else:
                duplicates[signature] = row
                retained.append(row)
                counts[split] += 1
    retained.sort(key=lambda r: r['id'])
    return retained, dict(records=len(retained), removed_exact_duplicates=removed,
                       groups=len(components), splits=counts, seed=seed,
                       warnings=['Empty splits are possible; hash ratios are approximate.'] if 0 in counts.values() else [])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--output-dir', required=True)
    p.add_argument('--seed', default='rainy-v1')
    p.add_argument('--heldout', help='Evaluation JSONL containing prompt fields')
    args = p.parse_args()
    try:
        blocked = []
        if args.heldout:
            for row in read_rows(args.heldout):
                if not isinstance(row.get('prompt'), str):
                    raise ValueError('heldout row missing prompt')
                blocked.append(row['prompt'])
        rows, report = prepare(read_rows(args.input), args.seed, blocked)
        report['input_sha256'] = hashlib.sha256(Path(args.input).read_bytes()).hexdigest()
        target = Path(args.output_dir)
        target.mkdir(parents=True, exist_ok=False)
        for split in ('train', 'validation', 'test'):
            with (target / (split + '.jsonl')).open('w', encoding='utf-8') as out:
                for row in rows:
                    if row['split'] == split:
                        out.write(json.dumps(row, ensure_ascii=False) + '\n')
        (target / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except (OSError, ValueError, UnicodeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
