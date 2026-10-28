"""Integrity-checked state restoration for synthetic technical runs only."""
import json
from pathlib import Path
try:
    from .train_lora_cpu import checkpoint_inventory, checkpoint_step, identity_digest, CHECKPOINT_MANIFEST
except ImportError:
    from train_lora_cpu import checkpoint_inventory, checkpoint_step, identity_digest, CHECKPOINT_MANIFEST


def validate_resume(checkpoint, identity, row_count):
    path = Path(checkpoint)
    if path.is_symlink():
        raise ValueError('checkpoint symlink rejected')
    path = path.resolve(strict=True)
    source = json.loads((path.parent/'identity.json').read_text())
    if source != identity:
        raise ValueError('resume identity mismatch')
    expected = dict(schema=1, global_step=checkpoint_step(path, identity),
        run_identity_sha256=identity_digest(identity), files=checkpoint_inventory(path))
    if json.loads((path/CHECKPOINT_MANIFEST).read_text()) != expected:
        raise ValueError('checkpoint integrity mismatch')
    state = json.loads((path/'trainer_state.json').read_text())
    step, order = state['global_step'], state['order']
    if (type(step) is not int or not 0 < step < identity['total_steps']
            or len(state['losses']) != step or len(order) != row_count
            or any(type(x) is not int for x in order)
            or sorted(order) != list(range(row_count))):
        raise ValueError('invalid or completed training state')
    return path, state


def save_rng(path):
    import torch
    import random
    import numpy as np
    name, keys, pos, has_gauss, cached = np.random.get_state()
    torch.save(dict(python=random.getstate(), cpu=torch.get_rng_state(),
        numpy=(name, keys.tolist(), pos, has_gauss, cached)), path)


def restore_state(checkpoint, optimizer, scheduler):
    """Call only after validate_resume; never unpickle arbitrary Python objects."""
    import torch
    import random
    import numpy as np
    optimizer.load_state_dict(torch.load(checkpoint/'optimizer.pt', map_location='cpu', weights_only=True))
    scheduler.load_state_dict(torch.load(checkpoint/'scheduler.pt', map_location='cpu', weights_only=True))
    rng = torch.load(checkpoint/'rng_state.pth', map_location='cpu', weights_only=True)
    name, keys, pos, has_gauss, cached = rng['numpy']
    np.random.set_state((name, np.asarray(keys, dtype=np.uint32), pos, has_gauss, cached))
    random.setstate(rng['python'])
    torch.set_rng_state(rng['cpu'])
