# Шинэ загварын бүртгэл

## 2026-10-28: restoration, no base promotion

Rechecked official Qwen3-0.6B card/report, Gemma release log, DeepSeek and Meta
repositories, Mistral inference and PEFT releases. Retain Qwen/Qwen3-0.6B at
`c1899de289a04d12100db370d81485cdf75e47ca`, Apache-2.0 open weights;
fully open training data is not established. No new release date, immutable
candidate, runtime upgrade or Mongolian advantage was established today.
The existing official tokenizer/template and tested runtime pins are unchanged.
Actual work restores the retained adapter archive, not new model inference.
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
