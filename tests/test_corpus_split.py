import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.review_corpus import load_corpus, sha
from scripts.split_corpus import partition


class CorpusSplitTests(unittest.TestCase):
    def test_transitive_sources_and_text(self):
        rows = [dict(id='a', source='one', text='эх'),
                dict(id='b', source='one', text='өөр эх'),
                dict(id='c', source='two', text=' өөр  эх\n')]
        outputs, manifest = partition(rows)
        self.assertEqual(manifest['group_count'], 1)
        self.assertEqual(max(map(len, outputs.values())), 3)

    def test_order_independent_preserves_provenance(self):
        rows, _ = load_corpus('data/mnwiki_pilot/corpus.jsonl')
        original = copy.deepcopy(rows)
        a = partition(rows)
        self.assertEqual(a, partition(list(reversed(rows))))
        self.assertEqual(rows, original)
        self.assertEqual(sorted(sum(a[0].values(), []), key=lambda r: r['id']),
                         sorted(original, key=lambda r: r['id']))
        self.assertFalse(a[1]['training_ready'])

    def test_unicode_normalization(self):
        rows = [dict(id='a', source='one', text='e\u0301'),
                dict(id='b', source='two', text='é')]
        self.assertEqual(partition(rows)[1]['group_count'], 1)

    def test_empty_and_duplicate_ids_rejected(self):
        for rows in ([], [dict(id='a'), dict(id='a')]):
            with self.assertRaises(ValueError):
                partition(rows)

    def test_real_cli_hashes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'parts'
            cmd = [sys.executable, 'scripts/split_corpus.py',
                   'data/mnwiki_pilot/corpus.jsonl', '--output-dir', str(out)]
            subprocess.run(cmd, check=True, capture_output=True)
            manifest = json.loads((out / 'manifest.json').read_text())
            self.assertEqual(sum(manifest['counts'].values()), 20)
            for name, expected in manifest['output_sha256'].items():
                self.assertEqual(sha((out / (name + '.jsonl')).read_bytes()), expected)
            before = (out / 'manifest.json').read_bytes()
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertEqual(before, (out / 'manifest.json').read_bytes())
