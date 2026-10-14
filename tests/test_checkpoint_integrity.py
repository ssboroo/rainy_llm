"""Filesystem fault tests, not model training or tensor deserialization tests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.train_lora_cpu import (
    CHECKPOINT_MANIFEST, CHECKPOINT_REQUIRED, check_resume, seal_checkpoint,
)


class CheckpointIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.identity = {'seed': 42, 'total_steps': 20}
        (self.root / 'run_identity.json').write_text(json.dumps(self.identity))
        self.cp = self.make_checkpoint(2)

    def make_checkpoint(self, step):
        cp = self.root / f'checkpoint-{step}'
        cp.mkdir()
        for name in CHECKPOINT_REQUIRED:
            (cp / name).write_bytes(b'synthetic-not-tensor-data')
        (cp / 'trainer_state.json').write_text(json.dumps({'global_step': step}))
        return cp

    def test_success_and_refuse_reseal(self):
        record = seal_checkpoint(self.cp, self.identity)
        self.assertEqual(record['global_step'], 2)
        self.assertEqual(set(record['files']), CHECKPOINT_REQUIRED)
        self.assertEqual(check_resume(self.root, self.cp, self.identity), str(self.cp))
        original = (self.cp / CHECKPOINT_MANIFEST).read_bytes()
        with self.assertRaisesRegex(ValueError, 'already sealed'):
            seal_checkpoint(self.cp, self.identity)
        self.assertEqual((self.cp / CHECKPOINT_MANIFEST).read_bytes(), original)

    def test_unsealed_and_empty_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsealed'):
            check_resume(self.root, self.cp, self.identity)
        (self.cp / 'optimizer.pt').write_bytes(b'')
        with self.assertRaisesRegex(ValueError, 'empty'):
            seal_checkpoint(self.cp, self.identity)
        self.assertFalse((self.cp / CHECKPOINT_MANIFEST).exists())

    def test_each_component_corruption_and_deletion(self):
        seal_checkpoint(self.cp, self.identity)
        for name in sorted(CHECKPOINT_REQUIRED):
            with self.subTest(name=name):
                path = self.cp / name
                original = path.read_bytes()
                # Same-size mutation must be detected, not just truncation.
                changed = bytearray(original)
                changed[-1] ^= 1
                path.write_bytes(changed)
                with self.assertRaises(ValueError):
                    check_resume(self.root, self.cp, self.identity)
                path.unlink()
                with self.assertRaisesRegex(ValueError, 'incomplete'):
                    check_resume(self.root, self.cp, self.identity)
                path.write_bytes(original)
        self.assertEqual(check_resume(self.root, self.cp, self.identity), str(self.cp))

    def test_added_file_or_changed_marker_rejected(self):
        seal_checkpoint(self.cp, self.identity)
        extra = self.cp / 'unexpected.bin'
        extra.write_bytes(b'extra')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            check_resume(self.root, self.cp, self.identity)
        extra.unlink()
        marker = self.cp / CHECKPOINT_MANIFEST
        record = json.loads(marker.read_text())
        record['run_identity_sha256'] = '0' * 64
        marker.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'integrity'):
            check_resume(self.root, self.cp, self.identity)

    def test_inconsistent_and_boolean_steps_rejected(self):
        for step in [True, 0, 3, 21]:
            with self.subTest(step=step):
                (self.cp / 'trainer_state.json').write_text(json.dumps({'global_step': step}))
                with self.assertRaisesRegex(ValueError, 'step'):
                    seal_checkpoint(self.cp, self.identity)

    def test_symlink_file_and_checkpoint_rejected(self):
        seal_checkpoint(self.cp, self.identity)
        link = self.root / 'checkpoint-3'
        link.symlink_to(self.cp, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            check_resume(self.root, link, self.identity)
        target = self.cp / 'optimizer.pt'
        target.unlink()
        target.symlink_to(self.cp / 'scheduler.pt')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            check_resume(self.root, self.cp, self.identity)

    def test_interrupted_marker_write_preserves_prior_checkpoint(self):
        prior = self.make_checkpoint(1)
        seal_checkpoint(prior, self.identity)
        before = (prior / CHECKPOINT_MANIFEST).read_bytes()
        with patch('scripts.train_lora_cpu.os.replace', side_effect=OSError('simulated I/O failure')):
            with self.assertRaises(OSError):
                seal_checkpoint(self.cp, self.identity)
        self.assertFalse((self.cp / CHECKPOINT_MANIFEST).exists())
        with self.assertRaisesRegex(ValueError, 'complete'):
            check_resume(self.root, self.cp, self.identity)
        self.assertEqual(check_resume(self.root, prior, self.identity), str(prior))
        self.assertEqual((prior / CHECKPOINT_MANIFEST).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
