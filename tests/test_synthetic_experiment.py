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
for name in ['mn_smoke.jsonl', 'mn_v2_draft.jsonl']:
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
            '--model', 'absent', '--evaluation', 'absent', '--output', '/tmp/unused', '--steps', '33'],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('limited to 32', result.stderr)
