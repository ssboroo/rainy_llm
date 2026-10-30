# Tiny CPU checkpoint-resume equivalence / Жижиг CPU сэргээх туршилт

## Purpose

This is a bounded technical check of the repository's checkpoint inventory, safe RNG restoration, optimizer/scheduler loading and fresh-process continuation. It uses a tiny deterministic PyTorch network so it can run without downloading a base model.

**It is not Qwen training, PEFT/LoRA training, a Mongolian benchmark, licensed-corpus training, or a RAINY model-quality result.** The `adapter_model.safetensors` filename is used only to exercise the existing checkpoint schema; `adapter_config.json` explicitly says the payload is not a PEFT adapter.

## Run

Requires optional `torch`, `numpy` and `safetensors` packages. It does not install dependencies or download models.

```bash
python scripts/checkpoint_resume_equivalence.py --help
python scripts/checkpoint_resume_equivalence.py --output /private/rainy-resume-equivalence-20261030
```

The output path must not exist and must be outside every Git checkout. It contains the run identity, a four-step uninterrupted reference checkpoint, a two-step checkpoint, a fresh Python subprocess that resumes steps 3–4, exact state comparisons and `summary.json`. Keep output private if it is retained; do not commit it or any checkpoint bytes.

The test compares five independent pieces exactly: model tensors, optimizer state, scheduler state, Python/NumPy/Torch RNG state, and trainer step/order/loss history. It exits non-zero on any mismatch. The CLI help remains usable when the optional ML runtime is absent; the actual experiment test is skipped unless Torch and safetensors are installed.

## Measured run (2026-10-30, Asia/Ulaanbaatar)

- Python 3.13.5; PyTorch 2.10.0+cpu; NumPy 2.3.5; safetensors 0.7.0.
- CPU, one thread, float32; eight fixed synthetic numeric rows; four optimizer steps, split after step two.
- Uninterrupted path including initialization and checkpoint save: 0.6701 s.
- Fresh-process resume wall time: 7.1075 s (includes Python process startup); resumed training itself: 0.0040 s for two steps.
- Peak RSS: 328,832 KiB in the parent and 330,240 KiB in the resume child (`ru_maxrss`, Linux).
- Exact equality: **5/5** — model tensors, optimizer, scheduler, RNG and trainer state.

This proves only that the generic checkpoint helpers can restore the small test network's state exactly in a fresh process on this CPU runtime. It does not prove Qwen/PEFT Trainer resume equivalence, CUDA equivalence, stochastic multi-worker equivalence, or language quality.

## Remaining real-model gate

The retained Qwen3-0.6B adapter archive has no base-model weights. The current host also lacks Transformers, PEFT, Accelerate and llama-cpp-python. A real Qwen uninterrupted-versus-resumed run still requires the exact immutable base snapshot, its tested training runtime, the same reviewed training data/config and durable private checkpoint storage. Do not substitute this tiny smoke for that run or relax the RSS supervisor.
