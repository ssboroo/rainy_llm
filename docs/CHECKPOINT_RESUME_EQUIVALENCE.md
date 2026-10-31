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

The output path must not exist and must be outside every Git checkout. It contains the run identity, a four-step uninterrupted reference checkpoint, a two-step checkpoint, a fresh Python subprocess that resumes steps 3–4, exact state comparisons and `summary.json`. Keep output private if it is retained; do not commit it or any checkpoint bytes. Peak RSS uses `resource.getrusage` where available; on Windows the report records `null` rather than inventing a value.

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

The private 2026-10-25 archive's base model is now identified by matching its recorded `model.safetensors` SHA-256 (`f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`) and `config.json` SHA-256 (`660db3b73d788119c04535e48cf9be5f55bc3100841a718637ae695b442f27dd`) to the official `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` snapshot. The archive's own `identity.json` nevertheless has null `model_id` and `model_revision` fields; future runners must record these explicitly. The archive does not include the 1.5 GB base weights. The current host also lacks the archive's pinned Transformers 4.51.3, PEFT 0.15.2 and Accelerate 1.6.0 runtime. A real Qwen uninterrupted-versus-resumed run still requires those exact base bytes, matching training runtime, the same reviewed training data/config and durable private checkpoint storage. Do not substitute this tiny smoke for that run or relax the RSS supervisor.
