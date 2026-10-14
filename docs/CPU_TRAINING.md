# Incremental free CPU LoRA / Үнэгүй CPU LoRA

**Experimental code, not a validated training environment.** The runner's five stdlib guard tests pass. No PyTorch/Transformers/PEFT training, trained adapter, measured loss or Mongolian improvement has been produced by this runner. QLoRA/GPU/distributed training are not implemented. Owner: ssboroo; upstream models, libraries and data retain their own licenses.

## Inputs and review
Use a small, reviewed, licensed local causal model snapshot with `config.json`, safetensors weights, tokenizer and an explicit chat template. Materialize Hub symlinks first. No automatic download, remote code, provider API or telemetry is enabled. This is not an OS-level network sandbox. All inputs must remain unchanged while running.

The dataset uses the repository instruction schema, containing **only train records**. Provide a separate evaluation JSONL; exact prompt overlap is rejected, but semantic contamination requires the existing overlap audit and human review. All records' source/license pairs must appear in a separate local review attestation:

```json
{
  "data_sha256": "REPLACE_WITH_THE_REVIEWED_FILE_SHA256",
  "reviewer_role": "human-reviewer",
  "reviewer": "ACTUAL_REVIEWER_REFERENCE",
  "quality_reviewed": true,
  "privacy_reviewed": true,
  "training_rights_verified": true,
  "approved_source_licenses": [
    {"source": "EXACT_DATA_SOURCE", "license": "VERIFIED_LICENSE"}
  ]
}
```

This is a format illustration, **not approval of any current data**. Do not copy it to falsely approve a dataset. Attestation structure does not authenticate the reviewer; review evidence and identity belong in the owner's review process. Keep identifying/private review details outside the public repo. The one format example and unreviewed Wikipedia pilot are insufficient for a quality run.

## Small sessions and recovery
Install a compatible, reviewed PyTorch/Transformers/PEFT/Accelerate environment separately. No training dependency lock is claimed yet. PEFT v0.21.2 was researched but not installed/tested; blindly mixing it with the old inference lock is unsupported. Runtime versions, script hash, model file hashes, data/review/eval hashes and training settings are recorded and must match on resume.

```bash
python scripts/train_lora_cpu.py \
  --model /private/models/pinned-small-model \
  --data /private/corpus/train.jsonl \
  --evaluation evaluation/mn_v2_draft.jsonl \
  --review /private/corpus/review.json \
  --output /private/persistent/rainy-run-001 \
  --total-steps 20 --session-steps 2 --seconds 120 \
  --max-length 256 --threads 2 --persistent-storage-confirmed
```

Run the same command with `--resume /private/persistent/rainy-run-001/checkpoint-2` to continue. Keep `--total-steps` fixed: it is the whole experiment's target, not additional steps. The session/time budgets may change. `--persistent-storage-confirmed` is the operator's attestation of durable storage, not a durability test. Do not set it for transient scratch. Output paths inside any Git checkout are rejected. Never commit checkpoints or weights.

The runner uses float32 CPU LoRA, rank 8, alpha 16, all-linear targets, AdamW, constant LR 1e-4, one sequence per batch, no dropout, seed 42. Prompt labels are masked. Templates whose generation prefix differs from the full conversation are rejected; sequences over the length limit are rejected instead of truncating answers. Architecture/template support is conditional, not universal.

Trainer is configured to save the adapter, optimizer, scheduler, RNG and trainer state every step and retain two checkpoints. After `on_save`, the runner writes `rainy-checkpoint.json`: all regular component file sizes/SHA-256 values, the step and run-identity hash. The marker is flushed/fsynced and atomically renamed only after inventory completion. Resume recomputes the inventory before loading tensors; missing, changed, extra, empty or symlinked components, missing seals, incomplete-save markers and directory/state step mismatches are rejected. Model-only adapters are insufficient.

Use one writer per run and immutable checkpoint files during verification/loading. This detects accidental corruption, not malicious replacement of both data and manifest; it is not a signature or a pickle security sandbox. Only load your own trusted checkpoints. Filesystem atomic rename does not prove remote-storage or power-loss durability. A leftover `.tmp` or absent marker means the save is not established as complete; choose a previously sealed checkpoint, do not fabricate a seal. Old unsealed checkpoints are not auto-migrated. Cross-version/hardware numerical equivalence remains untested; the runner hash changes with this update, so previous identities are intentionally incompatible.

2026-10-14: seven filesystem fault tests exercise successful sealing, every required component's modification/deletion, empty/unsealed files, extra files/modified markers, invalid steps, symlinks and interrupted marker publication while preserving a previous checkpoint. These are synthetic byte fixtures, not trained tensors. The `on_save` integration and real resumed optimizer execution still require a compatible training runtime.

Session/time limits are checked **between optimizer steps**, not during model loading, backward or checkpoint I/O. A slow step may exceed the time budget. An OOM/kill can lose the current step; use the last fully saved checkpoint, never an incomplete directory. This runner does not provide an OS resource cap or guarantee OOM recovery. Use a suitable external process/container memory/time limit after measuring the smallest smoke run. Model memory and disk requirements must be checked before loading; LoRA does not remove frozen base-weight/activation memory.

## Current verification and next gate
2026-10-13: environment has an 8 GiB cgroup memory cap, CPU quota of eight cores, no installed training stack, and approximately 28 GiB free scratch disk. The configured package index returned no matching Torch distribution. Durable private checkpoint storage was not established for this run. No weights were downloaded and no paid service was started.

Before calling the runner operational: select/pin a feasible small model and compatible dependency lock, obtain reviewed data, verify durable storage, run a 2-step smoke, resume to 4 steps and compare against uninterrupted 4-step training on identical inputs. Record actual parameter counts, losses, elapsed time, RSS and checkpoint hashes, then separately run before/after held-out generation. Loss reduction is not a quality claim.

Монгол: Код нь бага алхмын CPU LoRA сургалт ба checkpoint-оос үргэлжлүүлэхэд зориулагдсан. Одоогоор зөвхөн өгөгдлийн review, template masking, model hash, output байрлал, resume төлөвийн хамгаалалтын тест ажилласан. Бодит сургалт, loss, Монгол чанарын ахиц хэмжээгүй. Хүний хянасан өгөгдөл, тохирох runtime, тогтвортой checkpoint хадгалалт баталгаажсаны дараа богино сургалт/сэргээх туршилт хийнэ.

## Official references checked 2026-10-13
- https://huggingface.co/docs/transformers/main_classes/trainer — CPU training, save_only_model and checkpoint resume contracts.
- https://github.com/huggingface/peft/releases/tag/v0.21.2 — 2026-10-01 encoder-decoder/Transformers >=5.18.0 compatibility fix; not a measured RAINY gain.
- https://huggingface.co/docs/peft/en/developer_guides/checkpoint — adapter serialization is separate from base weights and full optimizer state.
