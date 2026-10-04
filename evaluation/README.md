# Mongolian held-out evaluation / Монгол тусгаарласан үнэлгээ

`mn_smoke.jsonl` currently contains **24 project-authored draft cases**. They are not human-reviewed and must not be described as a released benchmark. Never include this directory in pretraining, SFT, preference data, retrieval corpora, prompt-generation examples, or few-shot demonstrations used to tune a model.

## Validation

```bash
python scripts/validate_evaluation.py --training data/examples.jsonl
python scripts/validate_evaluation.py --release --min-cases 100
```

The first command validates structure, normalized prompt uniqueness and exact overlap against supplied training JSONL. Repeat `--training` for every training file. The second is intentionally expected to fail today: release mode requires at least 100 cases and every row must have `review_status: human-reviewed`.

The validator reports a SHA-256 of the exact evaluation file. Store that hash with every experiment. Exact normalized matching is only a first guard; it does not detect paraphrases, translations, semantic overlap, or contamination already present in a pretrained base model.

## Human review protocol

Two separate roles are recommended: an author and a reviewer. A reviewer checks Mongolian wording, answer completeness, ambiguity, category, source independence, safety, and whether a short exact-match answer is appropriate. Change `review_status` only after actual human review. Keep revisions in Git; do not add reviewer personal information.

Freeze a version before comparing models. Use identical case hash, prompt template, chat template, decoding budget and answer normalization. Report exact-match as a format-sensitive smoke metric alongside latency, generated tokens and qualitative/human assessment—not as complete Mongolian capability.
