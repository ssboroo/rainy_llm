"""Deterministic bulk collector tests; no external requests."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import collect_wikipedia_bulk as bulk

class BulkTests(unittest.TestCase):
    def test_unicode_line_separator_is_not_jsonl_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = {'id': 'mnwiki-99999999-1', 'text': 'Монгол\u2028өгөгдөл\u0085эх\u2029баримт'}
            (root / 'batch-prior.jsonl').write_text(json.dumps(row, ensure_ascii=False)+'\n', encoding='utf-8')
            self.run_batch(root, {'query': {'allpages': []}}, [])
            self.assertTrue(json.loads((root/'state.json').read_text())['exhausted'])
    def run_batch(self, root, response, pages, limit=1):
        with patch('sys.argv', ['bulk','--root',str(root),'--limit',str(limit),'--max-requests','4']), \
             patch.object(bulk,'request',return_value=response), \
             patch.object(bulk,'fetch_pages',return_value=pages), \
             patch.object(bulk.time,'sleep'), contextlib.redirect_stdout(io.StringIO()):
            bulk.main()
    def page(self, pid, text):
        return dict(pageid=900000000+pid,title=str(pid),extract=text,fullurl=f'https://mn.wikipedia.org/wiki/{pid}',revisions=[{'revid':pid}])
    def test_complete_page_and_resume_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            text='Монгол хэлний өгөгдлийг эх сурвалжтай нь хадгална. '*8
            response={'query':{'allpages':[{'title':'one'}]},'continue':{'apcontinue':'next'}}
            self.run_batch(root,response,[self.page(901,text),self.page(902,text+' Өөр эхийн нэмэлт.')])
            state=json.loads((root/'state.json').read_text())
            self.assertEqual(state['cursor'],'next')
            manifests=list(root.glob('*.manifest.json'))
            self.assertEqual(json.loads(manifests[0].read_text())['accepted'],2)
            self.run_batch(root,{'query':{'allpages':[{'title':'one'}]}},[self.page(901,text)])
            reports=[json.loads(x.read_text()) for x in root.glob('*.manifest.json')]
            self.assertEqual(sum(x['accepted'] for x in reports),2)
            self.assertTrue(json.loads((root/'state.json').read_text())['exhausted'])
    def test_filters_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            text='Монгол хэлний баримт эхийг хадгалдаг. '*10
            pages=[self.page(801,'short'),self.page(802,'English text '*40),
                   self.page(803,text+' test@example.com'),self.page(804,text)]
            self.run_batch(root,{'query':{'allpages':[{'title':'one'}]}},pages)
            report=json.loads(next(root.glob('*.manifest.json')).read_text())
            self.assertEqual(report['accepted'],1)
            self.assertEqual(set(report['rejected']),{'short','low-cyrillic','contact-pattern'})
            row=json.loads(next(root.glob('batch-*.jsonl')).read_text())
            self.assertFalse(row['training_ready'])
            self.assertEqual(row['license'],'CC-BY-SA-4.0')
            self.assertIn('oldid=804',row['revision_url'])
    def test_exhausted_does_not_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'state.json').write_text('{"exhausted":true}')
            with patch.object(bulk,'request') as req:
                self.run_batch(root,{},[])
                req.assert_not_called()

