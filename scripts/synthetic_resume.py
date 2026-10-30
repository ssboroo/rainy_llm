"""Integrity-checked state restoration for synthetic technical runs only."""
import json
import math
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
    # Store MT19937 keys as primitive integers so new checkpoints need no
    # NumPy pickle globals when loaded with torch's weights-only unpickler.
    torch.save(dict(python=random.getstate(), cpu=torch.get_rng_state(),
        numpy=(name, keys.tolist(), pos, has_gauss, cached)), path)


def _load_rng_state(path):
    """Load current and legacy NumPy RNG payloads without arbitrary unpickling.

    Older checkpoints stored NumPy's uint32 ndarray in rng_state.pth. PyTorch's
    weights-only unpickler rejects that legacy payload unless the narrowly
    required NumPy reconstruction symbols are allowlisted. No weights_only=False
    fallback is permitted.
    """
    import torch
    import numpy as np

    core = getattr(np, "_core", None)
    if core is None:
        core = np.core
    multiarray = getattr(core, "multiarray", None)
    reconstruct = getattr(multiarray, "_reconstruct", None)
    safe_globals = getattr(torch.serialization, "safe_globals", None)
    if reconstruct is None or safe_globals is None:
        raise RuntimeError("safe legacy RNG loading requires PyTorch safe_globals and NumPy multiarray")
    allowed = [np.ndarray, np.dtype, type(np.dtype(np.uint32)), reconstruct]
    with safe_globals(allowed):
        state = torch.load(path, map_location="cpu", weights_only=True)

    if not isinstance(state, dict) or set(state) != {"python", "numpy", "cpu"}:
        raise ValueError("invalid RNG state structure")
    python_state = state["python"]
    if (not isinstance(python_state, tuple) or len(python_state) != 3
            or type(python_state[0]) is not int
            or not isinstance(python_state[1], tuple) or len(python_state[1]) != 625
            or any(type(value) is not int for value in python_state[1])
            or not (python_state[2] is None or type(python_state[2]) in (int, float))):
        raise ValueError("invalid Python RNG state")

    numpy_state = state["numpy"]
    if (not isinstance(numpy_state, tuple) or len(numpy_state) != 5
            or numpy_state[0] != "MT19937"):
        raise ValueError("invalid NumPy RNG state")
    keys = np.asarray(numpy_state[1])
    if (keys.shape != (624,) or keys.dtype.kind not in "iu"
            or int(keys.min()) < 0 or int(keys.max()) > np.iinfo(np.uint32).max):
        raise ValueError("invalid NumPy RNG key array")
    if (type(numpy_state[2]) is not int or not 0 <= numpy_state[2] <= 624
            or type(numpy_state[3]) not in (int, bool) or numpy_state[3] not in (0, 1)
            or type(numpy_state[4]) not in (int, float) or not math.isfinite(numpy_state[4])):
        raise ValueError("invalid NumPy RNG metadata")

    cpu_state = state["cpu"]
    if (not isinstance(cpu_state, torch.Tensor) or cpu_state.dtype != torch.uint8
            or cpu_state.ndim != 1 or cpu_state.numel() == 0):
        raise ValueError("invalid CPU Torch RNG state")
    return state


def restore_state(checkpoint, optimizer, scheduler):
    """Call only after validate_resume; never unpickle arbitrary Python objects."""
    import torch
    import random
    import numpy as np
    optimizer.load_state_dict(torch.load(checkpoint/'optimizer.pt', map_location='cpu', weights_only=True))
    scheduler.load_state_dict(torch.load(checkpoint/'scheduler.pt', map_location='cpu', weights_only=True))
    rng = _load_rng_state(checkpoint/'rng_state.pth')
    name, keys, pos, has_gauss, cached = rng['numpy']
    np.random.set_state((name, np.asarray(keys, dtype=np.uint32), pos, has_gauss, cached))
    random.setstate(rng['python'])
    torch.set_rng_state(rng['cpu'])
