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

## Verify a stored experiment

Do not trust a copied aggregate without its raw predictions. Recompute exact-match scores and verify the case-file hash, completion status, per-row measurement types, total generation time, generated-token total and token-limit count:

```bash
python scripts/verify_experiment.py experiments/qwen35-4b-cpu-q4km-v1 \
  --cases evaluation/mn_smoke.jsonl
```

Add `--output experiments/<run>/integrity.json` only once when recording a new report; the command refuses to overwrite an existing file. On 2026-10-09, all five retained CPU experiments passed this verification against their raw predictions. The oldest float32 Qwen3-0.6B metadata predates token aggregates, so its otherwise valid report retains two explicit legacy warnings. This verification proves internal artifact consistency, not model quality, held-out provenance or human approval.

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

## Runtime and latency comparison guard — 2026-10-12

`compare_benchmarks.py` now compares backend, llama-cpp-python/Python versions, context size, temperature and repetition penalty alongside the existing evaluation, precision and decoding fields. GGUF metadata must contain valid runtime settings; matching missing fields do not count as valid GGUF configuration. Model artifact, tokenizer revision and chat-template hashes are model-specific identities, not required to be equal across different models.

`comparable` describes matched recorded evaluation/runtime settings. `latency_comparable` additionally requires matching non-empty hardware descriptions; otherwise `seconds_per_case_delta` is null and promotion is blocked. Individual measured times remain visible. This is a necessary guard, not proof of identical CPU load, build flags, warmup or throughput. Seconds per case depend on generated answer length and must not be called tokens/second.

The retained Qwen3-4B/Qwen3.5-4B reports lack hardware fields. Their 7/24 and 12/24 scores remain unchanged, but a newly computed [comparison audit](../experiments/comparison-audit-2026-10-12.json) blocks a controlled latency claim. Earlier reports are historical and remain intact for rollback. No inference was repeated.

Монгол: GGUF runtime/context/decoding зөрүүтэй бол харьцуулалт блоклоно. Hardware дутуу/өөр бол latency delta гаргахгүй. Өмнөх 7/24, 12/24 оноо хэвээр; хуучин metadata-д hardware байхгүй тул хурдны давуу тал батлагдсан гэж дүгнэхгүй.
