# Mongolian held-out evaluation / Монгол тусгаарласан үнэлгээ

`mn_smoke.jsonl` currently contains **24 project-authored draft cases**. They are not human-reviewed and must not be described as a released benchmark. Never include this directory in pretraining, SFT, preference data, retrieval corpora, prompt-generation examples, or few-shot demonstrations used to tune a model.

## Validation

```bash
python scripts/validate_evaluation.py --training data/examples.jsonl
python scripts/validate_evaluation.py --release --min-cases 100
```

The first command validates structure, normalized prompt uniqueness and exact overlap against supplied training JSONL. Repeat `--training` for every training file. The second is intentionally expected to fail today: release mode requires at least 100 cases and every row must have `review_status: human-reviewed`.

The validator reports a SHA-256 of the exact evaluation file. Store that hash with every experiment. Exact normalized matching is only a first guard; it does not detect paraphrases, translations, semantic overlap, or contamination already present in a pretrained base model.

Run the separate fuzzy audit against every proposed training file before freezing a release:

```bash
python scripts/audit_evaluation_overlap.py \
  --training data/examples.jsonl \
  --threshold 0.75 --ngram 3 \
  --output evaluation/overlap-audit.json
```

The report uses normalized character n-gram Jaccard similarity and stores only evaluation case IDs, training file indexes, row numbers and scores—not prompt text. Repeat `--training` for multiple files. Use `--fail-on-match` in a release pipeline after a project threshold is chosen. The default one-million-pair limit fails closed instead of silently sampling a large corpus; shard or pre-filter large corpora and record every shard hash. Every candidate requires human review. This lexical heuristic can miss translations and semantic paraphrases and cannot detect contamination inside pretrained model weights.

## Human review protocol

Two separate roles are recommended: an author and a reviewer. A reviewer checks Mongolian wording, answer completeness, ambiguity, category, source independence, safety, and whether a short exact-match answer is appropriate. Change `review_status` only after actual human review. Keep revisions in Git; do not add reviewer personal information.

Create a review packet without changing the source cases:

```bash
python scripts/review_evaluation.py export \
  --cases evaluation/mn_smoke.jsonl --output review-packet.jsonl
```

The reviewer changes every required check to `true` and the decision to `accept`, or leaves/rejects cases that need revision. After an actual human finishes the packet, apply it to a **new** output file:

```bash
python scripts/review_evaluation.py apply \
  --cases evaluation/mn_smoke.jsonl --reviews review-packet.jsonl \
  --reviewed-at YYYY-MM-DD --reviewer-role independent-human-reviewer \
  --output evaluation/mn_reviewed_candidate.jsonl
```

Each review is bound to the exact ID, category, prompt, answers and source with SHA-256. Applying a stale packet, missing/rejected case, incomplete checklist or unknown case fails. Output files are created exclusively and never silently overwritten. `human-reviewed` rows without matching review evidence fail validation. The role is generic by design; do not put a reviewer's name, email or other personal information in the public dataset.

Freeze a version before comparing models. Use identical case hash, prompt template, chat template, decoding budget and answer normalization. Report exact-match as a format-sensitive smoke metric alongside latency, generated tokens and qualitative/human assessment—not as complete Mongolian capability.
