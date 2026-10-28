# Bounded real CPU LoRA experiment

This is an executable **synthetic technical smoke**, not reviewed-corpus RAINY
training, not from-scratch pretraining, and not a general Mongolian quality claim.
It does not accept external training data or bypass `train_lora_cpu.py` review
requirements. The 32 arithmetic/copy fixtures are AI-authored, unreviewed, and
must not be counted as collected sources. The public 24-case benchmark remains
a draft diagnostic, not an independent release benchmark.

## Reproduce

Use Python 3.12 and `requirements/synthetic-smoke-20261025-lock.txt` in an isolated
environment. The recorded Torch wheel includes CUDA libraries, but this runner
always executes on CPU; it does not rent a GPU or call inference APIs.

Download `Qwen/Qwen3-0.6B` at immutable revision
`c1899de289a04d12100db370d81485cdf75e47ca` with `huggingface_hub.snapshot_download`
to a materialized local directory. Include configuration, tokenizer, safetensors,
README and Apache-2.0 LICENSE. Upstream source:
https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca

```bash
timeout 1200 python scripts/synthetic_lora_experiment.py \
  --model /private/models/qwen3-0.6b \
  --evaluation evaluation/mn_smoke.jsonl \
  --output /private/experiments/new-run \
  --steps 16 --seconds 600
```

Output must be new, outside every Git checkout, and disjoint from the model.
The outer timeout bounds the entire process; the inner cap checks after each
training step. CPU float32, 4 threads, seed 42, greedy non-thinking decoding,
32 new tokens, rank-4 q/v LoRA, and assistant-only masked loss are fixed.
The script rejects exact normalized training/evaluation prompt overlap and
tokenization prefix mismatch; it does not claim to detect all semantic leakage.
Before/after use identical evaluation bytes, decoding and hardware. Truncated
answers remain in the results; no answer repair or selective retries occur.

Inference/training use local-files-only loading and HF offline flags; Python
socket connections are blocked. This is not an OS network-namespace isolation
test. Each completed step saves adapter, optimizer, scheduler, RNG, ordered
sample indices and hash-sealed state. Use `--session-steps 2` to stop after two
steps of a `--steps 4` experiment; resume with `--resume /private/run/checkpoint-2`
and a NEW `--output` directory, preserving all other arguments. Runner/config,
data, model and runtime identities must match. Earlier runner checkpoints are
not silently migrated. `--skip-evaluation` runs mechanics only and emits null
quality scores; use it consistently in both sessions.

Real CPU Qwen3 validation on 2026-10-26 compared uninterrupted four steps with
two steps plus a fresh-process two-step resume: adapter, optimizer, scheduler,
RNG and loss/sample-order states were exactly equal. See the dated research
report. This is not GPU/cross-hardware equivalence or a quality improvement.

Keep weights and optimizer files private/outside Git. Retain the final checkpoint
in durable private storage before relying on it across sessions. This short
experiment is not an unattended long training job or an official RAINY release.
Reload and compare all predictions in a fresh process:

```bash
python scripts/verify_synthetic_adapter.py --model /private/models/qwen3-0.6b \
  --run /private/experiments/new-run --evaluation evaluation/mn_smoke.jsonl --step 16
```

The verifier validates checkpoint seals and model/tokenizer hashes (excluding
machine-specific Hub `.cache` bookkeeping). This verifies inference reload,
not optimizer resume equivalence.

Only small predictions, configuration, hashes and measured summaries belong in
the public repository. Decreasing training loss alone is not language-quality
improvement. A zero or negative score delta must be reported unchanged.

Монгол: Энэ нь бодит модель дээрх богино CPU LoRA туршилт. Хиймэл 32 жишээ нь
хүний хянасан Монгол corpus биш. Өмнөх/дараах оноо, loss, хугацаа, санах ойг
тусад нь тайлагнана. Бүх чадвар сайжирсан, эсвэл RAINY release бэлэн болсон
гэж дүгнэхгүй. Үндсэн сургалтын хүний review хамгаалалт хэвээр.
