from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from run_synthetic_bounded import supervise


class BoundedSyntheticTests(unittest.TestCase):
    def test_launch_failure(self):
        with tempfile.TemporaryFile(mode='w+') as log:
            result = supervise(['/nonexistent/rainy-python'], log, 3, 1024, lambda pid: 0)
            self.assertEqual(result['stop_reason'], 'launch_error')
            self.assertFalse(result['completed'])

    def test_monitor_failure_stops_child(self):
        def fail(pid):
            raise RuntimeError('monitor unavailable')
        with tempfile.TemporaryFile(mode='w+') as log:
            result = supervise([sys.executable, '-c', 'import time; time.sleep(5)'],
                               log, 3, 1024, fail)
            self.assertEqual(result['stop_reason'], 'monitor_error')
            self.assertEqual(result['error_type'], 'RuntimeError')
            self.assertFalse(result['completed'])

    def test_success_and_failure(self):
        for code in [0, 3]:
            with tempfile.TemporaryFile(mode='w+') as log:
                result = supervise([sys.executable, '-c', f'raise SystemExit({code})'],
                                   log, 3, 1024, lambda pid: 0)
                self.assertEqual(result['completed'], code == 0)
                self.assertEqual(result['returncode'], code)

    def test_timeout_and_memory(self):
        for seconds, rss, expected in [(0, 0, 'wall_timeout'), (3, 1025, 'rss_limit')]:
            with tempfile.TemporaryFile(mode='w+') as log:
                result = supervise([sys.executable, '-c', 'import time; time.sleep(5)'],
                                   log, seconds, 1024, lambda pid: rss)
                self.assertFalse(result['completed'])
                self.assertEqual(result['stop_reason'], expected)
