"""Local UTF-8 document search with exact source lines; no model or network."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import unicodedata


def search_documents(root, query, limit=5):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("documents must be a directory")
    if not isinstance(query, str) or not query.strip() or len(query) > 1000:
        raise ValueError("query must contain 1-1000 characters")
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    tokens = list(dict.fromkeys(re.findall(r"[^\W_]+", unicodedata.normalize("NFC", query).casefold())))
    if not tokens or len(tokens) > 32:
        raise ValueError("query must contain 1-32 distinct words")
    # Quote every token: user text never becomes FTS operators or SQL syntax.
    match = " OR ".join('"' + token + '"' for token in tokens)
    db = sqlite3.connect(":memory:")
    files = []
    total_bytes = 0
    chunks = 0
    try:
        db.execute("CREATE VIRTUAL TABLE passages USING fts5(body, path UNINDEXED, first UNINDEXED, last UNINDEXED, digest UNINDEXED, tokenize='unicode61 remove_diacritics 0')")
        for directory, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.') and not (Path(directory) / d).is_symlink())
            for name in sorted(names):
                path = Path(directory) / name
                if name.startswith('.') or path.suffix.lower() not in {'.md', '.txt'} or path.is_symlink():
                    continue
                if not path.is_file() or not path.resolve().is_relative_to(root):
                    continue
                if len(files) >= 200:
                    raise ValueError("document limit exceeded (200 files)")
                with path.open('rb') as stream:
                    raw = stream.read(1024 * 1024 + 1)
                total_bytes += len(raw)
                if len(raw) > 1024 * 1024 or total_bytes > 10 * 1024 * 1024:
                    raise ValueError("document size limit exceeded (1 MiB/file, 10 MiB total)")
                text = raw.decode('utf-8-sig')
                if '\x00' in text:
                    raise ValueError("binary content in text document")
                digest = hashlib.sha256(raw).hexdigest()
                relative = path.relative_to(root).as_posix()
                files.append({'path': relative, 'sha256': digest})
                lines = text.splitlines()
                for offset in range(0, len(lines), 12):
                    body = '\n'.join(lines[offset:offset + 12])
                    if not body.strip():
                        continue
                    chunks += 1
                    if chunks > 20000:
                        raise ValueError("passage limit exceeded (20000)")
                    db.execute("INSERT INTO passages VALUES (?, ?, ?, ?, ?)",
                               (body, relative, offset + 1, min(offset + 12, len(lines)), digest))
        rows = db.execute("SELECT path, first, last, digest, body FROM passages WHERE passages MATCH ? ORDER BY bm25(passages), path, CAST(first AS INTEGER) LIMIT ?", (match, limit)).fetchall()
        return {'schema_version': 1, 'method': 'sqlite-fts5-bm25-lexical',
                'files_indexed': len(files), 'passages_indexed': chunks,
                'snapshot': sorted(files, key=lambda item: item['path']),
                'results': [{'path': p, 'line_start': int(a), 'line_end': int(b),
                             'sha256': h, 'excerpt': body} for p, a, b, h, body in rows],
                'note': 'Source excerpts, not generated answers. Lexical matches do not establish answerability. Snapshot rebuilt on each request.'}
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--documents', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('--limit', type=int, default=5)
    args = parser.parse_args()
    try:
        report = search_documents(args.documents, args.query, args.limit)
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.exit(1, f'Search failed: {exc}\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
