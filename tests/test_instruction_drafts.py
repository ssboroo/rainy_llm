import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from scripts.build_instruction_drafts import check_manifest, template, build
from scripts.review_corpus import load_corpus, fingerprint


class InstructionDraftTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.hash = load_corpus('data/mnwiki_pilot/corpus.jsonl')
        self.manifest = json.loads(Path('data/mnwiki_pilot/split_manifest.json').read_text())
        self.splits = check_manifest(self.rows, self.hash, self.manifest)

    def test_pending_template_does_not_invent_answers(self):
        packet = template(self.rows)
        self.assertEqual(len(packet), 20)
        self.assertTrue(all(a['instruction'] == '' and a['answer_start'] is None for a in packet))
        with self.assertRaises(ValueError):
            build(self.rows, self.splits, packet)

    def fixture(self):
        r = self.rows[0]
        return dict(id='synthetic-test-only', parent_id=r['id'], parent_sha256=fingerprint(r),
                    instruction='Fixture only, not a reviewed question', answer_start=0, answer_end=3)

    def test_span_provenance_and_split_preserved(self):
        original = copy.deepcopy(self.rows)
        out = build(self.rows, self.splits, [self.fixture()])[0]
        self.assertEqual(out['output'], self.rows[0]['text'][:3])
        self.assertEqual(out['provenance'], self.rows[0])
        self.assertEqual(out['split'], self.splits[self.rows[0]['id']])
        self.assertFalse(out['training_ready'])
        self.assertEqual(self.rows, original)

    def test_invalid_spans_and_parent_refused(self):
        for changes in ({'answer_start': True}, {'answer_start': -1}, {'answer_end': 999999},
                        {'answer_end': 0}, {'parent_sha256': 'bad'}, {'parent_id': 'missing'}):
            with self.assertRaises(ValueError):
                build(self.rows, self.splits, [dict(self.fixture(), **changes)])
        with self.assertRaises(ValueError):
            build(self.rows, self.splits, [self.fixture(), self.fixture()])

    def test_stale_or_reassigned_manifest_refused(self):
        with self.assertRaises(ValueError):
            check_manifest(self.rows, 'bad', self.manifest)
        changed = copy.deepcopy(self.manifest)
        changed['assignments'][0]['split'] = 'invalid'
        with self.assertRaises(ValueError):
            check_manifest(self.rows, self.hash, changed)

    def test_real_cli_template_and_pending_build_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'template'
            args = [sys.executable, 'scripts/build_instruction_drafts.py']
            common = ['data/mnwiki_pilot/corpus.jsonl', '--splits', 'data/mnwiki_pilot/split_manifest.json']
            subprocess.run(args + ['template'] + common + ['--output-dir', str(out)], check=True, capture_output=True)
            summary = json.loads((out / 'summary.json').read_text())
            self.assertEqual(summary['records'], 20)
            bad = Path(temp) / 'bad'
            run = subprocess.run(args + ['build'] + common + ['--annotations', str(out / 'annotations.pending.json'),
                                  '--output-dir', str(bad)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(bad.exists())
            fixture = Path(temp) / 'fixture.json'
            fixture.write_text(json.dumps([self.fixture()]), encoding='utf-8')
            built = Path(temp) / 'built'
            subprocess.run(args + ['build'] + common + ['--annotations', str(fixture),
                           '--output-dir', str(built)], check=True, capture_output=True)
            draft = json.loads((built / 'instructions.draft.jsonl').read_text())
            self.assertEqual(draft['output'], self.rows[0]['text'][:3])
            self.assertEqual(draft['review_status'], 'draft-needs-human-review')
            self.assertNotEqual(subprocess.run(args + ['template'] + common + ['--output-dir', str(out)], capture_output=True).returncode, 0)
