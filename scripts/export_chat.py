"""Export one validated split to generic chat JSONL; does not tokenize or train."""
import argparse
import hashlib
import json
from pathlib import Path
try:
    from .prepare_data import read_rows
    from .validate_data import validate
except ImportError:
    from prepare_data import read_rows
    from validate_data import validate


def convert(rows, split, system=''):
    if split not in ('train', 'validation', 'test'):
        raise ValueError('invalid split')
    result = []
    for row in rows:
        if row['split'] != split:
            continue
        messages = []
        if system:
            messages.append(dict(role='system', content=system))
        prompt = row['instruction']
        if row.get('input'):
            prompt += '\n\n' + row['input']
        messages += [dict(role='user', content=prompt), dict(role='assistant', content=row['output'])]
        result.append(dict(id=row['id'], source=row['source'], license=row['license'], split=split, messages=messages))
    if not result:
        raise ValueError('selected split contains no records')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input')
    p.add_argument('--output-dir', required=True)
    p.add_argument('--split', required=True, choices=['train', 'validation', 'test'])
    p.add_argument('--system', default='')
    args = p.parse_args()
    try:
        count, errors = validate(args.input)
        if errors:
            raise ValueError('validation failed: ' + '; '.join(errors))
        rows = convert(read_rows(args.input), args.split, args.system)
        target = Path(args.output_dir)
        target.mkdir(parents=True, exist_ok=False)
        payload = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
        (target / 'messages.jsonl').write_text(payload, encoding='utf-8')
        manifest = dict(records=len(rows), split=args.split, input_records=count,
                        input_sha256=hashlib.sha256(Path(args.input).read_bytes()).hexdigest(),
                        output_sha256=hashlib.sha256(payload.encode()).hexdigest(),
                        format='generic-messages-v1', tokenized=False, system_prompt=args.system)
        (target / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(f'exported={len(rows)}; split={args.split}')
    except (ValueError, OSError, UnicodeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
