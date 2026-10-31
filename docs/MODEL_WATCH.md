## 2026-10-31 08:56 — official Gemma QAT GGUF and runtime release recheck

### Resource-feasible candidate to verify (watch-only)

- Exact model ID: `google/gemma-4-E2B-it-qat-q4_0-gguf`.
- Upstream family release: Gemma 4 E2B/E4B/31B/26B A4B was released **2026-03-31**; the official QAT Q4_0 GGUF repository's validated GGUF upload is dated **2026-07-17**.
- Immutable Hugging Face repository revision: `675cff42a74c774d6cb76f76d8eacb49b48c9b93`.
- Weights license: **Apache-2.0** as declared by the official model repository. This is downloadable open-weight, not evidence that all pretraining data/recipe are fully open-source. No separate executable code is shipped in the GGUF repository; the llama.cpp runtime has its own MIT license.
- GGUF contains tokenizer/chat-template metadata; the repository does not provide a separate tokenizer package version in the inspected card. The text model file `gemma-4-E2B_q4_0-it.gguf` is **3.35 GB**; the optional multimodal projector `gemma-4-E2B-it-mmproj.gguf` is **987 MB**. Text-only CLI testing does not require the projector.
- Runtime: official model card provides llama.cpp CLI/server instructions and the GGUF is tagged for llama.cpp. The exact runtime build used for a RAINY test remains unpinned/unverified.
- Resource note: this host has 5.81 GiB total RAM and 4.7 GiB available at preflight. A 3.35 GB file alone does not establish that model + KV cache + runtime will fit. No download, load, inference or peak-RSS measurement was possible here; keep watch-only.
- Do not confuse the official Q4_0 artifact with the separate llama.cpp b12008 CPU memory note below: that upstream measurement is for **Q4_K_M** and cannot be transferred to this Q4_0 file.

### Runtime and training libraries

- `llama.cpp` **b12008**, published 2026-10-30 14:06 UTC (22:06 Ulaanbaatar), immutable commit `344846b4fc6fff5988f215e7cf839f880d04decf`: fixes tied `token_embd` creation order; upstream reports Gemma 4 E2B-it Q4_K_M CPU model buffer (no mmap) reduced from 3163.73 MiB to 2947.73 MiB. This is an upstream memory result for that Q4_K_M configuration, not a RAINY measurement.
- Latest `llama.cpp` **b12017**, published 2026-10-30 20:19:54 UTC (2026-10-31 04:19:54 Ulaanbaatar), immutable commit `5047748f114564fcf271e6a648f60e2d2eae6264`: removes an RPC path helper; no model-quality or relevant memory change.
- `Transformers v5.22.1`, published 2026-10-30 09:36:03 UTC, commit `446a570e62b04a89ea001604ada7366baac2ea67`, remains a documentation-only patch.
- `PEFT v0.21.2` (2026-10-01, commit `eaa35c777c7ba554a2a3639ac9c79bb690f39a57`) remains the latest inspected PEFT release.
- `TRL v1.17.1`, published 2026-10-30 14:15:28 UTC (22:15:28 Ulaanbaatar), tag object `eee64790d58f2d560cc7219c7e6d9e8b8922c83b`, commit `44809ba3f3a136f3d62859ee981fee2506bce5c9`: a narrow LFM2.5 tool-call parenthesis fix; no relevant SFT/LoRA capability change. TRL v1.17.0's Mistral Large 4 recipe still requires Transformers >=5.22.0, PEFT >=0.21.0 and Accelerate >=1.15.0 and reports ~142 GiB/GPU on 8×B300, outside this host budget.

Decision: keep `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` as rollback baseline. Gemma 4 QAT Q4_0 is a candidate for a later same-hash Mongolian CPU comparison, not a promoted base. No dependency pins changed.

