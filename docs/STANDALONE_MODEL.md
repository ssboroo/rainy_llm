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
`scripts/ask_offline.py` accepts a local GGUF path and a trusted expected SHA-256; checks integrity before runtime import; requires an embedded chat template to avoid an implicit llama-2 fallback. No Hub download call or external API is used. It runs CPU text generation and prints either one JSON response or newline-delimited JSON (NDJSON) events with single-prompt `--stream`. Single-turn JSON and NDJSON streaming both use the loaded runtime tokenizer to estimate the current prompt and refuse generation when it exceeds the context left after the output budget and a conservative 64–256-token template reserve. The result includes the estimate and safe input budget. The `--chat` mode keeps one model process open across turns, bounds history to 1–64 turns (default 8) and a tokenizer-estimated prior-history budget (`--max-history-tokens`, default 1024), streams plain text with `--stream`, and supports `/help`, `/clear` and `/exit`. It retains the newest complete user/assistant pairs first. An overlong current prompt is refused before generation. Token estimates count each message with a small fixed overhead and reserve 64–256 context tokens for chat-template/control overhead; they are conservative estimates, not an exact rendered-template count. Conversation history remains in RAM only and is not persisted.

```bash
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --check-only
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --prompt "Монгол хэлээр өөрийгөө товч танилцуул."
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --prompt "Монгол хэлээр өөрийгөө товч танилцуул." --stream
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --chat --stream --max-history-turns 8 --max-history-tokens 1024
```

Single-prompt `--stream` emits NDJSON; in interactive `--chat --stream` mode, plain-text deltas are printed to the terminal. `--max-history-tokens` limits prior turns using the runtime tokenizer and a conservative per-message overhead; the current prompt has a separate context budget. The newest complete turns are retained first, and a current prompt that exceeds the safe input budget is refused without calling generation. This is an estimate because model-specific chat-template tokens vary; backend context errors are still surfaced rather than silently truncated. `/clear` removes the in-memory history and `/exit` ends the session. No conversation is written to disk.

The backend is llama-cpp-python (previous experiments used 0.3.36); this new entry point has **not been validated with real weights**. Install a compatible reviewed runtime separately; do not interpret a version mention as a tested dependency lock. Backend context errors are reported, not silently truncated. Embedded-template presence does not establish template correctness for every architecture; validate each pinned artifact. `--check-only` checks bytes/header only, not model compatibility. Keep the file unchanged between verification and loading.

The current execution environment lacks `llama_cpp`; the unit tests use synthetic bytes and a mock backend. They verify integrity rejection, local-path wiring, single-turn stream event/NDJSON shape, interactive turn/token budgets, newest-pair retention, overlong-prompt refusal, history clearing, streaming, cleanup and template refusal, not inference, offline networking behavior or model quality. The project still has no trained RAINY weights.

## Packaged safetensors inference runner (experimental)

scripts/ask_offline_bundle.py executes a bundle produced by scripts/export_offline_bundle.py. It supports a merged safetensors model or a base-plus-adapter layout. It requires a trusted expected bundle SHA-256, verifies the bundle manifest and all files, requires exact installed versions for every declared runtime pin, reads the explicit template from the verified bundle, uses local_files_only=True and trust_remote_code=False, and refuses to load if available RAM cannot be measured or is below a conservative threshold. Generation is greedy/deterministic with a bounded output budget; JSON reports model identity, runtime pins, prompt hash, token counts, latency, throughput and peak RSS when supported.

    python scripts/export_offline_bundle.py verify --bundle /private/rainy-bundle
    python scripts/ask_offline_bundle.py --bundle /private/rainy-bundle --expected-bundle-id TRUSTED_BUNDLE_SHA256 --prompt "Монгол хэлээр товч хариул."

The loader does not merge adapters, quantize, download files, or establish redistribution rights. The Python socket guard and Hugging Face offline flags are not a substitute for OS/container egress isolation. The current environment has no Transformers/PEFT packages or real bundle, so real safetensors inference remains unverified; mock tests are not a model-quality benchmark.

## Official references checked 2026-10-13
- https://llama-cpp-python.readthedocs.io/en/latest/ — local model_path and chat-template precedence.
- https://huggingface.co/docs/trl/v0.27.0/en/sft_trainer — SFT training interfaces, reference only; no training executed.
- https://huggingface.co/docs/peft/en/developer_guides/checkpoint — adapter vs full-model checkpoints and merge limitations.
