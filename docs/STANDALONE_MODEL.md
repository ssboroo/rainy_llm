# RAINY standalone Mongolian model / Бие даасан Монгол загвар

Owner direction, 2026-10-13: the core deliverable is a locally runnable, general-purpose Mongolian language model with a versioned weight artifact. Document search, voice and business tools are optional integrations. This supersedes business-document-assistant-first prioritization in PRODUCT_DIRECTION.md.

## What standalone means
After installation and licensed artifact acquisition, inference must work with outbound networking disabled, without API keys, a provider account, remote tokenizers or cloud retrieval. CPU/GPU hardware and a compatible runtime are still required. Local files may be copied from another computer. Offline knowledge is limited to training data and any explicitly supplied local context.

Start with a licensed pretrained open-weight model, adapt it to Mongolian and retain its upstream attribution. This yields a RAINY adaptation, not an independently pretrained foundation model. Training a foundation model from scratch is a separate compute/data undertaking and is not claimed here. No model can guarantee correct answers for every task.

## Model-first milestones
1. Compare resource-feasible pinned bases on language, instruction following, summarization, translation, reasoning, arithmetic, coding, structured output and uncertainty; preserve general abilities as well as Mongolian quality.
2. Build a licensed, reviewed Mongolian corpus and instruction dataset with source-separated train/validation/test splits. The current format example and unreviewed pilot are insufficient. Preserve eval exclusion, data rights and privacy checks.
3. Implement and validate a reproducible SFT LoRA/QLoRA pipeline. Record exact model/tokenizer/runtime revisions, seed, data hashes, hardware, loss and before/after held-out results. No paid GPU job without budget authorization.
4. Test merged or base-plus-adapter offline export, then quantized GGUF against the unquantized reference. A PEFT adapter alone does not contain the base weights. Compatibility and redistribution licenses must be checked before merging/export.
5. Release a versioned model card, artifact checksums, runtime lock, local chat/API and installation instructions only after actual inference, regression and offline-egress tests. No weights in this Git repository.

## First offline entry point (experimental)
`scripts/ask_offline.py` accepts a local GGUF path and a trusted expected SHA-256; checks integrity before runtime import; requires an embedded chat template to avoid an implicit llama-2 fallback. No Hub download call or external API is used. It runs CPU text generation and prints either one JSON response or newline-delimited JSON (NDJSON) events with `--stream`; no conversation is saved automatically.

```bash
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --check-only
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --prompt "Монгол хэлээр өөрийгөө товч танилцуул."
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --prompt "Монгол хэлээр өөрийгөө товч танилцуул." --stream
```

The backend is llama-cpp-python (previous experiments used 0.3.36); this new entry point has **not been validated with real weights**. Install a compatible reviewed runtime separately; do not interpret a version mention as a tested dependency lock. Backend context errors are reported, not silently truncated. Embedded-template presence does not establish template correctness for every architecture; validate each pinned artifact. `--check-only` checks bytes/header only, not model compatibility. Keep the file unchanged between verification and loading.

The current execution environment lacks `llama_cpp`; the unit tests use synthetic bytes and a mock backend. They verify integrity rejection, local-path wiring, stream event/NDJSON shape and template refusal/cleanup, not inference, offline networking behavior or model quality. The project still has no trained RAINY weights.

## Official references checked 2026-10-13
- https://llama-cpp-python.readthedocs.io/en/latest/ — local model_path and chat-template precedence.
- https://huggingface.co/docs/trl/v0.27.0/en/sft_trainer — SFT training interfaces, reference only; no training executed.
- https://huggingface.co/docs/peft/en/developer_guides/checkpoint — adapter vs full-model checkpoints and merge limitations.
