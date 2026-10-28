import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts.restore_synthetic_checkpoint import restore
from scripts.train_lora_cpu import CHECKPOINT_REQUIRED, seal_checkpoint


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.identity = {'total_steps': 2}
        (self.source / 'identity.json').write_text(json.dumps(self.identity))
        cp = self.source / 'checkpoint-2'
        cp.mkdir()
        for name in CHECKPOINT_REQUIRED:
            (cp / name).write_bytes(b'inert test fixture, never deserialized')
        (cp / 'trainer_state.json').write_text('{"global_step": 2}')
        seal_checkpoint(cp, self.identity)
        self.archive = self.root / 'run.tar.gz'

    def pack(self, extra=None):
        with tarfile.open(self.archive, 'w:gz') as tar:
            tar.add(self.source, arcname='original')
            if extra:
                info = tarfile.TarInfo(extra)
                info.size = 1
                tar.addfile(info, io.BytesIO(b'x'))
        return hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def test_restore_exact_and_no_overwrite(self):
        sha = self.pack()
        dest = self.root / 'restored'
        report = restore(self.archive, sha, dest)
        self.assertEqual(report['checkpoint_steps'], [2])
        self.assertFalse(report['pickle_deserialized'])
        self.assertFalse((dest / 'RESTORE_INCOMPLETE').exists())
        for file in self.source.rglob('*'):
            if file.is_file():
                self.assertEqual(file.read_bytes(), (dest/'run'/file.relative_to(self.source)).read_bytes())
        with self.assertRaises(FileExistsError):
            restore(self.archive, sha, dest)

    def test_wrong_archive_hash_writes_nothing(self):
        self.pack()
        dest = self.root / 'restored'
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            restore(self.archive, '0'*64, dest)
        self.assertFalse(dest.exists())

    def test_path_traversal_and_duplicates(self):
        for bad in ('original/../escape', '/absolute', 'original/identity.json', 'other/x'):
            with self.subTest(bad=bad):
                sha = self.pack(bad)
                with self.assertRaises(ValueError):
                    restore(self.archive, sha, self.root/'restored')
                self.assertFalse((self.root/'restored').exists())

    def test_symlink_rejected(self):
        (self.source/'link').symlink_to('identity.json')
        sha = self.pack()
        with self.assertRaises(ValueError):
            restore(self.archive, sha, self.root/'restored')

    def test_corrupt_checkpoint_not_published(self):
        (self.source/'checkpoint-2/optimizer.pt').write_bytes(b'changed')
        sha = self.pack()
        dest = self.root/'restored'
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            restore(self.archive, sha, dest)
        self.assertTrue((dest/'RESTORE_INCOMPLETE').exists())
        self.assertFalse((dest/'run').exists())

    def test_git_destination_rejected(self):
        sha = self.pack()
        (self.root/'.git').mkdir()
        with self.assertRaisesRegex(ValueError, 'outside every Git'):
            restore(self.archive, sha, self.root/'restored')

    def test_archive_limits(self):
        sha = self.pack()
        for key, value in [('MAX_MEMBERS', 1), ('MAX_BYTES', 1)]:
            with self.subTest(key=key), patch('scripts.restore_synthetic_checkpoint.'+key, value):
                with self.assertRaises(ValueError):
                    restore(self.archive, sha, self.root/'restored')
                self.assertFalse((self.root/'restored').exists())
