# Synthetic checkpoint restoration / Checkpoint сэргээх

`scripts/restore_synthetic_checkpoint.py` restores an already authorized local
archive into a new private directory outside every Git checkout. It requires a
trusted SHA-256 acquired separately from the archive, rejects unsafe tar paths,
links, special files, duplicates and oversized archives (128 MiB / 64 members),
and verifies each checkpoint's existing identity-bound seal. It never loads
optimizer/RNG pickle objects, downloads a model, or approves training data.

```bash
python scripts/restore_synthetic_checkpoint.py \
  --archive /private/rainy-transfer-seed42-20261027.tar.gz \
  --sha256 2c0b61ef66ca3eeaf12b59d073e33c9118c62f91aaef1e2586aa098a329b04a1 \
  --destination /private/restored-seed42
```

The parent directory must exist and be private/single-writer. The destination
must not exist. Successful restore publishes `run/` and `restore.json`; a failed
attempt may retain `.staging/` and `RESTORE_INCOMPLETE` for diagnosis. Never load
an incomplete directory or remove its marker to bypass verification. Retry with
a new destination. Files are copied with private permissions, not archive modes.
Keep the original durable archive; the restored working directory is not a backup.

Then, **with the separately acquired exact base snapshot and pinned runtime**:

```bash
python scripts/verify_synthetic_adapter.py --model /private/qwen3-0.6b \
  --run /private/restored-seed42/run --step 16 \
  --evaluation evaluation/mn_transfer_draft_20261026.jsonl
```

Use the evaluation path matching the retained identity hash. Restore success establishes byte/identity
integrity, not tensor compatibility, inference equivalence, resume equivalence,
OS-level network isolation or general Mongolian quality. The archive contains
an adapter, not the base model. Existing RSS guards must not be bypassed.

2026-10-28: the actual retained seed42 archive restored 13 files / 7,023,160 bytes,
including the sealed step16 checkpoint. No pickle deserialization or inference
was performed. Unit tests include corrupted checkpoint, wrong archive hash,
path traversal, duplicate members, links, limits, Git-output and overwrite refusal.

Монгол: хадгалсан архивыг hash-аар шалгаж, Git-ээс гадуур шинэ хавтаст сэргээнэ.
Энэ нь дахин сургалт эсвэл чанарын ахиц биш. Base weights ба runtime-ийг тусад нь
бэлтгэж байж бодит inference reload туршина; review gate өөрчлөгдөхгүй.

## Measured fresh-process reload (2026-10-28)

After archive restoration, run `scripts/verify_synthetic_adapter.py` with
`--model`, `--run`, `--evaluation`, `--step 16` and optional `--report NEW.json`.
The report refuses overwrite and records outputs, per-case latency, runtime,
evaluation/identity hashes and process peak RSS. Linux RSS units are KiB.
The retained seed42 checkpoint matched all 12 saved predictions in 27.7639s,
peak RSS 4,822,560 KiB. See `research/results/2026-10-28-restore/reload.json`.
This checks inference reproducibility, not optimizer resume or quality gains.
HF offline flags and Python socket guards do not certify OS-level isolation.


## Safe legacy RNG-state restoration (2026-10-30)

The retained 2026-10-25 step-16 archive stores NumPy MT19937 keys as a
`uint32` ndarray. On the current CPU runtime, a plain
`torch.load(..., weights_only=True)` rejected that historical file because
`numpy._core.multiarray._reconstruct` and NumPy dtype classes were not in the
default safe-global set. The resume helper now allowlists only the NumPy
ndarray/dtype/reconstruction symbols needed for this format, still uses
`weights_only=True`, then validates the exact Python, NumPy MT19937 and CPU
Torch RNG structures before restoring them. New checkpoints store NumPy keys
as primitive integers and do not require those NumPy globals. Unknown pickle
globals remain rejected; there is no `weights_only=False` fallback.

The inspected archive SHA-256 was
`e9036fdea2892609ae73785c64ae9a6887df3df23e760dffe0a464e3c5194063`.
The legacy RNG payload loaded successfully in an isolated CPU probe, while a
custom untrusted pickle global was rejected. This compatibility fix does not
complete a real Trainer resume: the archive contains the adapter/optimizer/
scheduler/RNG state but not the base model weights. Exact uninterrupted versus
resumed equivalence remains pending until the same pinned base snapshot and
runtime are available.


## Base snapshot fingerprint audit (2026-10-30)

The retained private step-16 archive \`rainy-qwen3-lora-smoke-20261025.tar.gz\` was inspected without loading its optimizer/RNG pickle files. Archive SHA-256: \`e9036fdea2892609ae73785c64ae9a6887df3df23e760dffe0a464e3c5194063\`; size: 6,552,224 bytes. All seven files listed by the step-16 checkpoint seal matched their recorded byte sizes and SHA-256 values.

Although the archived \`identity.json\` has null \`model_id\` and \`model_revision\` fields, its base-model file inventory records:

- \`model.safetensors\`: \`f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b\`, which matches the official Hugging Face file SHA-256 for [Qwen/Qwen3-0.6B at revision c1899de289a04d12100db370d81485cdf75e47ca](https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors).
- \`config.json\`: \`660db3b73d788119c04535e48cf9be5f55bc3100841a718637ae695b442f27dd\`, matching the 726-byte official config at the same immutable revision.

This independently identifies the archived adapter's base snapshot as \`Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca\`. The archive still does **not** contain the 1.5 GB base weights; it contains the adapter, optimizer, scheduler, RNG, identity, file hashes and synthetic evaluation outputs. The adapter config's local path and null revision are not sufficient on their own; the recorded base weight hash is the matching evidence.

Provenance gap for future runs: the training identity itself should explicitly record model ID, immutable revision, tokenizer/template hashes and license fields rather than relying only on a local file-hash map. Do not change the legacy identity or claim the old archive had explicit model ID/revision fields. Actual resume still needs the same base bytes reacquired and the archive's pinned training runtime (Torch 2.6.0, Transformers 4.51.3, PEFT 0.15.2, Accelerate 1.6.0); the current host lacks those packages and no base weights were downloaded.
