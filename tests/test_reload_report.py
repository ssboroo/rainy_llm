import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ReloadReportTests(unittest.TestCase):
    def test_existing_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'report.json'
            report.write_text('retained evidence', encoding='utf-8')
            result = subprocess.run([sys.executable, 'scripts/verify_synthetic_adapter.py',
                '--model', 'missing', '--run', 'missing', '--evaluation', 'missing',
                '--step', '16', '--report', str(report)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FileExistsError', result.stderr)
            self.assertEqual(report.read_text(), 'retained evidence')
