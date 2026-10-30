import json
from pathlib import Path
import tempfile
import unittest
import importlib.util
from scripts.synthetic_resume import validate_resume
from scripts.train_lora_cpu import seal_checkpoint, CHECKPOINT_REQUIRED


class _UntrustedPayload:
    pass

class ResumeTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('torch'), 'optional real torch backend')
    def test_rng_roundtrip_after_perturbation(self):
        import torch
        import random
        import numpy as np
        from scripts.synthetic_resume import save_rng, restore_state
        with tempfile.TemporaryDirectory() as tmp:
            cp = Path(tmp)
            model = torch.nn.Linear(2, 1)
            optimizer = torch.optim.AdamW(model.parameters())
            scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1)
            torch.save(optimizer.state_dict(), cp/'optimizer.pt')
            torch.save(scheduler.state_dict(), cp/'scheduler.pt')
            save_rng(cp/'rng_state.pth')
            expected = (random.random(), np.random.rand(), torch.rand(3))
            random.seed(999); np.random.seed(999); torch.manual_seed(999)
            restore_state(cp, optimizer, scheduler)
            actual = (random.random(), np.random.rand(), torch.rand(3))
            self.assertEqual(expected[:2], actual[:2])
            self.assertTrue(torch.equal(expected[2],actual[2]))

    def fixture(self, root, order=None):
        identity = {'total_steps':4, 'kind':'synthetic'}
        (root/'identity.json').write_text(json.dumps(identity))
        cp = root/'checkpoint-2'; cp.mkdir()
        for name in CHECKPOINT_REQUIRED:
            (cp/name).write_text('{}')
        (cp/'trainer_state.json').write_text(json.dumps(dict(global_step=2, losses=[1,2], order=order or [2,0,1])))
        seal_checkpoint(cp, identity)
        return cp, identity

    def test_valid_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            cp, identity = self.fixture(Path(tmp))
            self.assertEqual(validate_resume(cp,identity,3)[1]['global_step'],2)
            (cp/'optimizer.pt').write_text('changed')
            with self.assertRaisesRegex(ValueError,'integrity'):
                validate_resume(cp,identity,3)

    def test_identity_and_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            cp, identity = self.fixture(Path(tmp), [0,0,2])
            with self.assertRaisesRegex(ValueError,'identity'):
                validate_resume(cp,dict(identity,total_steps=8),3)
            with self.assertRaisesRegex(ValueError,'training state'):
                validate_resume(cp,identity,3)


    @unittest.skipUnless(importlib.util.find_spec('torch'), 'optional real torch backend')
    def test_legacy_numpy_rng_state_roundtrip_after_perturbation(self):
        import torch
        import random
        import numpy as np
        from scripts.synthetic_resume import restore_state
        with tempfile.TemporaryDirectory() as tmp:
            cp = Path(tmp)
            model = torch.nn.Linear(2, 1)
            optimizer = torch.optim.AdamW(model.parameters())
            scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
            torch.save(optimizer.state_dict(), cp/'optimizer.pt')
            torch.save(scheduler.state_dict(), cp/'scheduler.pt')
            # Legacy form: NumPy stores MT19937 keys as a uint32 ndarray.
            torch.save(dict(python=random.getstate(), cpu=torch.get_rng_state(),
                            numpy=np.random.get_state()), cp/'rng_state.pth')
            expected = (random.random(), np.random.rand(), torch.rand(3))
            random.seed(999); np.random.seed(999); torch.manual_seed(999)
            restore_state(cp, optimizer, scheduler)
            actual = (random.random(), np.random.rand(), torch.rand(3))
            self.assertEqual(expected[:2], actual[:2])
            self.assertTrue(torch.equal(expected[2], actual[2]))

    @unittest.skipUnless(importlib.util.find_spec('torch'), 'optional real torch backend')
    def test_rng_loader_rejects_untrusted_pickle_globals(self):
        import torch
        import random
        import numpy as np
        from scripts.synthetic_resume import _load_rng_state
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'untrusted.pth'
            torch.save(dict(python=random.getstate(), cpu=torch.get_rng_state(),
                            numpy=np.random.get_state(), extra=_UntrustedPayload()), path)
            with self.assertRaises(Exception):
                _load_rng_state(path)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cp, identity=self.fixture(root)
            link=root/'link'; link.symlink_to(cp, target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'):
                validate_resume(link,identity,3)
