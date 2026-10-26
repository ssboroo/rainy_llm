# Fresh transfer diagnostic — 2026-10-26

`mn_transfer_draft_20261026.jsonl` contains 12 AI-authored technical diagnostic
cases, two each for arithmetic, extraction, translation, transliteration,
instruction following and reasoning. Human review is **pending**. These are not
collected real sources, a representative benchmark or an approved release gate.
Original project ownership applies; no third-party text was copied.

The file was fixed before the seed-42 attempt, with SHA-256
`a13b3e9879547ae42b1cb84d62d85f961a67b9d091c18d1443baa7fa004828ae`.
No training fixture, learning rate, answer key or prompt is tuned after viewing
these results. Existing 24-case/v2 files and frozen source assignments are unchanged.
The initial attempt did not retain a complete before/after report; seed 43 has
not run. Do not interpret this file or the overlap report as completed evaluation.
No exact prompt overlap with the 32 synthetic training fixtures; the existing
character-trigram Jaccard audit at threshold 0.50 finds no candidate pairs.
This lexical check is not semantic or pretrained-data contamination detection.
Arithmetic is related to the training skill; do not call all categories out-of-domain.

Normalized exact-match uses the existing scorer, including its limitations:
valid verbose answers can fail a requested terse format. Inspect raw outputs,
token-limit hits and per-category counts, not only the aggregate. Two seeds and
two examples per category do not establish statistical significance or broad
Mongolian improvement. Once public and measured, this is a development diagnostic,
not an untouched private test set.

Run each seed in a fresh process (CPU float32, 4 threads, greedy 32-token cap):

```sh
python scripts/synthetic_lora_experiment.py --model /private/pinned-qwen3 \
  --evaluation evaluation/mn_transfer_draft_20261026.jsonl \
  --output /private/transfer-seed42 --steps 16 --seed 42
python scripts/synthetic_lora_experiment.py --model /private/pinned-qwen3 \
  --evaluation evaluation/mn_transfer_draft_20261026.jsonl \
  --output /private/transfer-seed43 --steps 16 --seed 43
```

Install the experiment's pinned runtime separately. Outputs must be outside Git;
never publish checkpoint weights here. Seed is included in run identity and a
different seed cannot resume an existing sealed run. The changed runner hash
also intentionally prevents resuming older-code checkpoints without migration.
