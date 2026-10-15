"""Collect a bounded, attributed Mongolian Wikipedia batch with global deduplication."""
import argparse
import hashlib
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from collections import Counter
from pathlib import Path

DEFAULT_TITLES = ['Монгол улс', 'Улаанбаатар', 'Монгол хэл', 'Монгол бичиг', 'Кирилл үсэг',
                  'Орхон гол', 'Сэлэнгэ мөрөн', 'Хөвсгөл нуур', 'Увс нуур', 'Говь',
                  'Алтайн нуруу', 'Хангайн нуруу', 'Хэнтийн нуруу', 'Наадам',
                  'Морин хуур', 'Хөөмий', 'Уртын дуу', 'Гэр', 'Айраг', 'Цагаан сар']


def request(params):
    url = 'https://mn.wikipedia.org/w/api.php?' + urllib.parse.urlencode(dict(format='json', **params))
    req = urllib.request.Request(url, headers={
        'User-Agent': 'RAINY-LLM/0.2 (https://github.com/ssboroo/rainy_llm)'})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.load(response)
    if 'error' in data:
        raise ValueError(str(data['error']))
    return data


def normalized(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())


def shingles(text):
    """Case-folded character 5-grams; lexical heuristic, not semantic review."""
    text = normalized(text).casefold()
    return Counter(text[i:i + 5] for i in range(max(0, len(text) - 4)))


def screening_reason(text, prior_shingles):
    if re.search(r'(?:Загвар|Template)\s*:|\{\{|\}\}', text, re.IGNORECASE):
        return 'quality-artifact'
    if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text):
        return 'contact-pattern'
    current = shingles(text)
    for previous in prior_shingles:
        union = current | previous
        if union and sum((current & previous).values()) / sum(union.values()) >= 0.80:
            return 'near-duplicate-text'
    return None


def read_rows(paths):
    rows = []
    for path in paths:
        with Path(path).open(encoding='utf-8') as stream:
            for number, line in enumerate(stream, 1):
                if line.strip():
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError(f'{path}:{number}: expected object')
                    rows.append(row)
    return rows


def fetch_pages(titles):
    pages = []
    for start in range(0, len(titles), 20):
        data = request(dict(action='query', titles='|'.join(titles[start:start + 20]), redirects=1,
                            prop='extracts|info|revisions', explaintext=1, exintro=1, exlimit=20,
                            rvprop='ids', inprop='url'))
        pages.extend(data['query']['pages'].values())
    return pages


def collect(titles, existing=(), limit=20):
    if not 1 <= limit <= 20:
        raise ValueError('batch limit must be 1..20')
    prior_sources = {r.get('source') for r in existing}
    prior_pageids = {str(r.get('id', '')).split('-')[1] for r in existing
                     if str(r.get('id', '')).startswith('mnwiki-')}
    prior_text = {normalized(r.get('text', '')) for r in existing if r.get('text')}
    prior_shingles = [shingles(t) for t in prior_text]
    rows, rejected = [], []
    seen_sources, seen_pageids, seen_text = set(), set(), set()
    pages = sorted(fetch_pages(titles), key=lambda p: p.get('title', ''))
    for page in pages:
        title = page.get('title', '')
        text = page.get('extract', '').strip()
        source, pageid = page.get('fullurl'), str(page.get('pageid', ''))
        if page.get('missing') is not None:
            reason = 'missing'
        elif len(text) < 100:
            reason = 'short'
        elif not source or not pageid or not page.get('revisions'):
            reason = 'incomplete-provenance'
        elif source in prior_sources or source in seen_sources or pageid in prior_pageids or pageid in seen_pageids:
            reason = 'duplicate-source'
        elif normalized(text) in prior_text or normalized(text) in seen_text:
            reason = 'duplicate-text'
        elif (screen_reason := screening_reason(text, prior_shingles)):
            reason = screen_reason
        elif len(rows) >= limit:
            reason = 'batch-limit'
        else:
            reason = None
        if reason:
            rejected.append({'title': title, 'reason': reason})
            continue
        revision = page['revisions'][0]['revid']
        rows.append(dict(id=f'mnwiki-{pageid}-{revision}', title=title, text=text, source=source,
            revision=revision, revision_url=f'https://mn.wikipedia.org/w/index.php?oldid={revision}',
            attribution='Mongolian Wikipedia contributors', history_url=source + '?action=history',
            license='CC-BY-SA-4.0', license_url='https://creativecommons.org/licenses/by-sa/4.0/',
            modifications='API plain-text lead extraction; surrounding whitespace trimmed.',
            review_status='unreviewed-real-source-text',
            text_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest()))
        seen_sources.add(source); seen_pageids.add(pageid); seen_text.add(normalized(text))
        prior_shingles.append(shingles(text))
    return rows, rejected


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', required=True, type=Path)
    p.add_argument('--titles-file', type=Path)
    p.add_argument('--existing', action='append', default=[], type=Path)
    p.add_argument('--limit', type=int, default=20)
    args = p.parse_args()
    if args.output_dir.exists():
        p.exit(1, 'output exists\n')
    try:
        titles = DEFAULT_TITLES if not args.titles_file else [x.strip() for x in
            args.titles_file.read_text(encoding='utf-8').splitlines() if x.strip()]
        if len(titles) != len(set(titles)):
            raise ValueError('duplicate requested title')
        rows, rejected = collect(titles, read_rows(args.existing), args.limit)
        if len(rows) != args.limit:
            raise ValueError(f'batch incomplete: collected {len(rows)} of {args.limit}; no output written')
        payload = ''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows)
        reasons = {}
        for item in rejected:
            reasons[item['reason']] = reasons.get(item['reason'], 0) + 1
        report = dict(schema=1, retrieved_at=datetime.now(timezone.utc).isoformat(),
            requested_titles=len(titles), articles=len(rows), characters=sum(len(r['text']) for r in rows),
            rejected=len(rejected), rejected_by_reason=reasons, rejected_items=rejected,
            existing_corpora=[str(x) for x in args.existing], sha256=hashlib.sha256(payload.encode()).hexdigest(),
            source_api='https://mn.wikipedia.org/w/api.php',
            source_terms='https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use',
            license='CC-BY-SA-4.0', human_reviewed=0, privacy_reviewed=0,
            quality_reviewed=0, near_duplicate_reviewed=0, training_ready=0,
            automated_screening={'version': 1, 'quality': 'template markers',
                'privacy': 'email pattern only; not comprehensive PII detection',
                'near_duplicate': 'casefolded NFC whitespace-normalized character 5-gram multiset Jaccard >= 0.80'},
            purpose='unreviewed real-text batch; not instruction data')
        args.output_dir.mkdir(parents=True)
        (args.output_dir / 'corpus.jsonl').write_text(payload, encoding='utf-8')
        (args.output_dir / 'manifest.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False))
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
