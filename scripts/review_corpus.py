"""Build an offline corpus review pack and export only explicitly accepted documents."""
import argparse
import datetime
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

CHECKS = ('mongolian_quality', 'facts_checked', 'privacy_checked', 'rights_checked')
FIELDS = ('id', 'title', 'text', 'source', 'revision_url', 'history_url',
          'attribution', 'license', 'license_url', 'modifications', 'text_sha256')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(row):
    return sha(json.dumps(row, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode())


def load_corpus(path):
    raw = Path(path).read_bytes()
    if len(raw) > 10 * 1024 * 1024:
        raise ValueError('review batches are limited to 10 MiB')
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    if not 1 <= len(rows) <= 200:
        raise ValueError('review batches require 1..200 documents')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS):
            raise ValueError('missing corpus text/provenance fields')
        if row['id'] in seen:
            raise ValueError('duplicate corpus id')
        seen.add(row['id'])
        if row['text_sha256'] != sha(row['text'].encode('utf-8')):
            raise ValueError('corpus text hash mismatch')
    return rows, sha(raw)


def make_packet(rows, corpus_sha256):
    return dict(schema=1, corpus_sha256=corpus_sha256, reviewer='', reviewer_role='',
                reviewed_at='', documents=[dict(id=r['id'], record_sha256=fingerprint(r),
                decision='pending', checks={k: False for k in CHECKS}, notes='') for r in rows])


def render_html(rows, packet):
    def esc(value):
        return html.escape(str(value), quote=True)

    def link(value):
        parsed = urlsplit(value)
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            return esc(value)
        return f'<a rel="noreferrer noopener" href="{esc(value)}">{esc(value)}</a>'

    parts = ['<!doctype html><html lang="mn"><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">',
             '<title>RAINY — Монгол корпусын хүний хяналт</title>',
             '<style>body{max-width:960px;margin:2rem auto;padding:0 1rem;font:17px/1.6 system-ui}article{border-top:2px solid #abc;margin-top:2rem;padding-top:1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}dd{overflow-wrap:anywhere}code{overflow-wrap:anywhere}a{color:#145aa3}</style>',
             '<h1>Монгол корпусын хүний хяналт / Corpus review</h1>',
             '<p>Бүгд pending. Энэ нь сургалтын зөвшөөрөл биш. Read the text and provenance, then edit review.pending.json. '
             'Use accept or reject, record your reviewer reference/date and checklist evidence. '
             'Do not mark AI review as human review. No decisions are saved by this read-only page.</p>',
             '<p>Эх бичвэр, ишлэл, лиценз нь эх сурвалжийн нөхцөлтэй хэвээр. '
             'Article text retains its listed upstream license; project ownership does not replace it. '
             'No remote resources/scripts are loaded; source links open only when clicked.</p>',
             f'<p>Documents: {len(rows)} · Corpus SHA-256: <code>{esc(packet["corpus_sha256"])}</code></p>']
    for i, row in enumerate(rows, 1):
        parts += [f'<article><h2>{i}. {esc(row["title"])}</h2>',
                  f'<p>ID: <code>{esc(row["id"])}</code></p><pre>{esc(row["text"])}</pre><dl>']
        for key in FIELDS:
            if key in ('text', 'title', 'id'):
                continue
            value = link(row[key]) if key in ('source', 'revision_url', 'history_url', 'license_url') else esc(row[key])
            parts.append(f'<dt>{esc(key)}</dt><dd>{value}</dd>')
        parts += ['</dl><p>Review: Mongolian wording · facts · privacy · usage rights. '
                  'Record corrections in notes; changed source text requires a new packet.</p></article>']
    return '\n'.join(parts) + '\n</html>\n'


def apply_packet(rows, corpus_sha256, packet):
    if not isinstance(packet, dict) or packet.get('schema') != 1 or packet.get('corpus_sha256') != corpus_sha256:
        raise ValueError('stale or invalid corpus packet')
    if (packet.get('reviewer_role') != 'human-reviewer' or not isinstance(packet.get('reviewer'), str)
            or not packet['reviewer'].strip()):
        raise ValueError('explicit human reviewer reference required')
    date = packet.get('reviewed_at')
    if not isinstance(date, str) or datetime.date.fromisoformat(date).isoformat() != date:
        raise ValueError('ISO review date required')
    reviews = packet.get('documents')
    if not isinstance(reviews, list) or len(reviews) != len(rows):
        raise ValueError('one review per document required')
    by_id = {}
    for review in reviews:
        if not isinstance(review, dict) or not isinstance(review.get('id'), str) or review['id'] in by_id:
            raise ValueError('invalid/duplicate review id')
        by_id[review['id']] = review
    if set(by_id) != {r['id'] for r in rows}:
        raise ValueError('unknown or missing document id')
    accepted = []
    for row in rows:
        review = by_id[row['id']]
        if review.get('record_sha256') != fingerprint(row):
            raise ValueError('stale document review')
        if review.get('decision') not in ('accept', 'reject'):
            raise ValueError('pending/invalid decision; complete every document review')
        if not isinstance(review.get('notes'), str) or not review['notes'].strip():
            raise ValueError('review evidence or rejection reason required in notes')
        if review['decision'] == 'accept':
            checks = review.get('checks')
            if not isinstance(checks, dict) or set(checks) != set(CHECKS) or not all(checks[k] is True for k in CHECKS):
                raise ValueError('all acceptance checks must be explicitly true')
            accepted.append(dict(row, review_status='human-reviewed', review_evidence=dict(
                review, reviewer=packet['reviewer'], reviewer_role=packet['reviewer_role'], reviewed_at=date)))
    return accepted


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('export', 'apply'))
    p.add_argument('corpus')
    p.add_argument('--output-dir', required=True)
    p.add_argument('--reviews')
    args = p.parse_args()
    try:
        rows, corpus_hash = load_corpus(args.corpus)
        if args.action == 'export':
            packet = make_packet(rows, corpus_hash)
            files = {'review.pending.json': json.dumps(packet, ensure_ascii=False, indent=2)+'\n',
                     'review.html': render_html(rows, packet)}
            report = dict(documents=len(rows), pending=len(rows), accepted=0, training_ready=False)
        else:
            if not args.reviews:
                raise ValueError('--reviews is required for apply')
            accepted = apply_packet(rows, corpus_hash, json.loads(Path(args.reviews).read_text(encoding='utf-8')))
            files = {'reviewed-corpus.jsonl': ''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in accepted)}
            report = dict(documents=len(rows), accepted=len(accepted), rejected=len(rows)-len(accepted),
                          training_ready=False, instruction_conversion_required=True)
        target = Path(args.output_dir)
        target.mkdir(parents=True, exist_ok=False)
        for name, content in files.items():
            (target / name).write_text(content, encoding='utf-8')
        (target / 'summary.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report))
    except (ValueError, OSError, UnicodeError) as exc:
        p.exit(1, str(exc)+'\n')


if __name__ == '__main__':
    main()
