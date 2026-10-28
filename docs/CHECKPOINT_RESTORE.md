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
