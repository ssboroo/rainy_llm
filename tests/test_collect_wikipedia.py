import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.collect_wikipedia import collect, normalized


def page(pageid, title, text=None):
    text = text or (title + ' ') * 60
    return {'pageid': pageid, 'title': title, 'extract': text,
            'fullurl': f'https://mn.wikipedia.org/wiki/{title}', 'revisions': [{'revid': pageid + 100}]}


class WikipediaBatchTests(unittest.TestCase):
    def test_suspect_template_and_contact_are_quarantined(self):
        pages = [page(1, 'А', 'Загвар:Инфобокс\n' + 'Монгол эх. ' * 30),
                 page(2, 'Б', 'Холбоо test@example.org ' + 'Эх бичвэр. ' * 30)]
        with patch('scripts.collect_wikipedia.fetch_pages', return_value=pages):
            rows, rejected = collect(['А', 'Б'], [], 2)
        self.assertEqual(rows, [])
        self.assertEqual([r['reason'] for r in rejected], ['quality-artifact', 'contact-pattern'])
        self.assertTrue(all('text' not in r for r in rejected))

    def test_near_duplicate_prior_and_current_rejected(self):
        text = 'Монгол орны байгаль нуур гол мөрөн уул тал хээрийн тухай. ' * 20
        pages = [page(2, 'А', text + ' Нэмэлт өгүүлбэр.'),
                 page(3, 'Б', 'Өөр соёлын хөгжмийн зэмсгийн тухай тайлбар. ' * 20),
                 page(4, 'В', 'Өөр соёлын хөгжмийн зэмсгийн тухай тайлбар. ' * 20 + ' Өөрчлөлт.')]
        existing = [dict(id='mnwiki-1-1', source='prior', text=text)]
        with patch('scripts.collect_wikipedia.fetch_pages', return_value=pages):
            rows, rejected = collect(['А', 'Б', 'В'], existing, 3)
        self.assertEqual([r['title'] for r in rows], ['Б'])
        self.assertEqual([r['reason'] for r in rejected], ['near-duplicate-text', 'near-duplicate-text'])

    def test_global_source_page_and_text_dedup(self):
        existing = [dict(id='mnwiki-1-101', source='https://mn.wikipedia.org/wiki/Өмнөх', text='өмнөх ' * 30)]
        pages = [page(1, 'Өмнөх'), page(2, 'URL давхардал'), page(3, 'Текст', 'өмнөх ' * 30),
                 page(4, 'Шинэ'), page(4, 'Шинэ redirect'), page(5, 'Ялгаатай')]
        pages[1]['fullurl'] = existing[0]['source']
        with patch('scripts.collect_wikipedia.fetch_pages', return_value=pages):
            rows, rejected = collect(['x'] * 5, existing, 1)
        self.assertEqual([r['title'] for r in rows], ['Шинэ'])
        self.assertEqual({x['reason'] for x in rejected}, {'duplicate-source', 'duplicate-text', 'batch-limit'})
        self.assertEqual(rows[0]['review_status'], 'unreviewed-real-source-text')

    def test_missing_short_incomplete_and_limit(self):
        pages = [dict(title='Алга', missing=''), page(1, 'Богино', 'богино'),
                 dict(title='Дутуу', extract='x' * 200), page(2, 'Нэг'), page(3, 'Хоёр')]
        with patch('scripts.collect_wikipedia.fetch_pages', return_value=pages):
            rows, rejected = collect(['x'] * 5, [], 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual([x['reason'] for x in rejected],
                         ['missing', 'short', 'incomplete-provenance', 'batch-limit'])

    def test_normalization_and_bounds(self):
        self.assertEqual(normalized(' e\u0301 \n x '), 'é x')
        for limit in (0, 21):
            with self.assertRaises(ValueError):
                collect([], [], limit)

    def test_cli_fail_closed_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            titles = Path(temp) / 'titles.txt'; titles.write_text('давхардал\nдавхардал\n')
            out = Path(temp) / 'out'
            cmd = [sys.executable, 'scripts/collect_wikipedia.py', '--titles-file', str(titles),
                   '--output-dir', str(out)]
            run = subprocess.run(cmd, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(out.exists())
