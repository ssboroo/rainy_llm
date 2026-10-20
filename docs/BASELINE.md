# Reproduce the CPU baseline

For the first three CPU experiments and experimental local question CLI, see [the 2026-10-05 quality report](QUALITY_EXPERIMENT_2026-10-05.md). A later [matched Qwen3.5-4B Q4_K_M experiment](QUALITY_EXPERIMENT_2026-10-07.md) scored 12/24 versus 7/24 for the retained Qwen3-4B-Instruct-2507 run. The gate still blocked promotion because the public smoke set is not human-reviewed and resource/cost metadata are incomplete. No baseline has been replaced.

This baseline deliberately uses the small older Qwen/Qwen3-0.6B model because it can run on the available CPU. It is not the newest candidate and is not the final RAINY base model.

Model card: https://huggingface.co/Qwen/Qwen3-0.6B
Model license: Apache-2.0 (upstream model card).
Pinned revision: c1899de289a04d12100db370d81485cdf75e47ca

## Compare without moving the baseline

```bash
python scripts/compare_benchmarks.py \
  experiments/qwen3-06b-cpu-v1 \
  experiments/candidate-run
```

The comparison refuses apples-to-oranges claims when evaluation SHA-256, metric, total cases, seed, sampling, token budget or thinking mode differ. Both revisions must be immutable hashes. A higher exact-match score alone is not enough for promotion: predictions must be complete and both runs must record `hardware`, `peak_vram_gb`, and `estimated_cost_usd`. Human review remains separate.

The legacy CPU baseline is a valid rollback artifact, but it predates those three resource fields. Therefore it can be compared for score and measured wall time, but the automated gate will not approve a production/base-model promotion from it until a fully instrumented baseline rerun exists.

As of 2026-10-06, numeric measurements must be finite: NaN/Infinity, booleans and invalid count types are rejected. Missing predictions in either run block technical eligibility. Invalid numeric input produces a validation report and CLI exit 1 rather than a division traceback. `promotion_eligible` is only a technical prerequisite; it is not release approval and does not independently verify human review, prediction-file integrity or held-out provenance.

## Setup

Use a separate Python 3.12 virtual environment. Install CPU PyTorch first, then the tested Transformers version. The exact resolved environment for the recorded run is in requirements/baseline-cpu-lock.txt (Linux CPU snapshot, not a universal cross-platform lock).

```bash
python -m venv .venv-baseline
# Linux/macOS: source .venv-baseline/bin/activate
# Windows PowerShell: .venv-baseline\Scripts\Activate.ps1
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install transformers==4.51.3 accelerate
python scripts/run_baseline.py --revision c1899de289a04d12100db370d81485cdf75e47ca --output-dir experiments/my-baseline
```

The unpinned torch install above is a convenient setup path, not exact reproduction. To reproduce the recorded environment, install the versions in the lock snapshot with the CPU wheel index available. Initial model download needs internet access and roughly gigabyte-scale disk space. CPU RAM must also hold float32 weights and runtime buffers.

Run parameters: 4 CPU threads, float32, seed 42, thinking disabled, greedy generation, 64 new tokens per case, no added system prompt. Greedy decoding is a reproducibility choice, not the model-card recommended sampling recipe; do not compare this score directly with vendor benchmarks.

The script writes real model responses, per-response elapsed generation time, output token counts, token-limit flags, pinned model revision, library versions, cases SHA-256 and exact-match scores. Timing excludes initial download/model loading and includes CPU generation overhead. Partial predictions survive interruption; only metadata status completed indicates a full run. Use a new output directory for every run.

The model receives only each question's prompt, never its reference answer. Scoring occurs after generation. Questions remain public, small, draft and not human-validated; 24-case accuracy is a narrow smoke result, not general Mongolian fluency or statistical evidence of production readiness.

## Real data is separate

The Wikipedia pilot in data/mnwiki_pilot is retrieved source material. It was NOT used to train, tune, or prompt this baseline. Do not imply that downloading data improves the model. Further work: review and clean documents, define train/validation/held-out sources, prepare legitimate supervision and compare larger feasible models before training.

## Монгол

Энэ туршилт жижиг Qwen3-0.6B загварыг CPU дээр ажиллуулна. Хамгийн шинэ загвар биш, эцсийн сонголт биш. 24 ноорог асуултын бодит хариу, хугацаа, тохиргоо, оноог хадгална. Wikipedia-ийн цуглуулсан эхүүдийг загварт сургаагүй, тестийн prompt-д нэмж өгөөгүй. Оноо нь форматад мэдрэмтгий анхны шалгалт бөгөөд Монгол хэлний нийт чадварын баталгаа биш.
