"""Tiny deterministic CPU checkpoint-resume equivalence smoke.

This validates RAINY's checkpoint integrity/RNG helpers with a small synthetic
PyTorch network. It is not Qwen/LoRA training, a Mongolian benchmark, or a model
quality result. All artifacts are written to a caller-selected path outside Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
try:
    import resource
except ImportError:  # Windows has no stdlib resource module.
    resource = None
import subprocess
import sys
import time

try:
    from .train_lora_cpu import digest, seal_checkpoint
    from .synthetic_resume import restore_state, save_rng, validate_resume
except ImportError:
    from train_lora_cpu import digest, seal_checkpoint
    from synthetic_resume import restore_state, save_rng, validate_resume

SEED = 20261030
TOTAL_STEPS = 4
SPLIT_STEP = 2
ROW_COUNT = 8


def _peak_rss_platform_units():
    if resource is None:
        return None
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def _rows():
    return [
        {"x": [0.1, 0.2, 0.3, 0.4], "y": 0.13},
        {"x": [0.2, 0.1, 0.4, 0.3], "y": 0.21},
        {"x": [0.3, 0.4, 0.1, 0.2], "y": 0.09},
        {"x": [0.4, 0.3, 0.2, 0.1], "y": 0.17},
        {"x": [0.5, 0.2, 0.1, 0.3], "y": 0.22},
        {"x": [0.6, 0.1, 0.3, 0.2], "y": 0.33},
        {"x": [0.7, 0.3, 0.2, 0.1], "y": 0.29},
        {"x": [0.8, 0.2, 0.4, 0.1], "y": 0.41},
    ]


def _dataset():
    import torch
    rows = _rows()
    features = torch.tensor([row["x"] for row in rows], dtype=torch.float32)
    targets = torch.tensor([[row["y"]] for row in rows], dtype=torch.float32)
    return features, targets


def _identity():
    import importlib.metadata
    import numpy as np
    import torch
    rows = _rows()
    data_sha = hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema": 1,
        "kind": "tiny-cpu-resume-equivalence-technical-smoke-not-rainy-training",
        "human_reviewed": False,
        "model": {"class": "TinyNet", "hidden": 8, "dropout": 0.25},
        "data_sha256": data_sha,
        "seed": SEED,
        "total_steps": TOTAL_STEPS,
        "split_step": SPLIT_STEP,
        "optimizer": {"name": "AdamW", "lr": 0.003, "weight_decay": 0.01},
        "scheduler": {"name": "LambdaLR", "factor": "max(0.5, 1 - 0.1 * step)"},
        "loss": "MSE + deterministic Python/NumPy jitter",
        "runtime": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "safetensors": importlib.metadata.version("safetensors"),
            "threads": 1,
            "device": "cpu",
            "dtype": "float32",
        },
        "runner_sha256": digest(Path(__file__)),
    }


def _initialise():
    import numpy as np
    import torch
    class TinyNet(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = torch.nn.Sequential(
                torch.nn.Linear(4, 8),
                torch.nn.Tanh(),
                torch.nn.Dropout(p=0.25),
                torch.nn.Linear(8, 1),
            )

        def forward(self, x):
            return self.layers(x)
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    model = TinyNet()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda step: max(0.5, 1.0 - 0.1 * step)
    )
    return model, optimizer, scheduler


def _train(model, optimizer, scheduler, order, start_step, stop_step):
    import numpy as np
    import random
    import torch
    features, targets = _dataset()
    losses = []
    model.train()
    for step in range(start_step, stop_step):
        index = order[step]
        jitter = (random.random() + float(np.random.random())) * 0.0001
        x = features[index].unsqueeze(0)
        y = targets[index].unsqueeze(0) + jitter
        optimizer.zero_grad(set_to_none=True)
        loss = torch.nn.functional.mse_loss(model(x), y)
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite loss in tiny CPU smoke")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        losses.append(float(loss.detach()))
    return losses


def _save_checkpoint(run_dir, model, optimizer, scheduler, order, losses, step, identity):
    import json
    import torch
    from safetensors.torch import save_file
    checkpoint = run_dir / f"checkpoint-{step}"
    checkpoint.mkdir(mode=0o700)
    save_file(
        {key: value.detach().cpu().contiguous() for key, value in model.state_dict().items()},
        str(checkpoint / "adapter_model.safetensors"),
    )
    (checkpoint / "adapter_config.json").write_text(
        json.dumps({"kind": "tiny-test-network-not-a-PEFT-adapter", "hidden": 8}),
        encoding="utf-8",
    )
    torch.save(optimizer.state_dict(), checkpoint / "optimizer.pt")
    torch.save(scheduler.state_dict(), checkpoint / "scheduler.pt")
    save_rng(checkpoint / "rng_state.pth")
    (checkpoint / "trainer_state.json").write_text(
        json.dumps({"global_step": step, "order": order, "losses": losses}, allow_nan=False),
        encoding="utf-8",
    )
    seal_checkpoint(checkpoint, identity)
    return checkpoint


def _write_identity(run_dir, identity):
    run_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    (run_dir / "identity.json").write_text(
        json.dumps(identity, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def _resume_worker(run_dir, checkpoint):
    import torch
    from safetensors.torch import load_file
    raw_run_dir = Path(run_dir)
    raw_checkpoint = Path(checkpoint)
    if any(parent.is_symlink() for parent in (raw_run_dir, *raw_run_dir.parents)):
        raise ValueError("run path symlinks are not accepted")
    run_dir = raw_run_dir.resolve(strict=True)
    if raw_checkpoint.is_symlink() or raw_checkpoint.parent.resolve(strict=True) != run_dir:
        raise ValueError("resume checkpoint must be a direct child of the run directory")
    if any((parent / ".git").exists() for parent in (run_dir, *run_dir.parents)):
        raise ValueError("all technical smoke artifacts must be outside Git")
    identity = json.loads((run_dir / "identity.json").read_text(encoding="utf-8"))
    checkpoint, state = validate_resume(raw_checkpoint, identity, ROW_COUNT)
    model, optimizer, scheduler = _initialise()
    model.load_state_dict(load_file(str(checkpoint / "adapter_model.safetensors")))
    restore_state(checkpoint, optimizer, scheduler)
    order = state["order"]
    losses = list(state["losses"])
    start = time.monotonic()
    losses.extend(_train(model, optimizer, scheduler, order, state["global_step"], TOTAL_STEPS))
    elapsed = time.monotonic() - start
    final = _save_checkpoint(
        run_dir, model, optimizer, scheduler, order, losses, TOTAL_STEPS, identity
    )
    result = {
        "steps_resumed": TOTAL_STEPS - state["global_step"],
        "elapsed_seconds": elapsed,
        "peak_rss_platform_units": _peak_rss_platform_units(),
        "final_checkpoint": str(final),
    }
    (run_dir / "worker-result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result))


def _state_equal(left, right):
    import torch
    if type(left) is not type(right):
        return False
    if isinstance(left, torch.Tensor):
        return left.dtype == right.dtype and left.shape == right.shape and torch.equal(left, right)
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_state_equal(left[k], right[k]) for k in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(_state_equal(a, b) for a, b in zip(left, right))
    return left == right


def _compare(reference, resumed):
    import torch
    from safetensors.torch import load_file
    results = {
        "model_tensors_exact": _state_equal(
            load_file(str(reference / "adapter_model.safetensors")),
            load_file(str(resumed / "adapter_model.safetensors")),
        ),
        "optimizer_exact": _state_equal(
            torch.load(reference / "optimizer.pt", map_location="cpu", weights_only=True),
            torch.load(resumed / "optimizer.pt", map_location="cpu", weights_only=True),
        ),
        "scheduler_exact": _state_equal(
            torch.load(reference / "scheduler.pt", map_location="cpu", weights_only=True),
            torch.load(resumed / "scheduler.pt", map_location="cpu", weights_only=True),
        ),
        "rng_exact": _state_equal(
            torch.load(reference / "rng_state.pth", map_location="cpu", weights_only=True),
            torch.load(resumed / "rng_state.pth", map_location="cpu", weights_only=True),
        ),
        "trainer_state_exact": json.loads(
            (reference / "trainer_state.json").read_text(encoding="utf-8")
        ) == json.loads((resumed / "trainer_state.json").read_text(encoding="utf-8")),
    }
    results["all_exact"] = all(results.values())
    return results


def run_experiment(output):
    raw_output = Path(output).expanduser()
    if any(parent.is_symlink() for parent in (raw_output, *raw_output.parents)):
        raise ValueError("output path symlinks are not accepted")
    output = raw_output.resolve()
    if output.exists():
        raise ValueError("output must not already exist")
    if any((parent / ".git").exists() for parent in (output, *output.parents)):
        raise ValueError("all technical smoke artifacts must be outside Git")
    import torch
    identity = _identity()
    output.mkdir(mode=0o700, parents=True)
    reference_dir = output / "reference"
    resumed_dir = output / "resumed"
    _write_identity(reference_dir, identity)
    _write_identity(resumed_dir, identity)

    started = time.monotonic()
    model, optimizer, scheduler = _initialise()
    order = torch.randperm(ROW_COUNT).tolist()
    reference_losses = _train(model, optimizer, scheduler, order, 0, TOTAL_STEPS)
    reference_cp = _save_checkpoint(
        reference_dir, model, optimizer, scheduler, order, reference_losses, TOTAL_STEPS, identity
    )
    reference_seconds = time.monotonic() - started

    model, optimizer, scheduler = _initialise()
    interrupted_order = torch.randperm(ROW_COUNT).tolist()
    interrupted_losses = _train(
        model, optimizer, scheduler, interrupted_order, 0, SPLIT_STEP
    )
    split_cp = _save_checkpoint(
        resumed_dir, model, optimizer, scheduler, interrupted_order,
        interrupted_losses, SPLIT_STEP, identity
    )

    child_start = time.monotonic()
    child = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker",
         "--run-dir", str(resumed_dir), "--checkpoint", str(split_cp)],
        check=False, capture_output=True, text=True, timeout=60,
        env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
             "HF_HUB_DISABLE_TELEMETRY": "1"},
    )
    child_seconds = time.monotonic() - child_start
    if child.returncode != 0:
        raise RuntimeError(
            f"fresh-process resume failed (exit {child.returncode}): {child.stderr[-3000:]}"
        )
    resumed_cp = resumed_dir / f"checkpoint-{TOTAL_STEPS}"
    comparisons = _compare(reference_cp, resumed_cp)
    summary = {
        "kind": identity["kind"],
        "model_quality_evaluated": False,
        "mongolian_quality_gain": False,
        "training_data": "8 deterministic synthetic numeric rows; no licensed corpus",
        "total_steps": TOTAL_STEPS,
        "resume_boundary": SPLIT_STEP,
        "reference_seconds": reference_seconds,
        "fresh_process_resume_wall_seconds": child_seconds,
        "fresh_process_resume_training_seconds": json.loads(
            (resumed_dir / "worker-result.json").read_text()
        )["elapsed_seconds"],
        "peak_rss_platform_units_parent": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_rss_platform_units_resume_child": json.loads(
            (resumed_dir / "worker-result.json").read_text()
        )["peak_rss_platform_units"],
        "runtime": identity["runtime"],
        "identity_sha256": hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "comparisons": comparisons,
        "note": "Technical checkpoint equivalence only; not Qwen, LoRA, Mongolian evaluation or RAINY model training.",
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))
    if not comparisons["all_exact"]:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--run-dir")
    parser.add_argument("--checkpoint")
    args = parser.parse_args()
    if args.worker:
        if not args.run_dir or not args.checkpoint or args.output:
            parser.error("--worker requires --run-dir and --checkpoint only")
        _resume_worker(Path(args.run_dir), Path(args.checkpoint))
    else:
        if not args.output or args.run_dir or args.checkpoint:
            parser.error("parent mode requires --output only")
        run_experiment(args.output)


if __name__ == "__main__":
    main()