Sources:
- [Gemma family release dates](https://ai.google.dev/gemma/docs/releases)
- [Official Gemma 4 QAT Q4_0 GGUF](https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf/tree/675cff42a74c774d6cb76f76d8eacb49b48c9b93)
- [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [llama.cpp b12008 release](https://github.com/ggml-org/llama.cpp/releases/tag/b12008)
- [llama.cpp b12017 release](https://github.com/ggml-org/llama.cpp/releases/tag/b12017)
- [Transformers v5.22.1](https://github.com/huggingface/transformers/releases/tag/v5.22.1)
- [PEFT v0.21.2](https://github.com/huggingface/peft/releases/tag/v0.21.2)
- [TRL v1.17.1](https://github.com/huggingface/trl/releases/tag/v1.17.1)
- [llama-cpp-python tokenizer API](https://llama-cpp-python.readthedocs.io/en/latest/api-reference/)

## 2026-10-30 20:57 — latest runtime release recheck

### Transformers v5.22.1
- Official patch release published **2026-10-30 09:36:03 UTC (17:36:03 Ulaanbaatar)**; immutable commit `446a570e62b04a89ea001604ada7366baac2ea67`.
- Release notes say the change is documentation-only: remove the WIP ML4 document. It adds no relevant Qwen CPU, GGUF, LoRA or QLoRA capability. Keep the tested RAINY training pin unchanged.

### llama.cpp b12005
- Official release published **2026-10-30 12:45:08 UTC (20:45:08 Ulaanbaatar)**; immutable commit `e0f142d5ddc1461ce721644d92af33db23545105`.
- Adds initial OpenCL q2_0 kernels/optimizations for Adreno. This is relevant to a future Android/Qualcomm low-bit deployment, not the current x86 CPU-only host; it does not provide a new Qwen3-0.6B artifact or establish compatibility with the project's unpinned llama-cpp-python runtime.
- PEFT v0.21.2 (2026-10-01) and TRL v1.17.0 (2026-10-29) remain the latest inspected releases; their newer features do not fit the current CPU-only Qwen training stack.

Decision: no model/runtime pin change. The 5.8 GiB host has no Adreno/OpenCL target, no `llama_cpp` package and no GGUF weights. No inference, quantization or training was attempted. No newer resource-feasible Qwen/Gemma/DeepSeek/Meta/Mistral model with a verified same-hash Mongolian advantage was established.

Sources: [Transformers v5.22.1 release](https://github.com/huggingface/transformers/releases/tag/v5.22.1), [Transformers commit](https://github.com/huggingface/transformers/commit/446a570e62b04a89ea001604ada7366baac2ea67), [llama.cpp b12005 release](https://github.com/ggml-org/llama.cpp/releases/tag/b12005), [llama.cpp commit](https://github.com/ggml-org/llama.cpp/commit/e0f142d5ddc1461ce721644d92af33db23545105).

## 2026-10-30 16:56 — official model and runtime recheck

### Meta Muse Glimmer 30B
- Exact ID: `meta-models/Muse-Glimmer-30B`; official research publication 2026-10-19; paper [Muse Glimmer 30B](https://ai.meta.com/research/publications/muse-glimmer-30b-an-on-device-agentic-model/), arXiv 2610.24628.
- Inspected immutable snapshot `cec94fcfd6512f2cfe708138c32533b346ea4f69`; Apache-2.0 artifacts; tokenizer.json, tokenizer_config.json and chat_template.jinja present; Transformers metadata uses AutoModelForMultimodalLM + AutoProcessor. BF16 metadata reports 29,776,626,688 parameters. Official card lists 4-bit artifacts for 24/32GB hardware. Open-weight with Apache-licensed artifacts; not proof of open pretraining data. Not feasible on 5.8GiB host; no download/inference.

### Meta Muse Spark Open 816B
- Exact ID: `meta-models/Muse-Spark-Open-816B-A42B`; model-card release date 2026-10-15; inspected snapshot `0fb02478b02565b2ce7fc57e6051c91172774ac9`.
- Separate Muse Model License (`license:other`), manually gated; not OSI open-source. Requires visible “Built with Muse Spark Open” notice and separate Model-as-a-Service agreement above stated revenue threshold. Tokenizer and chat_template.jinja exist; 65 BF16 shards, 822,036,529,664 bytes tensor data. No access requested/download/inference.

### DeepSeek-V4.1-Flash-1017
- Exact ID: `deepseek-ai/DeepSeek-V4.1-Flash-1017`; official update 2026-10-17; card states MIT for repo and weights, 763B parameters, Transformers/vLLM/SGLang examples. Classify as downloadable open-weight; the card does not establish fully open pretraining data/recipe.
- Exact immutable revision SHA not captured; do not invent or use main as pin. No Jinja chat template: official card points to `encoding/` and `deepseek-recipe`. `deepseek-flash` is hosted API alias, distinct from downloadable weights. Far beyond host memory.

### Qwen, Google/Gemma, Mistral
- Qwen cloud changelog: `qwen3.8-flash` and `qwen-audio-3.1-realtime-flash` expanded to EU/HK API regions on 2026-10-27; API-only, not verified local weight IDs.
- Google exact model IDs and inspected revisions:
  - `google/embeddinggemma-2` — official release **2026-10-06**; inspected file snapshot `c3f2237ce16fe33d1bb9dab8692c29c79865bdeb`; Apache-2.0; 740M multimodal embedding encoder, 1.49 GB safetensors file, feature-extraction/AutoModel + AutoProcessor; no chat template or text-generation interface. It may be relevant to a future retrieval integration, but Mongolian retrieval quality was not tested.
  - `google/gemma-4-E2B-it` — smallest Gemma 4 instruction checkpoint; official family release **2026-03-31**; inspected snapshot `c3cdbdc9e7fd33008f19e1e1d8d46382b1349cac`; Apache-2.0; 2.3B effective / 5.1B total parameters (including embeddings); 10.2 GB BF16 safetensors. `tokenizer.json`, `tokenizer_config.json` and `chat_template.jinja` are present; Transformers example uses AutoProcessor + AutoModelForMultimodalLM (latest Transformers; exact minimum version not stated). The official repository has no quantized artifact in this scan. Full BF16 does not fit 5.8 GiB RAM; a future supported 4-bit conversion is a watch candidate only, not a measured result. No download/inference; Mongolian quality untested.
  - `google/gemma-4-12B-it` — Gemma 4 12B Unified instruction model, official family release **2026-06-03**; inspected snapshot `707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7`; Apache-2.0; 11,959,730,224 BF16 parameters; tokenizer.json, tokenizer_config.json and chat_template.jinja present; Transformers metadata uses AutoProcessor + AutoModelForMultimodalLM. BF16 requires far more than the 5.8 GiB host; no official quantized artifact was verified here. No download/inference.
  - These are not newer than the October Meta/DeepSeek updates above; no newer resource-feasible Gemma chat base was verified.
- Mistral Large 4 remains watch-only under its separate Mistral Ecosystem Open-Weight License and is too large.

### Runtime and training releases
- Transformers v5.22.0 (2026-10-29, commit `0f01f27e9c939328b69e9057bfa0d0b25544915b`) adds Mistral Large 4 and FP8 adapter-training backward support; upstream reports chunked expert dequant lowering one 8k-token FP8 backward peak 28.9→2.8 GiB. Not a RAINY measurement; do not replace tested 4.51.3 CPU pin.
- PEFT v0.21.2 (2026-10-01, commit `eaa35c777c7ba554a2a3639ac9c79bb690f39a57`) remains latest; fixes encoder-decoder compatibility with Transformers >=5.18.0.
- TRL v1.17.0 (2026-10-29, commit `e257382de9e046b8181a5d1f91586f9bce324126`) supports Mistral Large 4 SFT LoRA on 8×B300 (~142 GiB/GPU reported), requiring Transformers >=5.22.0, PEFT >=0.21.0, Accelerate >=1.15.0; not feasible here.
- llama.cpp b12001 (2026-10-30 07:41 UTC / 15:41 Ulaanbaatar, commit `eb4e244be77a906a183cd4a00fd51d9ad3200955`) adds RDNA4_M. b12000 adds OCP FP8 E4M3 conversion and Qwen3.8 NVFP4 fixes; no impact on current Qwen CPU path.

Decision: keep Qwen3-0.6B as rollback baseline. No candidate fits the 5.8GiB host with a verified compatible runtime and the same frozen Mongolian evaluation. No pin change, base promotion, download, training or inference.

Sources: [Muse Glimmer paper](https://ai.meta.com/research/publications/muse-glimmer-30b-an-on-device-agentic-model/), [Muse Glimmer card](https://huggingface.co/meta-models/Muse-Glimmer-30B/tree/cec94fcfd6512f2cfe708138c32533b346ea4f69), [Muse Spark metadata](https://huggingface.co/api/models/meta-models/Muse-Spark-Open-816B-A42B), [DeepSeek card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017), [DeepSeek release](https://api-docs.deepseek.com/news/news261017/), [Qwen changelog](https://docs.qwencloud.com/changelog/models), [Gemma releases](https://ai.google.dev/gemma/docs/releases), [Transformers v5.22.0](https://github.com/huggingface/transformers/releases/tag/v5.22.0), [PEFT v0.21.2](https://github.com/huggingface/peft/releases/tag/v0.21.2), [TRL v1.17.0](https://github.com/huggingface/trl/releases/tag/v1.17.0), [llama.cpp b12001](https://github.com/ggml-org/llama.cpp/releases/tag/b12001).

## 2026-10-30 13:25 — latest official Qwen3.8 release scan

### Qwen3.8-27B (open-weight; not resource-feasible here)

- Exact model ID: \`Qwen/Qwen3.8-27B\`.
- Official Qwen family release date: **2026-08-14**.
- Immutable inspected Hugging Face snapshot: \`72a217afab8029b39e4af1c7273a829995a3dbaf\` (a snapshot revision, not claimed to be the initial release commit).
- Model card license: **Apache-2.0**. Downloadable open weights and Apache-licensed repository files do not establish fully open training data or a fully reproducible open pretraining recipe; classify as open-weight, not fully open-source.
- Model card tags it as \`qwen3_5\` / Image-Text-to-Text and gives the local loading path \`AutoProcessor\` + \`AutoModelForMultimodalLM\`. The pinned snapshot contains \`tokenizer.json\` (12.8 MB), \`tokenizer_config.json\` (16.8 kB), \`vocab.json\`, \`merges.txt\` and \`chat_template.jinja\` (9.42 kB).
- The model repository is **55.6 GB** across 18 safetensors shards. This exceeds the current host's 5.81 GiB total RAM by a wide margin before runtime/cache overhead. It is not a candidate for local CPU inference or training here.
- Official model card lists Transformers, vLLM, SGLang and Docker Model Runner examples. It does not state a minimum stable Transformers version. The current RAINY Transformers 4.51.3 pin is not accepted as compatible without an isolated load test; no package upgrade or download was attempted.

### Qwen3.8-2.4T-A95B (separate license; not resource-feasible)

- Exact model ID: \`Qwen/Qwen3.8-2.4T-A95B\`; official Qwen family release date **2026-08-12**.
- Immutable inspected config snapshot: \`912e40d903bfc891be8fe3c51faa0a09d182ce95\`.
- Hugging Face metadata reports license \`qwen3.8-max\`, not Apache-2.0. Treat it as downloadable open-weight under a separate model license, not fully open-source; review the actual terms before any commercial use.
- The repository is sharded into 213 safetensors files; individual inspected shards are 17.2 GB. No total-RAM or local runtime benchmark was attempted because it is far beyond this host's budget.

### Decision

Qwen3.8 is the newest Qwen family release verified in this scan, but its 27B and 2.4T variants are not feasible on this host. Keep Qwen3-0.6B as the rollback baseline and Qwen3.5-0.8B as a smaller watch-only comparison candidate. Do not infer that a newer model is better for Mongolian; no Qwen3.8 weights were downloaded, no inference/training/evaluation was run, and no base was promoted.

### Official sources

- https://github.com/QwenLM/Qwen3.8 (release dates and official runtime matrix)
- https://huggingface.co/Qwen/Qwen3.8-27B/tree/72a217afab8029b39e4af1c7273a829995a3dbaf
- https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/blob/912e40d903bfc891be8fe3c51faa0a09d182ce95/config.json

## 2026-10-30 13:18 — retained Qwen3-0.6B archive fingerprint

- Private archive: `rainy-qwen3-lora-smoke-20261025.tar.gz`, 6,552,224 bytes, SHA-256 `e9036fdea2892609ae73785c64ae9a6887df3df23e760dffe0a464e3c5194063`. Its sealed step-16 checkpoint has seven required files; all seven byte counts and SHA-256 values matched `rainy-checkpoint.json`.
- The archive's `identity.json` records the base `model.safetensors` hash `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`. This exactly matches the official Hugging Face [Qwen/Qwen3-0.6B file](https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors) at immutable revision `c1899de289a04d12100db370d81485cdf75e47ca` (the Hub page reports the same SHA-256). The recorded `config.json` hash `660db3b73d788119c04535e48cf9be5f55bc3100841a718637ae695b442f27dd` also matches the official 726-byte config at that revision.
- Therefore the legacy adapter's base snapshot is identified as `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca`, even though its old `identity.json` and `adapter_config.json` have null revision fields and the adapter config contains only a local path. The archive contains no base weights, so this is a fingerprint match, not a restored model.
- Keep Qwen3-0.6B as the rollback baseline. Before any new training, improve future identity metadata to explicitly record model ID, immutable revision, tokenizer/template hashes and license; do not rewrite the old identity or pretend it already contained those fields.
- Official reference: https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors and https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/config.json

## 2026-10-30 13:04 — resource-feasible Qwen candidate and upstream runtime scan

### Candidate: Qwen3.5-0.8B (watch-only; no promotion)

- Exact model ID: `Qwen/Qwen3.5-0.8B`.
- Release date: **2026-03-02** — the official Qwen model-family repository lists the 0.8B release on this date.
- Immutable model snapshot inspected: `2b48083dfa97c3cbf0220cf1a5e6cffe0a511157`.
- Model repository reports **Apache-2.0**. This is an open-weight model with published model code, not evidence that all pretraining data is open or that every derivative/quantized artifact has the same provenance.
- Files at that revision include `tokenizer.json` (12.8 MB), `tokenizer_config.json`, and explicit `chat_template.jinja` (6.67 kB). The model card uses `AutoProcessor` + `AutoModelForMultimodalLM`; it is an image-text-to-text model, not a text-only checkpoint.
- `config.json`: `Qwen3_5ForConditionalGeneration`, `model_type=qwen3_5`, 24 layers, hidden size 1,024, hybrid linear/full attention, and `transformers_version=4.57.0.dev0`. This field is build metadata, not a guaranteed minimum stable runtime version. The model card does not specify a tested minimum stable Transformers version.
- Model repository size is about 1.77 GB, including a 1.75 GB safetensors weight file. This is a disk-size observation, not a peak-RAM measurement; activations, KV/cache state, processor and runtime add overhead. It may be a candidate for the current 5.81 GiB CPU host, but fit is unverified.
- Transformers' Qwen3.5 integration documentation says support was contributed on 2026-02-09. The Qwen3.5 architecture support was merged into `llama.cpp` in February 2026 (`models: support qwen3.5 series`, commit `fc0fe4004985d6749a7a05e250d161f9dbe41d65`); no compatible local GGUF artifact/runtime was acquired in this run.
- No dedicated technical report for this exact dense 0.8B checkpoint was identified. The Qwen3.5-Omni report (arXiv:2604.15804, 2026-04-17) describes a separate hundreds-of-billions-parameter Omni model and must not be cited as a report for this 0.8B checkpoint.
- Decision: retain Qwen3-0.6B as the existing baseline. Compare this candidate only after a compatible pinned runtime and legally acquired immutable weights are available, using the same frozen evaluation hash, decoding, CPU/thread settings and memory measurement. No download, inference, training, Mongolian score, latency or base promotion occurred in this run.

### Other official releases checked

- Google: the official release log dates EmbeddingGemma 2 (740M) to 2026-10-06; it is an embedding encoder, not a causal chat generator. Gemma 4 12B Unified is dated 2026-06-03; E2B/E4B and larger Gemma 4 variants are dated 2026-03-31. The inspected `google/gemma-4-E2B-it` repository snapshot is about 10.3 GB, above this host's total RAM before runtime overhead.
- DeepSeek: DeepSeek-V4.1-Flash remains an API service in the reviewed official material; no immutable local weight snapshot/license/runtime contract suitable for this host was verified. Treat it as API-only, not open-weight.
- Meta: no newer resource-feasible downloadable Llama candidate was verified; Llama 4 access/license requirements remain separate from open-source code.
- Mistral: `mistralai/Mistral-Large-4-1T-A52B` remains open-weight under the Mistral Ecosystem Open-Weight License, not fully open-source; its FP8 weights are about 1.06 TB and it is not feasible here.

### Training/inference library release notes

- Transformers **v5.22.0**, published 2026-10-29, commit `0f01f27e9c939328b69e9057bfa0d0b25544915b`: adds Mistral Large 4 support and related FP8 adapter-training changes. The project remains on its tested 4.51.3 pin; no broad runtime upgrade was made.
- PEFT **v0.21.2**, published 2026-10-01, commit `eaa35c777c7ba554a2a3639ac9c79bb690f39a57`: fixes encoder-decoder compatibility with Transformers >=5.18.0. No direct need to upgrade the current Qwen CPU stack was established.
- TRL **v1.17.0**, published 2026-10-29, commit `e257382de9e046b8181a5d1f91586f9bce324126`: includes Mistral Large 4 LoRA SFT on 8×B300, reporting about 142 GiB/GPU. This is not a resource-feasible Qwen CPU recipe.
- `llama.cpp` **b12000**, a pre-release published 2026-10-30 04:25 UTC (12:25 Ulaanbaatar), commit `68d20b884c3878217de79eade0a249efde96ab38`: adds OCP FP8 E4M3 conversion/runtime support and fixes Qwen3.8-27B-NVFP4 conversion paths. This is useful upstream quantization work but does not justify adopting an unpinned pre-release for the current 0.6B baseline.

### Sources

- https://github.com/QwenLM/Qwen3.8
- https://huggingface.co/Qwen/Qwen3.5-0.8B/tree/2b48083dfa97c3cbf0220cf1a5e6cffe0a511157
- https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/2b48083dfa97c3cbf0220cf1a5e6cffe0a511157/config.json
- https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/2b48083dfa97c3cbf0220cf1a5e6cffe0a511157/chat_template.jinja
- https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/qwen3_5.md
- https://github.com/ggml-org/llama.cpp/commit/fc0fe4004985d6749a7a05e250d161f9dbe41d65
- https://ai.google.dev/gemma/docs/releases
- https://huggingface.co/google/gemma-4-E2B-it
- https://github.com/huggingface/transformers/releases/tag/v5.22.0
- https://github.com/huggingface/peft/releases/tag/v0.21.2
- https://github.com/huggingface/trl/releases/tag/v1.17.0
- https://github.com/ggml-org/llama.cpp/releases/tag/b12000

# Шинэ загварын бүртгэл

## 2026-10-30 09:05 — Mistral Large 4 weights released; watch-only

- Release date: Hugging Face's official model announcement is dated **2026-10-29**. This supersedes the earlier 2026-10-29 pre-release check below; the weights are now downloadable.
- Exact FP8 model ID: `mistralai/Mistral-Large-4-1T-A52B`. The initial immutable model/weight release revision is `9bc535781e2938f0cc827614ba863070ccf44591`. The later current-main README-only snapshot observed during this check is `f12dabdc0c1e99e7f7924461a6f308859b05af4d`; use the initial release revision when pinning the original weight payload. Official NVFP4 model ID: `mistralai/Mistral-Large-4-1T-A52B-NVFP4`; its immutable revision was not independently pinned in this check.
- Distribution class: **open-weight, not fully open-source**. The official model repo's weights use the Mistral Ecosystem Open-Weight License (modified MIT). It permits use, modification and fine-tuning but requires a separate commercial license for a Model-as-a-Service business. Training data and a complete open training recipe are not released here. The model repo does not establish a separate model-specific code license; do not infer one from the weights license.
- Tokenizer/template: the pinned model repository includes `chat_template.jinja` and `config.json`. The official usage path uses `AutoProcessor.apply_chat_template`; an exact tokenizer package/version was not established in this review. Keep the template file/hash alongside any future artifact.
- Runtime: Hugging Face's official integration article documents Transformers support in **v5.22.0**, released 2026-10-29 at Transformers commit `0f01f27`; it also documents llama.cpp GGUF support. The official NVFP4 vLLM recipe uses 8-way tensor/decode-context parallelism and Blackwell GPUs. These are upstream compatibility statements, not local tests. Keep the current Qwen experiment pins (Transformers 4.51.3 / Torch 2.6.0+cpu / PEFT 0.15.2) unchanged until an isolated runtime test and same-hash Mongolian comparison exist.
- Resource: the official FP8 repo page reports about **1.06 TB** across 54 weight shards. The llama.cpp team's FP8-derived Q2_K GGUF is about **381 GB**; Unsloth lists 1-bit variants around 233 GB and 2-bit variants around 302–378 GB. The NVFP4 checkpoint is reported at about 619 GB and is intended for multi-GPU Blackwell serving. The current host has 5.81 GiB total RAM / 4.50 GiB available and cannot run this model.
- Training-library update: TRL **v1.17.0** was released 2026-10-29 at commit `e257382de9e046b8181a5d1f91586f9bce324126` (tag object `078b7e406068952f1f1886a1812f7a66555b3506`). It adds an `SFTTrainer` + PEFT LoRA example for this model, using assistant-only loss and packing, but the published run is on one **8×B300** node at about **142 GiB per GPU**. It requires Transformers ≥5.22.0, PEFT ≥0.21.0 and Accelerate ≥1.15.0. These are upstream example requirements and vendor-reported measurements, not an independently reproduced RAINY run. The current 5.81 GiB host and pinned CPU stack cannot use this recipe; no runtime pins changed. PEFT's latest release remains v0.21.2 (2026-10-01, commit eaa35c777c7ba554a2a3639ac9c79bb690f39a57).
- Research-paper check: no official Mistral Large 4 technical report/paper was identified in the reviewed official release/model-card sources. The TRL v1.17.0 notes include GRPO importance-sampling and precision changes, but those are not a reason to replace the current supervised-LoRA path without a matching experiment.
- Decision: watch only; no download, inference, fine-tuning, baseline change or quality claim. The API alias `mistral-large-4` is a hosted service identifier; it is distinct from the downloadable model IDs above.

Sources: [Hugging Face release post (2026-10-29)](https://huggingface.co/blog/mistral-large4), [official FP8 model at its initial immutable revision](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B/tree/9bc535781e2938f0cc827614ba863070ccf44591), [license at that revision](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B/blob/9bc535781e2938f0cc827614ba863070ccf44591/LICENSE), [chat template at that revision](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B/blob/9bc535781e2938f0cc827614ba863070ccf44591/chat_template.jinja), [Transformers v5.22.0 release](https://github.com/huggingface/transformers/releases/tag/v5.22.0), [TRL v1.17.0 release](https://github.com/huggingface/trl/releases/tag/v1.17.0), [PEFT releases](https://github.com/huggingface/peft/releases), [llama.cpp release history](https://github.com/ggml-org/llama.cpp/releases), [GGUF quant sizes](https://huggingface.co/ggml-org/Mistral-Large-4-1T-A52B-GGUF), [NVFP4 serving recipe](https://huggingface.co/blog/mistral-large4).


## 2026-10-29 21:04 — official upstream/runtime recheck; no base promotion

- Retain Qwen/Qwen3-0.6B at immutable revision c1899de289a04d12100db370d81485cdf75e47ca. Its weights are Apache-2.0; this does not prove its training corpus is fully open-source. No alternative received a matched frozen Mongolian evaluation or resource comparison in this run.
- PEFT v0.21.2 was released 2026-10-01 at commit eaa35c777c7ba554a2a3639ac9c79bb690f39a57. Its release note fixes encoder-decoder use with Transformers >=5.18.0; it is not evidence of better Qwen3 Mongolian generation. Keep the previously tested PEFT 0.15.2 pin.
- Transformers v5.20.2 release commit 18329f1065382e54db698e242cf98bd3f3e5a766 is dated 2026-10-19. It is not substituted for the tested Transformers 4.51.3 stack without compatibility and same-hash evaluation.
- llama.cpp prerelease b11906 identifies commit 4d71b42fd87db24b8b7c808c151b713aa4459cfd (2026-10-26); the note describes a CPU concat-kernel rewrite. This is an upstream runtime change, not a model-quality result or proof that a llama-cpp-python wheel is compatible. llama-cpp-python v0.3.36 platform builds point to commit 1652066e0af45f2313b339670ef9555e8a54e545 (2026-10-01). Neither runtime was installed here.
- Google's release log dates EmbeddingGemma 2 (740M) to 2026-10-06; it is an embedding model, not a causal text-generation replacement. Gemma 4 release dates in the official log are 2026-03-31 and 2026-06-03 for the listed variants.
- DeepSeek-V4.1-Flash was announced 2026-09-10 with API identifier deepseek-flash and 552B total parameters (8B input-active, 16B output-active). The reviewed announcement does not establish a resource-feasible local weight artifact/revision for this host; treat it as API availability, not a local model.
- Mistral Large 4 was announced 2026-10-06 as a public-preview API with weights planned for the end of October. As of this 2026-10-29 check, an exact downloadable weight revision, weight/code licenses, tokenizer/template and local runtime contract were not verified. Its stated roughly 1T total / 52B active scale is outside this 5.8 GiB RAM host.
- Qwen's official producer index surfaces larger Qwen3.5/3.6/3.8 families, but no newly pinned small candidate was benchmarked here. Meta model terms remain model-specific; no license was inferred across the family.

Sources: https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca ; https://arxiv.org/abs/2505.09388 ; https://github.com/huggingface/peft/releases/tag/v0.21.2 ; https://github.com/huggingface/transformers/releases ; https://github.com/ggml-org/llama.cpp/releases/tag/b11906 ; https://github.com/abetlen/llama-cpp-python/releases ; https://ai.google.dev/gemma/docs/releases ; https://www.deepseek.com/en/news/deepseek-v4-1-flash/ ; https://mistral.ai/news/mistral-large-4/ ; https://github.com/QwenLM/Qwen3.8 ; https://github.com/meta-llama/llama-models

- Safetensors official PyPI history lists stable 0.8.0 on 2026-06-09 and pre-release 0.9.0rc1 on 2026-09-24. Because the real bundle/runtime pair was not available for compatibility testing, neither version is silently selected; bundle creators must declare the exact tested safetensors and tokenizer-backend pins. The manifest records operator-supplied pins, not a generated full dependency lock. Source: https://pypi.org/project/safetensors/

The new safetensors runner is a local execution path, not a model/base upgrade. It does not establish legal redistribution, real inference, offline OS isolation, or quality. No weights, tokenizer, or runtime packages were downloaded in this run.

## 2026-10-29 16:55 — official release recheck; no base promotion

| Candidate / exact identifier observed | Verified release date and distribution | Immutable weight revision / licenses / tokenizer-template / runtime | Resource decision |
| --- | --- | --- | --- |
| Mistral Large 4; official model-page identifier `mistral-large-4` | Mistral's official announcement is dated 2026-10-06 and describes a public-preview API; it says weights are planned for the end of October. As of this check (2026-10-29), a downloadable official weight revision was not established from the reviewed official page. | Exact weight repository/revision, weight license, code license, tokenizer/chat template and local runtime compatibility: **not verified**. Do not infer an Apache license or treat the API preview as a local model. | Official page reports about 1,050B total / 52B active parameters. Not feasible on this host (5.8 GiB RAM); watch-only. |
| DeepSeek-V4.1-Flash; official announcement's API identifier `deepseek-flash` | Official notice dated 2026-09-10 confirms API availability and describes 552B total / 8B active parameters. | Exact downloadable weight ID/revision, weight license, code license, tokenizer/chat template and local runtime compatibility were not established by the reviewed notice. The API alias is not a local weight ID. | Far outside the current host budget; no local integration. |
| EmbeddingGemma 2; exact generation-model ID not applicable | Google's official release log dates the 740M embedding model to 2026-10-06. | Exact model revision/license/runtime were not re-established in this run; it is an embedding model, not a causal text-generation replacement. | Not a standalone chat base. |
| Qwen/Qwen3-0.6B retained baseline | Existing tested candidate; no new base revision selected. | Keep immutable revision `c1899de289a04d12100db370d81485cdf75e47ca`, Apache-2.0 weights and previously tested tokenizer/template/runtime pins; see the retained-baseline entry below. | No candidate promotion without a matched frozen Mongolian evaluation and resource comparison. |

Sources: [Mistral Large 4 announcement](https://mistral.ai/news/mistral-large-4/), [Mistral model documentation](https://docs.mistral.ai/models/mistral-large-4-0), [DeepSeek V4.1-Flash announcement](https://www.deepseek.com/en/news/deepseek-v4-1-flash/), [Google Gemma release log](https://ai.google.dev/gemma/docs/releases), [Qwen3-0.6B pinned card](https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca), [PEFT releases](https://github.com/huggingface/peft/releases), [Transformers releases](https://github.com/huggingface/transformers/releases), [llama-cpp-python releases](https://github.com/abetlen/llama-cpp-python/releases).

No new candidate is promoted. PEFT v0.21.2 (2026-10-01, commit eaa35c7) and Transformers v5.20.2 (2026-10-19) remain untested against the retained Qwen runtime; the current experiment pins are not changed. The upstream llama-cpp-python page lists platform-specific 0.3.36 builds, but this environment has no `llama_cpp` installation and no local GGUF artifact. Release novelty alone does not justify a runtime or base switch.

## 2026-10-29 — offline packaging capability; no base promotion

### Retained baseline

- Exact model ID: Qwen/Qwen3-0.6B.
- Immutable Hub revision: c1899de289a04d12100db370d81485cdf75e47ca.
- Weight license: Apache-2.0, confirmed by the model card and LICENSE at that revision. The base model is open-weight; this does not establish that its full training data is open-source.
- Tokenizer/chat template: pinned tokenizer files at the same revision; the official card demonstrates apply_chat_template. The packaging tool now requires a discoverable explicit chat template in tokenizer_config.json or tokenizer.chat_template.jinja rather than silently selecting a fallback.
- Previously tested CPU runtime: Torch 2.6.0+cpu, Transformers 4.51.3, PEFT 0.15.2, Accelerate 1.6.0; CPU float32, four threads. The pinned upstream model files total approximately 1.52 GB. On 2026-10-28, a fresh-process adapter reload reproduced 12/12 retained predictions in 27.7639 s at 4,822,560 KiB peak RSS; this is reproducibility, not correctness or general Mongolian quality.

### Upstream release check

- Official Qwen3-0.6B card and exact revision: https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca. The Qwen3 report is https://arxiv.org/abs/2505.09388 (submitted 2025-05-14). No new exact small-model revision with measured Mongolian advantage was selected.
- PEFT release page lists v0.21.2 as latest, released 2026-10-01 at commit eaa35c7: https://github.com/huggingface/peft/releases. This release is not installed in the pinned experiment.
- Transformers v5.20.2 was released 2026-10-19: https://github.com/huggingface/transformers/releases. It is not substituted for the tested Transformers 4.51.3 stack without a compatibility and same-evaluation rerun.
- Google's release log lists EmbeddingGemma 2 (740M) on 2026-10-06 and Gemma 4 releases in 2026: https://ai.google.dev/gemma/docs/releases. EmbeddingGemma is an embedding model, not a causal chat-model replacement. A generative Gemma candidate remains unpromoted until exact model ID/revision, license terms, tokenizer/template, runtime support, CPU/RAM and same-hash Mongolian evaluation are all established.
- DeepSeek-V3 reports 671B total parameters / 37B active per token: https://github.com/deepseek-ai/DeepSeek-V3; it is outside this CPU host's resource budget. Meta's model list records model-specific license/use-policy gates: https://github.com/meta-llama/llama-models. The Mistral inference repository is archived and read-only since 2026-06-16: https://github.com/mistralai/mistral-inference.

### Change and decision

Added a local offline bundle packager for an existing full/merged safetensors directory or base-plus-adapter directory. It records exact upstream revision, separately declared weight/code licenses, URLs, runtime pins, tokenizer-template identity and per-file SHA-256; verification performs no network calls and loads no tensors. The tool does not merge adapters, quantize weights, verify legal rights, execute inference or establish OS-level network isolation.

No model download, inference, training, held-out score or latency/RAM/cost comparison was run on 2026-10-29. No candidate or runtime was promoted. The 15 tests are fixture-based packaging tests, not actual model validation; latest remote CPU CI run #187 passed 171 tests in 2.535 s with one optional Torch skip; fixture tests still do not validate a real model. No new RAINY weights were created or committed.

## 2026-10-28: restoration, no base promotion

Rechecked official Qwen3-0.6B card/report, Gemma release log, DeepSeek and Meta
repositories, Mistral inference and PEFT releases. Retain Qwen/Qwen3-0.6B at
`c1899de289a04d12100db370d81485cdf75e47ca`, Apache-2.0 open weights;
fully open training data is not established. No new release date, immutable
candidate, runtime upgrade or Mongolian advantage was established today.
The existing official tokenizer/template and tested runtime pins are unchanged.
Afternoon fresh-process inference matched12/12 retained adapter outputs;
evening work adds a real child-RSS preflight, not new training or quality gains.
No API-only service was used as a local base. See today's research and
[restore usage](CHECKPOINT_RESTORE.md).

## 2026-10-27 21:00 — retained transfer result, no promotion

Same `Qwen/Qwen3-0.6B` immutable revision
`c1899de289a04d12100db370d81485cdf75e47ca`, Apache-2.0 open weights (not a
fully open training-data claim), official local tokenizer/template. CPU float32,
four threads, Transformers4.51.3/PEFT0.15.2/Torch2.6.0+cpu executed. Seed42
16-step synthetic LoRA changed the separate 12-case draft score0/12→3/12;
training30.038s, model-process peak RSS4.604GiB. Supervisor zero RSS is invalid.
Seed43 ran but complete artifacts were not retained: no repeat-seed promotion.
No newly asserted model release date, architecture change or replacement base.
Official Qwen card/report and PEFT releases rechecked; dependency freeze and
per-file model hashes retained with [results](../research/results/2026-10-27-transfer/).

## 2026-10-27 recheck — no base promotion

Reopened the official [Qwen3-0.6B card](https://huggingface.co/Qwen/Qwen3-0.6B),
[Qwen3 report](https://arxiv.org/abs/2505.09388) (submitted 2025-05-14), and
[PEFT releases](https://github.com/huggingface/peft/releases). Retain
`Qwen/Qwen3-0.6B` revision `c1899de289a04d12100db370d81485cdf75e47ca`,
Apache-2.0 open weights and existing tokenizer/chat-template/runtime pins.
No newly verified immutable candidate, dependency upgrade, or vendor quality
claim is integrated. No model execution or resource/quality comparison completed
in this run. The bounded subprocess supervisor is infrastructure, not a model
quality improvement. See `research/2026-10-27.md`.

## 2026-10-26 17:11: transfer comparison incomplete

Kept Qwen/Qwen3-0.6B at c1899de289a04d12100db370d81485cdf75e47ca,
Apache-2.0 open weights, official local tokenizer/template, non-thinking greedy
CPU float32. Official model card, Qwen3 report, PEFT documentation/releases and
Google/DeepSeek/Meta/Mistral producer pages reopened. No new immutable candidate
or tested runtime upgrade promoted. The seed-configurable runner was exercised
through16 synthetic training steps, but the full transfer predictions/summary
were not retained after interruption. No complete quality/resource comparison
or replacement-base decision can be made. See today's research for failures.

## 2026-10-26: checkpoint reproducibility, no model promotion

Retained Qwen3-0.6B revision c1899de289a04d12100db370d81485cdf75e47ca
and its official tokenizer/template/license. The official model card, Qwen3
report (2025-05-14) and PEFT release page were rechecked. PEFT v0.21.2's
encoder-decoder/Transformers >=5.18.0 fix does not justify changing this tested
causal runtime. Real CPU LoRA resume matched uninterrupted training exactly;
no new Mongolian quality score was measured. See [research](../research/2026-10-26.md).

## 2026-10-25 16:30: actual pinned Qwen3 CPU experiment

`Qwen/Qwen3-0.6B` revision `c1899de289a04d12100db370d81485cdf75e47ca`
was downloaded and executed (Apache-2.0 open weights; not API-only, not a
fully open training-data claim). No new release-date claim is made.
Official tokenizer/chat template at that revision, `enable_thinking=False`;
Transformers 4.51.3, Torch 2.6.0+cu124 CPU execution, PEFT 0.15.2 tested.
Weights are 1,503,300,328 bytes; combined inference/LoRA experiment peak RSS
4.84 GiB with four CPU threads. Real 16-step synthetic LoRA changed the same
draft exact-match score from 0/24 to 6/24; translation/transliteration stayed
0/4. This is limited diagnostic evidence, not broad Mongolian validation.
No existing base/pin/results were replaced. Adapter is specific to this base;
no cross-architecture compatibility is assumed. Full hashes, timings, outputs,
failure notes and limitations are in [research](../research/2026-10-25.md).

## 2026-10-25 13:00: immutable small-base candidate recorded; no promotion

The official `Qwen/Qwen3.5-0.8B-Base` card was verified at immutable revision
`dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`. It is a pretrained-only 0.8B
vision-language causal model under Apache-2.0. The card states that the
`<|im_start|>` / `<|im_end|>` control tokens and official chat template support
LoRA-style PEFT without necessarily tuning the large embeddings. Transformers,
vLLM and SGLang compatibility is producer-declared; no local runtime was
installed or tested here. Exact CPU RAM, quantized artifact and throughput
requirements remain unmeasured, and no matched-hash Mongolian baseline exists.

Google's dated release page still lists EmbeddingGemma 2 (740M, 2026-10-06) as
the newest entry; it is an embedding model. No new resource-feasible DeepSeek,
Meta or Mistral causal candidate with a complete local comparison was
established. Existing model pins and rollback results remain unchanged. No
weights, adapter or dependency were downloaded, trained, inferred or promoted.

## 2026-10-25 09:00: small-model watch; baseline retained

Official Qwen, Google Gemma, DeepSeek and PEFT sources were rechecked.
`Qwen/Qwen3.5-0.8B` is dated 2026-03-09 and is explicitly positioned for
prototyping and task-specific fine-tuning; it is resource-interesting, but this
run did not establish its immutable revision, exact weights license, pinned
runtime compatibility, tokenizer/chat-template behavior or a matched-hash
Mongolian quality/latency/memory advantage. It therefore remains watch-only.
Qwen3.8-27B and the 763B DeepSeek-V4.1-Flash-1017 remain outside this host's
resource envelope. Google's latest dated Gemma entry observed was the
specialized EmbeddingGemma 2 (740M, 2026-10-06), not a causal base. PEFT v0.21.2
(2026-10-01, release commit `eaa35c7`) remains the latest verified release.

No model, adapter or dependency was downloaded, trained, inferred or promoted.
Existing pins, baseline results and rollback evidence remain unchanged. The
executable result is licensed raw corpus batch 01, not model-quality evidence.

## 2026-10-24 21:00: official recheck; baseline retained

Official Qwen, Google Gemma, DeepSeek, Meta, Mistral and PEFT sources were
rechecked. `Qwen/Qwen3.8-27B` is a 27B native vision-language model and is not
resource-feasible on this host. Google's latest dated entry remains
EmbeddingGemma 2 (740M, 2026-10-06), an embedding model rather than a causal
base. `deepseek-ai/DeepSeek-V4.1-Flash-1017` remains 763B. Mistral's newest
modified entries are specialized Timestral forecasters; Meta's producer index
did not surface a new small causal model. PEFT v0.21.2 remains the latest
verified release checked here.

No immutable, resource-feasible candidate with verified license, tokenizer,
chat template, runtime compatibility and a matched-hash Mongolian quality,
latency and memory advantage was established. Existing pins and rollback
evidence remain unchanged. No model, adapter or dependency was downloaded,
trained, inferred or promoted; batches 04–05 are raw corpus work only.

## 2026-10-24 17:00: official recheck; no promotion

Official Qwen, Google Gemma, DeepSeek, Meta and Mistral producer listings plus
PEFT releases were rechecked. Recently dated entries are specialized or far
outside the local resource envelope: Google lists EmbeddingGemma 2 (740M,
2026-10-06), Mistral lists Large 4 (52B active / 1.05T total), and the checked
DeepSeek V4.1 Flash card is 763B. PEFT v0.21.2 (2026-10-01, release commit
`eaa35c7`) includes an encoder-decoder compatibility fix for Transformers
>=5.18, but the RAINY runtime is not installed or compatibility-tested here;
this is not grounds for a blind dependency upgrade.

No immutable, resource-feasible candidate with a verified license/runtime
combination and matched-hash Mongolian quality, latency and memory advantage
was established. Existing pins and rollback evidence remain unchanged. No
model, adapter or dependency was downloaded, trained, inferred or promoted;
batch 03 is raw corpus work only.

## 2026-10-24 13:00: official recheck; no promotion

Official Qwen listings, Google Gemma releases, the DeepSeek producer card and
PEFT releases were reopened. The newest Qwen entries surfaced by modification
date remain image/guard/specialized or much larger models rather than a newly
validated small Mongolian causal base. Google's latest dated release entry is
still specialized rather than evidence of a better RAINY causal base;
DeepSeek-V4.1-Flash-1017 remains a 763B model, and PEFT remains v0.21.2.

No immutable, resource-feasible candidate with verified license, local runtime
compatibility and a matched-hash Mongolian quality/resource advantage was
established. Existing pins and rollback evidence remain unchanged. No model,
adapter or dependency was downloaded, trained, inferred or promoted; batch 02
is raw corpus work only.

## 2026-10-24 09:00: official recheck; baseline retained

Official Qwen, Google Gemma, DeepSeek, Meta, Mistral and PEFT producer pages
were checked after the 2026-10-23 snapshot. No resource-feasible immutable
causal base with a newly verified weights/code license, compatible pinned local
runtime and matched-hash Mongolian advantage was established. Specialized
embedding, time-series and very large multimodal releases do not replace the
current causal-model comparison candidates.

Existing model revisions, baseline results and rollback evidence remain
unchanged. No model, adapter or runtime dependency was downloaded, trained,
inferred or promoted. The executable work in this run is licensed raw corpus
batch 01; collection throughput is not model-quality evidence.

## 2026-10-23 21:00: official recheck; baseline retained

Official Qwen, Google Gemma, DeepSeek, Meta, Mistral and PEFT pages were
reopened after the 17:00 snapshot. Google still lists EmbeddingGemma 2 (740M,
2026-10-06) as the latest dated Gemma entry; it is not a causal base. Mistral
Large 4 remains an upcoming October 31 weight release, and the newly surfaced
Timestral checkpoints are specialized time-series forecasters rather than
general language models. PEFT v0.21.2 remains the latest verified release.

No new resource-feasible immutable causal base, verified license/runtime
combination, locally executed compatibility result or same-hash Mongolian
advantage was established. Existing pins, baseline result and rollback
evidence remain unchanged. No weights or dependency were downloaded, trained,
inferred or promoted; the executable work completes raw corpus batches 04–05.

## 2026-10-23 17:00: small-model watch only; no promotion

Official producer pages surfaced `Qwen/Qwen3.5-0.8B` and
`mistralai/Ministral-3-3B-Instruct-2512`; the latter currently resolves to
revision `b4cc13e94e5e7481a83b34797b8a47efb62d197c`. This run did not establish
an immutable Qwen revision, a verified Ministral weights-license/runtime
combination, or a same-hash Mongolian quality/latency/RAM comparison for either
candidate. They therefore remain watch-only and are not represented as RAINY
improvements.

The newer surfaced Qwen3.8 27B/Flash-Next, DeepSeek-V4.1-Flash-1017 and Mistral
Large 4 artifacts exceed the current local resource envelope. EmbeddingGemma 2
is an embedding model, not a causal base. No model, adapter or runtime pin was
downloaded, trained, inferred or changed. The executable result is raw corpus
batch 03; retained baseline and rollback evidence remain unchanged.

## 2026-10-23 13:00: official recheck; no promotion

Official Qwen, Google Gemma, DeepSeek, Meta, Mistral and PEFT sources were
reopened. Google still dates EmbeddingGemma 2 to 2026-10-06; it is an embedding
model, not a causal RAINY training base. DeepSeek-V4.1-Flash-1017 and Mistral
Large 4 remain far outside this run's local memory/disk envelope, while PEFT's
latest verified release remains v0.21.2. Producer claims and repository update
ordering are not held-out Mongolian results.

No resource-feasible immutable causal model, verified license/runtime change or
matched RAINY Mongolian advantage was established. Existing pins, rollback
evidence and baseline remain unchanged. No weights or dependency were
downloaded, trained, inferred or promoted; the executable change is raw corpus
batch 02.

## 2026-10-23 09:00: official recheck; baseline retained

Official Qwen producer listings, Google Gemma releases, the DeepSeek producer
index and PEFT releases were reopened. Qwen's newest surfaced items are image,
guard and driving models rather than a smaller validated Mongolian causal base.
Google's October 6 release list includes specialized Gemma artifacts; vendor
multilingual or medical claims are not RAINY held-out Mongolian evidence. PEFT
remains v0.21.2. No immutable model/runtime pin was changed, downloaded or
promoted. The executable change is a new attributed raw-text batch, not model
training, inference or measured quality gain.

## 2026-10-22 17:00: official sources unchanged; data gate continued

Reopened official Qwen material, Google Gemma releases, the exact
`deepseek-ai/DeepSeek-V4.1-Flash-1017` card, Meta's producer index, Mistral
model documentation and PEFT releases. Google still lists EmbeddingGemma 2
(2026-10-06) as the latest dated family entry. DeepSeek's card still identifies
MIT weights, 763B parameters, no Jinja chat template and separate Python/Rust
prompt encoding. These upstream runtime instructions do not establish local
compatibility or Mongolian quality.

No new resource-feasible immutable causal base, license change, locally tested
runtime or matched held-out Mongolian advantage was established. Existing
pins, Qwen3.5-4B experimental result and rollback artifacts remain unchanged.
No download, dependency installation, inference, training or promotion was
performed; the executable result is licensed raw-data batch 03.

## 2026-10-22 13:00: official recheck; retained baseline

Reopened official Qwen material, the Google Gemma release log, the exact
`deepseek-ai/DeepSeek-V4.1-Flash-1017` card, Meta's producer index, Mistral's
Large 4 announcement/docs and PEFT releases. Google still lists
EmbeddingGemma 2 (2026-10-06) as its latest dated Gemma entry; it is an
embedding model rather than a causal training base. DeepSeek Flash-1017 is a
roughly 763B multimodal model and Mistral Large 4 is a 1.05T/52B-active
open-weight model; neither is feasible in this run's 9,967 MiB RAM / 25 GiB
free-disk environment. Producer performance claims are not Mongolian evidence.

No new resource-feasible immutable causal base, verified license change,
locally tested dependency or matched held-out Mongolian advantage was
established. Existing pins, rollback results and the Qwen3.5-4B experimental
baseline remain unchanged. No weights, runtime dependency, model integration,
training or inference was executed; batch 02 is raw-data work only.

## 2026-10-22 09:00: official recheck; no baseline promotion

Reopened the official Qwen organization/cards, Google Gemma release log,
DeepSeek producer card and PEFT releases. The checked pages still show
Qwen3.8-27B (2026-08-13), EmbeddingGemma 2 (2026-10-06),
DeepSeek-V4.1-Flash-1017 and PEFT v0.21.2 (2026-10-01). No new immutable,
resource-feasible causal base, license change, locally validated runtime result
or matched Mongolian advantage was established. Existing pins, rollback data
and baseline results remain unchanged; no model or dependency was downloaded,
integrated or promoted. The executable work is a new licensed raw-source batch,
not training, inference or measured quality gain.

## 2026-10-21 21:00: official sources rechecked; baseline retained

Reopened the official Qwen3.8-27B card, Google Gemma release log, DeepSeek and
Meta producer pages, Mistral Large 4 planned-weight page and PEFT releases. No
new immutable resource-feasible base, license change, locally validated runtime
compatibility or matched Mongolian result was established after 17:00. The
Qwen3.8-27B card still describes a 27B open-weight multimodal model, Google's
latest dated Gemma entry remains EmbeddingGemma 2 (2026-10-06), and Mistral
Large 4 remains an upcoming artifact. Existing pins, baseline results and
rollback evidence are retained. This run completes two raw corpus batches; it
does not integrate, train or promote a model.

## 2026-10-21 17:00: official sources unchanged; data work continued

Reopened the official Qwen organization/cards, Google Gemma release log,
DeepSeek and Meta producer pages, the Mistral Large 4 planned-weight page and
PEFT releases. No new immutable resource-feasible base, license change, tested
runtime compatibility or matched Mongolian result was established after the
13:00 check. Existing pins, baseline results and rollback evidence are retained;
no model or dependency was downloaded or promoted. The executable work is raw
corpus collection and cross-branch deduplication, not training or quality gain.

## 2026-10-21 13:00: upstream recheck; no baseline change

Reopened the official Qwen3.8-27B card, Google Gemma release log, DeepSeek and
Meta producer pages, the planned Mistral Large 4 weights page, and PEFT release
metadata. No new immutable resource-feasible model revision, license change,
locally compatible runtime result, or held-out Mongolian comparison was
established after the morning snapshot. Qwen3.8-27B remains watch-only at the
morning pin; PEFT remains uninstalled. No model was downloaded, integrated or
promoted. This run adds raw corpus data only; retained configs, revisions and
rollback results are unchanged.

## 2026-10-21: official recheck and Qwen3.8-27B immutable snapshot

Official model card/API checked for exact ID Qwen/Qwen3.8-27B: model-card
release date 2026-08-13, immutable revision
1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0, Apache-2.0 weights/repository,
open-weight rather than API-only. The API exposes a Jinja chat template and
lists Transformers with Qwen3_5ForConditionalGeneration; compatibility is
declared upstream, not locally validated. BF16 weights contain 27,781,427,952
parameters and occupy 55,615,875,685 bytes, exceeding this run's approximately
26 GiB free disk before runtime overhead. No download, adapter-compatibility
claim, integration or baseline promotion. Fully open training data is not
established.

Gemma's official release log still lists EmbeddingGemma 2 (2026-10-06) as its
latest entry; it is an embedding model, not a drop-in causal base. DeepSeek
Flash-1017 remains the latest checked DeepSeek card; Meta's official organization
page provided no newer resource-feasible candidate. Mistral Large 4 remains an
upcoming 2026-10-31 weight release, not downloadable/tested today. PEFT latest
API remains v0.21.2 (2026-10-01T10:29:50Z). Existing baseline and rollback
evidence are retained. Executable deliverable: 20 licensed raw sources, not
trained weights or measured Mongolian quality.

## 2026-10-20: DeepSeek Flash-1017 watch-only snapshot

17:00 follow-up: official producer/runtime/paper sources reopened; PEFT latest
API remains v0.21.2 (2026-10-01T10:29:50Z). No new immutable model pin or tested
runtime upgrade established. Batch 03 adds raw technology/energy sources, not
training or measured quality improvement. Baseline and rollback evidence kept.

13:00 follow-up: official producer pages, PEFT releases/API and LoRA paper
reopened. PEFT remains v0.21.2 (2026-10-01T10:29:50Z). No newly verified
immutable model revision or tested runtime upgrade beyond the morning snapshot.
Batch 02 adds real raw data, not a model-quality improvement.

Official [model card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)
and Hub API checked: exact ID `deepseek-ai/DeepSeek-V4.1-Flash-1017`, immutable
revision `1bae0e1088993b9b82de08f59de5be5a34e42170`. Repository creation is
2026-10-17T02:40:38Z; an independent release announcement date was not verified.
MIT applies to repository code and weights. Open-weight, not API-only; fully
open training data is not established. Vendor describes a minor update with
reasoning/coding/visual improvements; these are not RAINY Mongolian measurements.
There is no Jinja chat template: the card points to Python encoding and the
deepseek-recipe toolkit. Tokenizer files and runtime version compatibility have
not been locally validated. Hub reports 763B parameters with mixed tensor types;
not feasible in this approximately 10 GiB RAM / 26 GiB free-disk environment.
No download, adapter compatibility claim, integration or base replacement.

Qwen/Gemma/Meta/Mistral official pages and LoRA paper reopened. PEFT latest API
still reports v0.21.2, published 2026-10-01T10:29:50Z, the encoder-decoder fix for
Transformers >=5.18.0. No tested dependency upgrade. Existing pins/results kept.
Executable deliverable: 20 new licensed raw sources; see [research](../research/2026-10-20.md).

## 2026-10-19 source recheck

21:00 follow-up: seven official producer/runtime/paper sources and PEFT API
reopened. Still v0.21.2 (2026-10-01T10:29:50Z); no new verified immutable pin,
tested runtime integration or baseline promotion. Batches 03–04 add raw sources,
not training or measured model-quality improvement.

17:00 continuation: official producer/runtime/paper pages and PEFT latest API
rechecked during this work cycle. No new verified immutable pin or tested runtime
upgrade. Batch 02 is real corpus collection, not training or quality improvement.

Official Qwen, Gemma, DeepSeek, Meta, Mistral pages, PEFT releases/API and LoRA
paper reopened. PEFT API still reports v0.21.2, published 2026-10-01T10:29:50Z,
encoder-decoder compatibility fix for Transformers >=5.18.0. No new immutable
model pin or tested runtime upgrade established; baseline and rollback evidence
unchanged. Actual deliverable: 20 real raw sources, not model-quality improvement.
See [research](../research/2026-10-19.md). Watchlist coverage is not exhaustive.

## 2026-10-18 source recheck

21:00 follow-up: official producer/runtime/paper sources and PEFT API rechecked;
v0.21.2 remains the API's latest release. No new immutable model pin or tested
dependency change. Batches 04–05 complete collection target, not model training.

17:00 follow-up: official producer/runtime/paper sources and PEFT API rechecked.
No new verified immutable model pin, tested dependency upgrade or baseline
promotion. Batch 03 adds raw sources only; no measured model-quality gain.

13:00 follow-up: same official sources and PEFT release API rechecked; no new
verified immutable pin or tested upgrade. Batch 02 adds raw sources, not trained
weights or benchmark evidence. Baseline unchanged.

Official producer pages, PEFT releases and LoRA paper rechecked. PEFT latest API
still reports v0.21.2 (2026-10-01T10:29:50Z), encoder-decoder fix for Transformers
>=5.18.0. No new verified immutable model pin, tested runtime upgrade or baseline
promotion. Delivered real corpus data, not training or measured quality gain.
See [research](../research/2026-10-18.md); previous pins/results preserved.

## 2026-10-17 source recheck

17:00 follow-up: reopened the same official producer/runtime/paper sources.
PEFT latest API remains v0.21.2 (2026-10-01T10:29:50Z). No new verified model
revision, dependency upgrade or baseline change; batch 03 is data collection only.

13:00 follow-up: official producer pages, PEFT release notes/API and LoRA paper
rechecked. No new immutable pin, tested runtime upgrade or baseline promotion.
Batch 02 adds raw sources only; no training/inference or measured quality gain.

Reopened official Qwen, Gemma, DeepSeek, Meta, Mistral pages, PEFT releases and
LoRA paper. PEFT latest-release API still reports v0.21.2, published
2026-10-01T10:29:50Z; no new immutable model pin, tested runtime upgrade or
baseline promotion established. Delivered a 20-source raw corpus batch, not
training/inference or measured quality improvement. Existing pins and results
remain unchanged. See [today's research](../research/2026-10-17.md).

## 2026-10-16 source recheck

21:00 follow-up: reopened official producer pages, PEFT releases and LoRA paper.
PEFT latest-release API still reports v0.21.2, published 2026-10-01T10:29:50Z;
no dependency upgrade, new immutable weight pin or model promotion established.
Completed two real-source batches, not model integration or quality improvement.
Existing runtime/model pins and rollback results are unchanged.

13:00 follow-up: reopened the same official producer pages, PEFT releases and LoRA
paper. No new immutable revision, tested runtime or baseline promotion established.
Executed daily raw-source batch 02; no inference/training or model-quality claim.

Official Qwen/Gemma/DeepSeek/Meta/Mistral pages below and PEFT releases/LoRA paper
were reopened. PEFT latest API remains v0.21.2 (2026-10-01T10:29:50Z), an
encoder-decoder fix for Transformers >=5.18.0, not a locally validated training
lock. No new immutable model revision or runtime integration was established;
baseline and rollback artifacts unchanged. Delivered a new 20-document raw batch,
not inference/training or measured model improvement. See today's research.

Шалгасан: 2026-09-29, Asia/Ulaanbaatar. Энэ нь бүрэн зах зээлийн жагсаалт биш, тухайн өдөр албан ёсны эх сурвалжаас баталгаажуулсан shortlist. Нийтэлсэн өдөр ба metadata шинэчилсэн өдрийг ялгана.

| Загвар | Албан ёсны эх сурвалж | Одоогийн шийдвэр |
| --- | --- | --- |
| Qwen3.8-27B | https://huggingface.co/Qwen/Qwen3.8-27B | Монгол benchmark-д нэр дэвшигч; model card Apache-2.0 гэж тэмдэглэсэн |
| Qwen3.8-Flash-Next | https://huggingface.co/Qwen/Qwen3.8-Flash-Next | Том загварын судалгааны нэр дэвшигч; лиценз, нийт/идэвхтэй параметр, бодит санах ойг нарийвчлан шалгах |
| Gemma 4 family | https://ai.google.dev/gemma/docs/core/model_card_4 | Жижиг хувилбаруудыг GPU тодорхой болмогц эхэлж үнэлэх санал; model card Apache-2.0 |
| DeepSeek-V4.1-Flash | https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash | MIT гэж тэмдэглэсэн; том MoE тул одоохондоо архитектур/үнэлгээний судалгаа |

Өмнөх Qwen3-4B, Gemma 3-4B нь хуучин baseline кандидатууд. README ба ROADMAP-ийн анхны нэрс эцсийн сонголт биш; шинэ сонголтыг энэ бүртгэл болон хэмжилтээр удирдана.

## Өдөр тутмын шинэчлэл

1. Qwen, Google, DeepSeek, Meta, Mistral болон бусад үйлдвэрлэгчийн албан ёсны model card, release, жингийн repository-г шалгах.
2. Яг model ID, release date (баталгаажсан үед), immutable revision SHA, weights/code лиценз, tokenizer/chat template, runtime dependency-г бүртгэх. Мэдэхгүй утгыг таахгүй.
3. Нээлттэй жинтэй (open-weight) болон бүрэн open-source гэсэн ангиллыг ялгах. API-only загварыг fine-tuning суурь гэж бүү бүртгэ.
4. Нэг ижил held-out Монгол тест, decoding budget ашиглан baseline-тай харьцуулах. Зөв бичих, утга ойлгох, орчуулга, галиг, reasoning, latency, peak VRAM-ийг хэмжих.
5. GPU ба төсөвт багтах эсэх, runtime дэмжлэг, лицензийг шалгасны дараа isolated config/branch-д интеграц хийх.
6. Чанар/нөөцийн давуу тал нотлогдвол шинэ суурь сонгох; өмнөх revision/config/results-ийг rollback хийх боломжтой хадгалах.

## Хязгаар

Энд зөвхөн судалгааны бүртгэл нэмсэн. Эдгээр шинэ загварыг татаж, inference хийж, сургаж эсвэл Монгол benchmark ажиллуулаагүй. Сонгосон production/training model байхгүй. Өмнөх adapter-ийг шинэ архитектурт шууд нийцнэ гэж үзэхгүй. MoE-ийн идэвхтэй параметр нь бүх жинг хадгалах санах ойн хэмжээтэй адил биш. Шинэ гэсэн шалтгаанаар автоматаар суурь сольж болохгүй.

## 2026-09-29 follow-up

Reopened the Qwen3.8-27B, Gemma 4 and DeepSeek-V4.1-Flash official cards above; checked [Meta](https://huggingface.co/meta-llama) and [Mistral](https://huggingface.co/mistralai) producer indexes. No candidate promoted to an integration or replacement baseline. Release dates and immutable candidate revisions remain unverified here; runtime support is not locally tested and measured VRAM/latency/cost are unavailable. Weights availability is not proof of fully open-source training data/code. The pinned Qwen3-0.6B CPU baseline artifacts remain the rollback reference in experiments/qwen3-06b-cpu-v1. This follow-up fixes data split correctness before further comparisons; see research/2026-09-29.md.

## 2026-10-03 verification

Reopened the official [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [Gemma 4](https://ai.google.dev/gemma/docs/core/model_card_4), and [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) cards, plus the [Meta](https://huggingface.co/meta-llama) and [Mistral](https://huggingface.co/mistralai) producer indexes. Qwen3.8-27B remains an Apache-2.0, 27B open-weight candidate whose card lists Transformers/vLLM/SGLang support. Producer claims and index ordering are not RAINY benchmark evidence. No candidate received a verified release-date/revision upgrade, local runtime integration, adapter compatibility claim, or baseline promotion today. The pinned Qwen3-0.6B experiment remains the rollback baseline; no new inference, VRAM, latency or cost measurement was run.

## 2026-10-04 verification

Reopened the official Qwen3.8-27B, Gemma 4 and DeepSeek-V4.1-Flash cards and the Meta/Mistral producer indexes. No newly verified immutable revision, local RAINY runtime result, Mongolian held-out score, latency, VRAM or cost result was added, so no integration or baseline promotion occurred. Today’s implementation instead adds a reproducible held-out release gate; candidate comparison must record the evaluation SHA-256 and pass the same frozen cases/config. Qwen3-0.6B remains the pinned rollback baseline.

## 2026-10-05 verification and promotion gate

Reopened the official Qwen3.8-27B, Gemma 4 and DeepSeek-V4.1-Flash cards plus Meta and Mistral producer indexes. No candidate gained a verified RAINY-local immutable revision/runtime result or Mongolian score today. Added `scripts/compare_benchmarks.py`: candidates are comparable only on the same evaluation SHA-256, metric, case count, seed, sampling, token budget and thinking mode. Promotion additionally requires higher measured accuracy, complete predictions, and recorded hardware, peak VRAM and cost. Adapter metadata must pin its base revision; architectural compatibility is never inferred. The Qwen3-0.6B artifact remains the rollback baseline and was not overwritten.


## 2026-10-05 follow-up: executed CPU candidates

After the earlier research-only entry, real CPU inference was completed for pinned Qwen3-0.6B BF16 (0/24), Qwen3-1.7B BF16 (0/24) and the separately pinned Unsloth Qwen3-4B-Instruct-2507 Q4_K_M conversion (7/24). These are feasible older candidates, not a claim about the latest releases. The GGUF runtime now actually executes locally; it remains experimental and is not a promoted RAINY base. No training occurred. See [full run identities, sources, resource measurements, raw responses and reproduction commands](QUALITY_EXPERIMENT_2026-10-05.md). Different runtime/precision blocks a matched 4B comparison. The unchanged 24-question draft smoke set cannot establish general Mongolian quality; no human-reviewed held-out result or model-quality leadership claim is made. Existing configs/results are retained for rollback.


## 2026-10-06: pinned small-model research candidates

These are **open-weight research candidates**, not working RAINY integrations or approved replacements. Apache-2.0 on the weight repositories does not establish fully open training data/code. No API-only endpoint is treated as a downloadable training base.

| Model ID | Immutable repository revision (HF API, checked 2026-10-06) | Weight license | Verified release date | Runtime and resource decision |
| --- | --- | --- | --- | --- |
| [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` | Apache-2.0 | Not verified in this run; repository creation date is not release evidence | Card documents Transformers, vLLM, SGLang and KTransformers. Its Transformers recipe uses upstream main; an immutable runtime version must be verified separately. 4B language weights alone are roughly 8 GB at BF16, before vision/runtime/cache: do not assume they fit the previous 8 GiB process limit. Next: inspect a pinned quantized artifact and chat template. |
| [google/gemma-4-E2B-it](https://huggingface.co/google/gemma-4-E2B-it) | `3e22461f65e89153144f8adb70e3b8c2cc9845a7` | Apache-2.0 | 2026-03-31, Google family release log | Card uses AutoProcessor and AutoModelForMultimodalLM with current Transformers. E means effective parameters, not total stored weights; PLE and encoders affect memory. Actual peak RAM/VRAM and a compatible pinned runtime are unmeasured. |
| [google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | `ee0ef6023621cff504d758262d4e04895a5af4a2` | Apache-2.0 | 2026-03-31, Google family release log | Same effective-versus-total parameter caveat. No claim of fitting 8 GiB; quantization and context must be tested. |

Revision evidence: the public `https://huggingface.co/api/models/<model-id>` endpoint, queried for each row. Release evidence: [Google release log](https://ai.google.dev/gemma/docs/releases). The pinned hashes identify snapshots; no weights were downloaded today. The approximate Qwen weight-memory calculation is arithmetic, not a measured runtime requirement.

Also rechecked [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash), [Meta's producer index](https://huggingface.co/meta-llama), and [Mistral Small 4's official announcement](https://mistral.ai/news/mistral-small-4/). These checks do not establish exhaustive latest-release coverage or a new Mongolian quality result. No additional candidate was promoted.

The previous 4B Q4_K_M result remains 7/24 on public draft smoke questions, not a held-out benchmark. Today's code change rejects invalid numeric measurements and incomplete-baseline promotion; it does not improve model answers. Preserve old locks/results; architecture and adapter compatibility must be checked separately.

## 2026-10-07: Qwen3.5-4B executed candidate

Pinned upstream `Qwen/Qwen3.5-4B` at `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` and the separate third-party `unsloth/Qwen3.5-4B-GGUF` conversion at `e87f176479d0855a907a41277aca2f8ee7a09523`. The executed `Qwen3.5-4B-Q4_K_M.gguf` is 2,740,937,888 bytes with SHA-256 `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4`. Both repositories report Apache-2.0; the conversion is not an official Qwen artifact and open weights do not prove open training data.

Real CPU inference completed with llama-cpp-python 0.3.36 and Transformers 4.51.3: **12/24 (50%)**, 52.9427 generation seconds, 4.241 GiB peak process RSS, two token-limit hits. Against the retained Qwen3-4B-Instruct-2507 Q4_K_M run, the gate found matched settings, +5 exact matches and -0.5231 seconds/case. It still returned `promotion_eligible=false`: resource/cost metadata are incomplete and the 24 public draft cases are not a human-reviewed held-out benchmark. No training, adapter compatibility claim or base-model replacement occurred. See [the full experiment report](QUALITY_EXPERIMENT_2026-10-07.md).

## 2026-10-08: official-source verification

No candidate was integrated or promoted today. Official sources were rechecked; dates below are publisher release dates, not repository-update dates.

| Candidate | Verified identity and release | Classification | RAINY decision |
| --- | --- | --- | --- |
| `mistralai/Mistral-Small-4-119B-2603` | HF revision `a11f36bebf709121056b1dbcc943d1c6afbe494d`; Mistral announcement 2026-03-16; Apache-2.0 | Open weights; publisher calls the release open source. 119B total, 6B active/token, official repository 242 GB | Vendor minimum is 4x H100, 2x H200 or 1x B200. Not feasible in the measured 8 GiB CPU environment; no download or Mongolian run. |
| `deepseek-ai/DeepSeek-V4.1-Flash` | HF revision `2cba9e42aa026125f3ed06c6d98c1db82f7ca027`; MIT; official repository 510 GB | Open weights; Transformers/vLLM/SGLang recipes are published | Not feasible locally; no download, latency/VRAM/cost measurement or adapter claim. |
| Qwen3.8 / Gemma 4 / Meta Llama 4 families | Official producer pages rechecked 2026-10-08 | Open-weight families with artifact-specific licenses; API availability is not weight availability | No newly verified small candidate displaced the executed Qwen3.5-4B. Existing pinned entries and rollback artifacts remain unchanged. |

Vendor benchmark and efficiency claims are not Mongolian evidence. Mistral Small 4's active parameter count does not reduce the need to store its full MoE weights. DeepSeek's published runtime recipes do not imply compatibility with RAINY's existing adapters. The next model experiment remains a resource-feasible, pinned Gemma 4 quantization after the human-review evaluation workflow.

## 2026-10-09: EmbeddingGemma 2 and official-source verification

No generative base was replaced or promoted today. Google's official release log records **EmbeddingGemma 2** on 2026-10-06, and the official model card classifies it as a 740M multimodal embedding model rather than a chat/generative LLM.

| Model ID | Immutable repository revision (HF API, checked 2026-10-09) | License and release | Runtime/resource notes | RAINY decision |
| --- | --- | --- | --- | --- |
| [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2) | `914f7f89142e33e77833254d9c9b90c3cef7303b` | Apache-2.0; released 2026-10-06 in the [Google Gemma release log](https://ai.google.dev/gemma/docs/releases) | 740M total parameters, 8K context, 768-dimensional text/image/video/audio embeddings and 100+ languages. Official card recommends BF16 or FP32 and warns that FP16 can produce NaNs or degrade quality. Local memory, latency and Mongolian retrieval quality are unmeasured. | Research-only candidate for future semantic near-duplicate detection or RAG retrieval. **Not** a generative training base and not a replacement for Qwen3.5-4B. |

The official Qwen3.8, Gemma 4, DeepSeek-V4.1-Flash, Meta and Mistral sources were also rechecked. No newly verified resource-feasible generative candidate was promoted. EmbeddingGemma 2 was not downloaded or executed, and its vendor multilingual coverage is not evidence of Mongolian benchmark quality. Any future use must pin the revision above and measure held-out Mongolian retrieval/near-duplicate performance, latency, peak memory and cost separately from chat generation.

## 2026-10-10: Mistral Large 4 public preview

Mistral officially announced Mistral Large 4 on 2026-10-06. The current status must not be mislabeled as a downloadable local integration:

| Identity | Availability on 2026-10-10 | License/revision | Runtime and RAINY decision |
| --- | --- | --- | --- |
| API model `mistral-large-4` | Paid public-preview API; 1M context. Pricing observed in official docs: promotional $0.68/M input, $0.07/M cached input and $2.09/M output tokens; prices can change. | API terms apply. No downloadable weight snapshot, immutable weight revision or weight license was available to pin. | 1.05T total, 52B active parameters and a 1.6B vision encoder. No local inference, training, Mongolian benchmark, latency, VRAM or cost run. |
| Planned `mistralai/Mistral-Large-4-1T-A52B` | Official HF page says “Upcoming release” with current ETA 2026-10-31; weights are not yet released. | Unknown until the actual artifact/model card is published; a planned ID is not an immutable revision. | Watch only. Do not design adapter compatibility or replace the retained Qwen3.5-4B baseline from vendor claims. |

Official announcement: https://mistral.ai/news/mistral-large-4/ and API documentation: https://docs.mistral.ai/models/mistral-large-4-0. Mistral states 160+ language coverage, but this is not a measured Mongolian result. Qwen, Google/Gemma, DeepSeek and Meta official sources were rechecked; no newly verified resource-feasible downloadable generative candidate displaced the retained baseline today.

## 2026-10-11: official-source recheck

Rechecked the official Qwen blog, Google Gemma release log, verified DeepSeek and Meta producer indexes, and Mistral Large 4 announcement. Google's latest listed family release remains EmbeddingGemma 2 (2026-10-06), which is already tracked as a non-generative retrieval candidate. DeepSeek's verified index still lists DeepSeek-V4.1-Flash as its most recently updated model, Meta still lists Llama 4 as current, and Mistral Large 4 weights remain a planned rather than released artifact. No new resource-feasible downloadable generative model, immutable revision or license evidence displaced the retained Qwen3.5-4B experiment. No inference, training, latency, VRAM, cost or Mongolian quality measurement was run today.

## 2026-10-12: comparison guard and producer recheck

Reopened official [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) and [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) cards, [Google releases](https://ai.google.dev/gemma/docs/releases), [DeepSeek](https://huggingface.co/deepseek-ai), [Meta](https://huggingface.co/meta-llama), and the [Mistral Large 4 planned weights](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B). Google still lists the 2026-10-06 EmbeddingGemma 2 release; Mistral's page remains Upcoming release. No new verified revision, downloadable candidate integration or replacement base was added. Existing pins/licenses remain historical snapshots, not newly fetched Hub SHAs. Open weights do not establish open training data/code; the Mistral preview API is not local weights.

The comparison gate now checks GGUF backend/version, Python, context, temperature and repetition penalty. A separate latency guard requires matching recorded hardware. The retained Qwen pair still has higher candidate exact-match accuracy on the same 24 draft questions, but its metadata cannot substantiate matched hardware: latency comparison and promotion are blocked. No weights, adapters or old results were overwritten; no training/inference/resource measurement ran today.

## 2026-10-13: official-source recheck and evaluation readiness

Reopened official [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), [Google Gemma releases](https://ai.google.dev/gemma/docs/releases), verified [DeepSeek](https://huggingface.co/deepseek-ai) and [Meta](https://huggingface.co/meta-llama) producer pages, and [Mistral Large 4 planned weights](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B). Qwen's card still identifies the 27B artifact as Apache-2.0 weights with Transformers/vLLM/SGLang support. Google's latest listed family release remains EmbeddingGemma 2 on 2026-10-06. DeepSeek still surfaces V4.1-Flash, Meta still describes Llama 4 as current, and Mistral's weight page remains an upcoming 2026-10-31 release rather than a downloadable snapshot.

No new immutable revision was pinned and no model was downloaded, integrated, trained or benchmarked today. Vendor claims are not Mongolian evidence. The new review-progress report shows the 100-case v2 packet is entirely pending, so it cannot yet support candidate promotion. Existing model pins, configs and results remain the rollback record.

## 2026-10-13 21:03 follow-up: training runtime research

Official producer pages above were reopened; no new model ID/revision or baseline promotion was established. PEFT v0.21.2 was published 2026-10-01T10:29:50Z (GitHub latest-release API), annotated tag `86b6cbda4c125337bdc0cc7fc3f2fe09c17238e1`, commit `eaa35c777c7ba554a2a3639ac9c79bb690f39a57`. Its release note fixes encoder-decoder compatibility with Transformers >=5.18.0; this is not a Mongolian causal-model quality result. [Official release](https://github.com/huggingface/peft/releases/tag/v0.21.2). No library upgrade or tested training lock was installed. The new [experimental CPU LoRA runner](CPU_TRAINING.md) is guard-tested only; real backend training/resume remains pending. Existing model pins, licenses and experiment artifacts are retained unchanged.
## 2026-10-14: checkpoint reliability and source check

Reopened the official Qwen3.8-27B card, Google releases, DeepSeek/Meta producer pages and planned Mistral Large 4 weights page. No new immutable model revision, license change or locally tested model integration was established; retained baseline/config/results are unchanged. PEFT latest-release metadata remains v0.21.2 (2026-10-01), not a newly installed training dependency. Implemented checkpoint completion/integrity in the experimental CPU LoRA runner using the official Transformers `on_save` contract. Seven synthetic filesystem fault tests do not establish real backend training/resume or Mongolian quality. Details and sources: [2026-10-14 research](../research/2026-10-14.md).

### 2026-10-14 13:03 follow-up

Reopened the same official producer pages and PEFT release notes. No new immutable model/runtime integration or measured model upgrade was established. Existing rollback pins/results remain untouched. Work instead unblocks licensed real-source review with an offline 20-document reading pack; all decisions remain pending. See [corpus review](CORPUS_REVIEW.md) and today's research for executed tests and limitations.

### 2026-10-14 17:00 follow-up

Reopened official Qwen, Google, DeepSeek, Meta, Mistral pages, PEFT releases and LoRA paper. No new immutable revision or tested runtime upgrade established; existing pins and baseline unchanged. Implemented source-grouped raw corpus splitting instead; no model inference/training claim. See today's research and [corpus partitions](CORPUS_SPLITS.md).

### 2026-10-14 21:05 follow-up

Rechecked official producer pages, PEFT releases, LoRA paper and TRL SFT dataset guidance. No new pinned artifact or tested runtime integration established; baseline unchanged. Selected work: explicit source-linked prompt/answer draft conversion, not a model upgrade. TRL format documentation does not validate this environment's absent training runtime. See [instruction drafts](INSTRUCTION_DRAFTS.md) and today's research.

## 2026-10-16 17:00 source check

Reopened official Qwen, Gemma, DeepSeek, Meta and Mistral pages, PEFT releases and
the LoRA paper. No new immutable pin, tested dependency upgrade or model promotion
was established. Existing baseline/config/results remain unchanged. Actual work:
20 new attributed corpus sources, all unreviewed; not model integration, training
or measured quality improvement. See [research](../research/2026-10-16.md).

## 2026-10-15 09:00 source and model recheck

Reopened the official Qwen3.8-27B card, Google Gemma release log, DeepSeek and Meta producer indexes, and planned Mistral Large 4 weights page. No new immutable small-model revision or locally tested runtime integration was established, so the retained baseline/config/results remain unchanged. The executable work was the first globally deduplicated 20-document daily corpus batch; it is raw unreviewed CC BY-SA 4.0 text, not model integration or measured quality gain. See [daily corpus batches](../data/mnwiki_daily/README.md) and the 2026-10-15 research note.

### 2026-10-15 13:00 follow-up

Rechecked the official producer pages. Mistral Large 4 weights remain an upcoming 2026-10-31 artifact rather than a released immutable snapshot. No newly verified resource-feasible generative model, license change, runtime integration or baseline promotion was established. The executable work was daily corpus batch 02; no inference, training or measured model-quality improvement occurred.

### 2026-10-15 17:00 follow-up

Reopened official Qwen, Gemma, DeepSeek, Meta and Mistral pages plus the LoRA paper and PEFT releases. The PEFT latest-release API still reports v0.21.2 (2026-10-01T10:29:50Z), not an installed or tested training lock. No new immutable weight revision, compatible runtime integration or baseline promotion was established. Shipped batch 03 with conservative template/email and lexical near-duplicate screening; raw collection and automated screening do not demonstrate model-quality improvement. See today's research for actual tests, resource/storage blockers and remaining human-review gates.

### October 20, 21:00 follow-up
Reopened the official producer pages, LoRA paper and PEFT releases cited in
today's research. Latest PEFT API remains v0.21.2 (2026-10-01T10:29:50Z);
no new verified model revision, tested runtime upgrade or baseline promotion.
The executable data deliverable is 40 new raw sources (daily 100/100), all
pending review, not trained weights or measured model-quality improvement.
