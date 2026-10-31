import json
from pathlib import Path
import subprocess
import sys
import unittest


class SyntheticExperimentTests(unittest.TestCase):
    def test_cli_and_isolated_fixtures(self):
        result = subprocess.run([sys.executable, 'scripts/synthetic_lora_experiment.py', '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, '-c', '''
import sys
sys.path.insert(0, 'scripts')
from synthetic_lora_experiment import synthetic_rows, validate_separation
import json
from pathlib import Path
rows = synthetic_rows()
assert len(rows) == 32
for name in ['mn_smoke.jsonl', 'mn_v2_draft.jsonl', 'mn_transfer_draft_20261026.jsonl']:
    cases = [json.loads(line) for line in Path('evaluation', name).read_text().splitlines()]
    validate_separation(rows, cases)
try:
    validate_separation(rows, [{'prompt': rows[0]['prompt']}])
except ValueError:
    pass
else:
    raise AssertionError('leak accepted')
try:
    validate_separation(rows + rows[:1], [])
except ValueError:
    pass
else:
    raise AssertionError('duplicate accepted')
'''], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_budget_rejected_before_loading(self):
        result = subprocess.run([sys.executable, 'scripts/synthetic_lora_experiment.py',
            '--model', 'absent', '--model-id', 'Qwen/Qwen3-0.6B', '--model-revision', 'c1899de289a04d12100db370d81485cdf75e47ca',
            '--weights-license', 'Apache-2.0', '--code-license', 'not separately specified',
            '--model-card-url', 'https://huggingface.co/Qwen/Qwen3-0.6B',
            '--license-url', 'https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/LICENSE',
            '--evaluation', 'absent', '--output', '/tmp/unused', '--steps', '33'],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('limited to 32', result.stderr)

    def test_seed_rejected_before_loading(self):
        result = subprocess.run([sys.executable, 'scripts/synthetic_lora_experiment.py',
            '--model', 'absent', '--model-id', 'Qwen/Qwen3-0.6B', '--model-revision', 'c1899de289a04d12100db370d81485cdf75e47ca',
            '--weights-license', 'Apache-2.0', '--code-license', 'not separately specified',
            '--model-card-url', 'https://huggingface.co/Qwen/Qwen3-0.6B',
            '--license-url', 'https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/LICENSE',
            '--evaluation', 'absent', '--output', '/tmp/unused', '--seed', '-1'],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('seed must be', result.stderr)

    def test_fresh_transfer_lexical_separation(self):
        result = subprocess.run([sys.executable, '-c', '''
import sys, json
from pathlib import Path
sys.path.insert(0, 'scripts')
from synthetic_lora_experiment import synthetic_rows
from audit_evaluation_overlap import audit_overlap
cases = [json.loads(s) for s in Path('evaluation/mn_transfer_draft_20261026.jsonl').read_text().splitlines()]
assert len(cases) == 12
report = audit_overlap(cases, [(1, i+1, r) for i,r in enumerate(synthetic_rows())], threshold=0.5)
assert report['candidate_count'] == 0, report
'''], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
