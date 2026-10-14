import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.review_corpus import sha, fingerprint, load_corpus, make_packet, render_html, apply_packet, CHECKS


class CorpusReviewTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(id='doc-1', title='Монгол эх', text='Туршилтын өгүүлбэр.',
            source='https://example.org/article', revision_url='https://example.org/rev/1',
            history_url='https://example.org/history', attribution='Fixture author',
            license='fixture-license', license_url='https://example.org/license',
            modifications='test fixture only', review_status='unreviewed-real-source-text')
        self.row['text_sha256'] = sha(self.row['text'].encode())
        self.rows = [self.row]
        self.packet = make_packet(self.rows, 'a'*64)

    def reviewed_packet(self):
        p = copy.deepcopy(self.packet)
        p.update(reviewer='synthetic-test-fixture', reviewer_role='human-reviewer', reviewed_at='2026-10-14')
        p['documents'][0].update(decision='accept', checks={k: True for k in CHECKS}, notes='Test evidence only.')
        return p

    def test_export_never_approves(self):
        r = self.packet['documents'][0]
        self.assertEqual(r['decision'], 'pending')
        self.assertTrue(all(v is False for v in r['checks'].values()))
        self.assertEqual(self.packet['reviewer'], '')
        self.assertNotIn('text', r)

    def test_html_escapes_text_and_unsafe_urls(self):
        row = dict(self.row, title='<script>alert(1)</script>', text='<img src=x onerror=alert(1)>',
                   source='javascript:alert(1)')
        page = render_html([row], make_packet([row], 'a'*64))
        self.assertNotIn('<script>', page)
        self.assertNotIn('<img', page)
        self.assertNotIn('href="javascript:', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('Content-Security-Policy', page)
        self.assertIn('Fixture author', page)
        self.assertIn('https://example.org/license', page)

    def test_accept_preserves_provenance_reject_excludes(self):
        p = self.reviewed_packet()
        accepted = apply_packet(self.rows, 'a'*64, p)
        for field in ('text', 'source', 'license', 'history_url', 'modifications', 'text_sha256'):
            self.assertEqual(accepted[0][field], self.row[field])
        self.assertEqual(self.row['review_status'], 'unreviewed-real-source-text')
        p['documents'][0]['decision'] = 'reject'
        self.assertEqual(apply_packet(self.rows, 'a'*64, p), [])

    def test_stale_and_incomplete_reviews_fail_closed(self):
        good = self.reviewed_packet()
        mutations = [lambda p: p.update(corpus_sha256='b'*64),
                     lambda p: p.update(reviewer_role='ai-reviewer'),
                     lambda p: p.update(reviewed_at='not-a-date'),
                     lambda p: p['documents'][0].update(decision='pending'),
                     lambda p: p['documents'][0].update(record_sha256='b'*64),
                     lambda p: p['documents'][0].update(notes=''),
                     lambda p: p['documents'][0]['checks'].update(rights_checked=1),
                     lambda p: p['documents'][0].update(id='unknown'),
                     lambda p: p['documents'].append(p['documents'][0])]
        for mutate in mutations:
            p = copy.deepcopy(good)
            mutate(p)
            with self.assertRaises(ValueError):
                apply_packet(self.rows, 'a'*64, p)
        changed = [dict(self.row, license='changed')]
        with self.assertRaisesRegex(ValueError, 'stale'):
            apply_packet(changed, 'a'*64, good)

    def test_invalid_hash_duplicate_and_empty_corpus(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'corpus.jsonl'
            for rows in [[], [self.row, self.row], [dict(self.row, text='changed')]]:
                path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
                with self.assertRaises(ValueError):
                    load_corpus(path)

    def test_real_pilot_cli_and_no_overwrite(self):
        repo = Path(__file__).resolve().parents[1]
        corpus = repo/'data/mnwiki_pilot/corpus.jsonl'
        rows, h = load_corpus(corpus)
        self.assertEqual(len(rows), 20)
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/'review'
            cmd = [sys.executable, str(repo/'scripts/review_corpus.py'), 'export', str(corpus), '--output-dir', str(target)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((target/'review.pending.json').read_text())
            self.assertEqual(packet['corpus_sha256'], h)
            page = (target/'review.html').read_text()
            self.assertEqual(page.count('<article>'), 20)
            for row in rows:
                self.assertIn(row['id'], page)
            before = (target/'review.pending.json').read_bytes()
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(before, (target/'review.pending.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
