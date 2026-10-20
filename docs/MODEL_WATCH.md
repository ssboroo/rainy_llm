# Шинэ загварын бүртгэл

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
