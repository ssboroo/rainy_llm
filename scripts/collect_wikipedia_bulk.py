"""Bounded Wikipedia lead collection with resumable SQLite indexing; no training approval."""
import argparse
import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from collect_wikipedia import request, fetch_pages, normalized, screening_reason

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('data/mnwiki_bulk'))
    p.add_argument('--limit', type=int, default=250)
    p.add_argument('--max-requests', type=int, default=100)
    a = p.parse_args()
    if not 1 <= a.limit <= 5000 or not 1 <= a.max_requests <= 500:
        p.error('limit 1..5000; max-requests 1..500')
    a.root.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE docs (page TEXT PRIMARY KEY, hash TEXT UNIQUE)')
    existing = list(Path('data').glob('mnwiki_pilot/corpus.jsonl'))
    existing += list(Path('data').glob('mnwiki_daily/*/batch-*/corpus.jsonl'))
    existing += list(a.root.glob('batch-*.jsonl'))
    for path in existing:
        for line in path.read_text(encoding='utf-8').splitlines():
            r = json.loads(line)
            page = r['id'].split('-')[1]
            h = hashlib.sha256(normalized(r['text']).casefold().encode()).hexdigest()
            db.execute('INSERT OR IGNORE INTO docs VALUES (?, ?)', (page, h))
    state_path = a.root / 'state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {'cursor': None, 'exhausted': False}
    if state.get('exhausted'):
        print('Discovery exhausted; no restart or duplicate collection.')
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = a.root / ('batch-' + stamp + '.jsonl')
    accepted, examined, calls = 0, 0, 0
    rejected = {}
    with output.open('x', encoding='utf-8') as stream:
        while accepted < a.limit and calls + 4 <= a.max_requests:
            params = dict(action='query', list='allpages', apnamespace=0, apfilterredir='nonredirects', aplimit=40)
            if state.get('cursor'):
                params['apcontinue'] = state['cursor']
            response = request(params)
            calls += 1
            titles = [v['title'] for v in response['query']['allpages']]
            pages = fetch_pages(titles)
            calls += (len(titles) + 19) // 20
            # Process the entire discovery page before advancing the cursor.
            # The target is soft by at most 39 records, preventing dropped titles.
            for page in pages:
                examined += 1
                text = page.get('extract', '').strip()
                pid = str(page.get('pageid', ''))
                h = hashlib.sha256(normalized(text).casefold().encode()).hexdigest()
                reason = None
                if page.get('missing') is not None or not page.get('fullurl') or not page.get('revisions'):
                    reason = 'incomplete-source'
                elif len(text) < 200:
                    reason = 'short'
                elif len(text) > 50000:
                    reason = 'oversize'
                elif sum('\u0400' <= c <= '\u04ff' for c in text) / max(1, sum(c.isalpha() for c in text)) < .65:
                    reason = 'low-cyrillic'
                elif db.execute('SELECT 1 FROM docs WHERE page=? OR hash=?', (pid,h)).fetchone():
                    reason = 'exact-duplicate'
                else:
                    reason = screening_reason(text, [])
                if reason:
                    rejected[reason] = rejected.get(reason, 0) + 1
                    continue
                rev = page['revisions'][0]['revid']
                source = page['fullurl']
                row = dict(id=f'mnwiki-{pid}-{rev}', title=page['title'], text=text,
                    source=source, revision=rev,
                    revision_url=f'https://mn.wikipedia.org/w/index.php?oldid={rev}',
                    history_url=source+'?action=history', attribution='Mongolian Wikipedia contributors',
                    license='CC-BY-SA-4.0', license_url='https://creativecommons.org/licenses/by-sa/4.0/',
                    modifications='API plain-text lead extraction; surrounding whitespace trimmed.',
                    text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                    retrieved_at=datetime.now(timezone.utc).isoformat(),
                    review_status='unreviewed-real-source-text', training_ready=False)
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True)+'\n')
                db.execute('INSERT INTO docs VALUES (?,?)', (pid,h))
                accepted += 1
            stream.flush()
            state = dict(cursor=response.get('continue', {}).get('apcontinue'),
                         exhausted='continue' not in response)
            # State is published only after complete pages; workflow commits data and state together.
            temp = state_path.with_suffix('.tmp')
            temp.write_text(json.dumps(state, indent=2)+'\n')
            temp.replace(state_path)
            if state['exhausted']:
                break
            time.sleep(1)
    report = dict(accepted=accepted, examined=examined, api_requests=calls, rejected=rejected,
        total_unique_indexed=db.execute('SELECT count(*) FROM docs').fetchone()[0],
        corpus_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        human_reviewed=0, training_ready=0, source_api='https://mn.wikipedia.org/w/api.php',
        scope='Wikipedia introductions only; no semantic deduplication, comprehensive PII or factual review',
        state=state)
    output.with_suffix('.manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))
if __name__ == '__main__':
    main()
