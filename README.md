# RAINY LLM

**Бие даан ажиллах Монгол хэлний загварыг өгөгдөл, бодит сургалт, давтан хэмжилтээр хөгжүүлэх төсөл.**

[![CPU checks](https://github.com/ssboroo/rainy_llm/actions/workflows/cpu-checks.yml/badge.svg)](https://github.com/ssboroo/rainy_llm/actions/workflows/cpu-checks.yml)
[![Bulk corpus](https://github.com/ssboroo/rainy_llm/actions/workflows/bulk-corpus.yml/badge.svg)](https://github.com/ssboroo/rainy_llm/actions/workflows/bulk-corpus.yml)

[Өгөгдөл](#өгөгдлийн-сан) · [Туршилтын үр дүн](#бодитоор-хийсэн-туршилтууд) · [Эхлэх](#ажиллуулж-эхлэх) · [Дараагийн ажил](#дараагийн-ажил) · [English](#english-summary)

> **2026-10-30-ны төлөв:** бодит CPU LoRA сургалт, checkpoint сэргээх болон шинэ процессоор inference дахин шалгах туршилт хийгдсэн. Эдгээр нь хиймэл жишээтэй, жижиг оношлох туршилтууд. **Хүний хянасан Монгол корпус дээр сургасан нийтэд ашиглуулах RAINY загвар, бэлэн чат үйлчилгээ, API/Docker release гараагүй.**

## Одоогийн боломж

| Хэсэг | Бодит төлөв |
| --- | --- |
| Өгөгдөл цуглуулах | Эх сурвалж, revision, лиценз, текстийн hash хадгалсан Wikipedia оршлууд |
| Өгөгдлийн сан | Хоёр салбарын 3,685 мөр; ID ба нормчилсон текстээр тус тус 3,681 давхардаагүй эх |
| Чанарын хяналт | Автомат шүүлт болон хүний review хэрэгслүүд бий; түүхий корпусын human-reviewed/training-ready төлөв 0 |
| Асуулт–хариулт | Эхэд тулгуурласан 10 ноорог; сургалтад баталсан багц биш |
| Үнэлгээ | 24 smoke асуулт, 100 асуулттай v2 ноорог, 12 transfer асуулттай тусдаа ноорог |
| Сургалт | Qwen3-0.6B дээр бодит CPU LoRA technical smoke; reviewed-corpus сургалт ба QLoRA туршаагүй |
| Checkpoint | Hash шалгалт, архив сэргээх, fresh-process reload; legacy NumPy RNG state-ийг safe weights-only loader-оор сэргээх боломж нэмэгдсэн; бодит Trainer resume equivalence хүлээгдэнэ |
| Offline | Local GGUF CLI and safetensors bundle runner remain experimental; no real RAINY bundle or OS-level egress test yet |
| CI | CPU код/өгөгдлийн шалгалт амжилттай; энэ нь model release-ийн баталгаа биш |
| Хэрэглэгчийн бүтээгдэхүүн | Local document search ба туршилтын CLI бий; бэлэн web chat/API/Docker байхгүй |

Эцсийн суурь загвар сонгоогүй. Нээлттэй жинтэй загварыг Монгол хэлэнд тохируулан сургах чиглэлтэй; эхнээс нь foundation model сургасан гэж мэдэгдэхгүй.

## Өгөгдлийн сан

**2026-10-28-нд салбаруудын JSONL файлыг уншиж тоолсон snapshot:**

| Байршил | Файл/багц | Мөр |
| --- | ---: | ---: |
| `main`: pilot + daily корпус | 55 | 1,100 |
| `data/bulk-wikipedia`: bulk корпус | 7 | 2,585 |
| Хоёр салбарын нийлбэр | 62 | 3,685 |
| Давхардсан 4 мөрийг хассан нийт | — | **3,681** |

ID болон Unicode NFC/хоосон зайг нормчилсон текстийн давтагдахгүй тоо хоёулаа 3,681. Энэ тоо нь утгын давхардалгүй, баримтын алдаагүй эсвэл хүний хянасан гэсэн баталгаа биш. Асуулт–хариултын ноорог болон хиймэл сургалтын жишээг эх баримтын тоонд оруулаагүй.

- [Pilot корпус](data/mnwiki_pilot)
- [Өдөр тутмын корпус](data/mnwiki_daily)
- [Тусдаа bulk салбарын корпус](https://github.com/ssboroo/rainy_llm/tree/data/bulk-wikipedia/data/mnwiki_bulk)
- [Эх сурвалжийн бүртгэл](data/source_registry.json)
- [10 асуулт–хариултын ноорог](data/instruction_annotations/pilot-qa-2026-10-21.draft.jsonl)

Wikipedia-ийн **оршил текст** цуглуулдаг; бүтэн өгүүлэл, ном, хүний хянасан instruction corpus биш. Эх бүрийн attribution, revision/history URL, CC-BY-SA-4.0 нөхцөлийг хадгална. Бусад эх сурвалж, суурь загварын эрхийг тусад нь шалгана. Pilot-ийн зөвшөөрлийг бүх bulk өгөгдөлд автоматаар хамааруулахгүй.

### Автомат цуглуулалт

[Bulk workflow](.github/workflows/bulk-corpus.yml) Улаанбаатарын цагаар **01:17, 05:17, 09:17, 13:17, 17:17, 21:17** ажиллах хуваарьтай. Нэг удаагийн зорилт 1,000 орчим эх; API-ийн хуудсыг бүтнээр дуусгах үед 39 хүртэл нэмэлт эх орж болно. Cursor-оос үргэлжилж, амжилттай татсан өгөгдөл болон төлөвийг тусдаа салбарт хамт commit хийнэ.

**2026-10-28-ны засвар:** өмнөх таталтыг зогсоосон Unicode JSONL мөр хуваалтын алдааг давтаж тестлээд зассан. Одоогийн main corpus-ийг давхардлын шалгалтад оруулж, түр алдааны bounded retry, maxlag=5 болон дууссан discovery хуудсын ахицыг хадгалах хамгаалалт нэмсэн. [Эхний нэмэгдүүлсэн ажиллуулалт](https://github.com/ssboroo/rainy_llm/actions/runs/40697296744) амжилттай: 1,015 шинэ эх, 126 logical API request, network_error=null; өгөгдөл ба cursor хадгалагдсан. Өдөрт 6,000 орчим эх нь зорилт; баталгаатай гарц биш. GitHub хуваарийг хойшлуулах эсвэл алгасах боломжтой.

[Цуглуулалтын ажиллагаа, хадгалалт, хязгаар](docs/BULK_CORPUS.md)

## Бодитоор хийсэн туршилтууд

| Туршилт | Хэмжсэн үр дүн | Утга ба хязгаар |
| --- | --- | --- |
| Суурь загварын харьцуулалт | Qwen3-4B Instruct Q4_K_M: 7/24; Qwen3.5-4B Q4_K_M: 12/24 | Жижиг public draft smoke; RAINY сургалтын үр дүн биш |
| 2026-10-25 CPU LoRA | Qwen3-0.6B, 32 хиймэл жишээ, 16 алхам; **0/24 → 6/24** | Бодит сургалт; нийт Монгол хэлний чадварын баталгаа биш |
| 2026-10-26 resume | Тасралтгүй 4 алхам ба шинэ процессоор 2+2 алхам | Adapter/optimizer/scheduler/RNG, loss ба жишээний дараалал яг таарсан |
| 2026-10-27 transfer, seed42 | 16 алхам; **0/12 → 3/12** | 12 асуулттай шинэ ноорог; хүний review, бүрэн хоёр-seed харьцуулалт дутуу |
| 2026-10-28 архив сэргээх | 13 файл, 7,023,160 байт; checkpoint seal ба identity таарсан | Adapter архив; base weights тусдаа |
| 2026-10-28 fresh-process reload | **12/12 хадгалсан хариулт таарсан**, 27.76 секунд; peak RSS 4.60 GiB | Хариу давтагдахыг шалгасан; 12/12 нь зөв хариултын оноо биш |

Өөр өөр асуулт, runtime, загвартай мөрүүдийг нэг шууд чанарын зэрэглэл болгож харьцуулахгүй. Training loss буурах, CI ногоон болох, checkpoint ачаалагдах нь хэрэглэгчийн бүх даалгаварт сайн хариулна гэсэн баталгаа биш.

Туршилтын баримтууд:

- [Суурь загварын харьцуулалт](experiments/qwen35-4b-cpu-q4km-v1/comparison.json)
- [Synthetic CPU туршилтын заавар](docs/SYNTHETIC_CPU_EXPERIMENT.md)
- [24 асуултын өмнөх/дараах үр дүн](research/results/2026-10-25-synthetic-lora/summary.json)
- [12 асуултын transfer үр дүн](research/results/2026-10-27-transfer/seed42/summary.json)
- [Архив сэргээх ба inference reload](docs/CHECKPOINT_RESTORE.md)
- [Reload-ийн бодит тайлан](research/results/2026-10-28-restore/reload.json)
- [2026-10-28-ны судалгаа, шалгалтын тэмдэглэл](research/2026-10-28.md)

### Одоогийн сургалтын саад

Процессын RAM хэрэглээг хянах supervisor нь child RSS харагдахгүй үед зогсоодог. 2026-10-28-ны бодит preflight `monitor_error`, хэмжилтийн 0 хүчинтэй дээжтэй дууссан. **0-ийг RAM хэрэглээ гэж тооцохгүй; хамгаалалтыг тойрохгүй.** Тус host дээр дараагийн bounded seed43 сургалтыг эхлүүлэхийн өмнө RAM хэмжилт ажиллах орчин хэрэгтэй.

[Preflight болон supervisor-ийн заавар](docs/BOUNDED_EXPERIMENT.md)

## Ажиллуулж эхлэх

### Код, өгөгдлийн шалгалт

Git болон Python 3.10+ хэрэгтэй. Эдгээр команд модель татахгүй, сургалт эхлүүлэхгүй.

```bash
git clone https://github.com/ssboroo/rainy_llm.git
cd rainy_llm
python scripts/validate_data.py data/examples.jsonl
python -m unittest discover -s tests -v
python scripts/validate_source_registry.py
```

Жишээ өгөгдлийн шалгалт: `records=1, errors=0`. Системээс хамаарч `python3` эсвэл `py -3` ашиглаж болно. Torch шаарддаг optional тест runtime байхгүй үед skip болно. 2026-10-29-ний шинэ runner-ийн remote CPU CI run #204-д **188 тест: 187 passed, 1 optional Torch skip** (2.528 s) болсон. [CI run](https://github.com/ssboroo/rainy_llm/actions/runs/40880161938). Шууд CLI ажиллуулах import алдааг зассаны дараах шалгалт; бодит модель inference биш. Энэ нь код/өгөгдлийн шалгалт болохоос модель сурсан эсвэл Монгол чанар сайжирсан гэсэн баталгаа биш.

### Local document search

```bash
python scripts/search_documents.py --documents examples/knowledge --query "Хүргэлт"
```

Файл, мөр, hash-тай эхийн хэсгийг хайна. Энэ нь LLM-ээр хариулт үүсгэх web chatbot биш. [Заавар](docs/DOCUMENT_SEARCH.md)

### Offline model bundle packaging (experimental)

The new offline bundle tool copies a model artifact that already exists locally; it does not download weights, merge adapters, run inference, or make an artifact a RAINY release. It supports a full/merged safetensors model directory and a base-plus-adapter directory. It requires an immutable 40-character base revision, separate weights/code license labels, explicit upstream URLs, exact runtime pins, tokenizer vocabulary and a chat template. It rejects symlinks, mutable revisions, unpinned dependencies, existing destinations, and source artifacts above the default 16 GiB cap. The output is kept outside Git and includes per-file SHA-256, size and a manifest identity hash. For base-plus-adapter bundles, the tool also checks `adapter_config.json` against the declared base ID and revision. A Hugging Face cache path must identify the exact `snapshots/<revision>`; a config containing only a Hub model ID requires `--adapter-base-revision` after independent verification; an opaque local path requires both `--adapter-base-model-id` and `--adapter-base-revision`. These attestations are recorded but do not independently prove local weight provenance.

Example for a local full model directory (replace paths and metadata only after verifying the real artifact and license):

    python scripts/export_offline_bundle.py create --source /private/model-artifact --destination /private/rainy-bundle --mode merged --model-id Qwen/Qwen3-0.6B --revision c1899de289a04d12100db370d81485cdf75e47ca --weights-license Apache-2.0 --code-license Apache-2.0 --model-card-url https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca --license-url https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/LICENSE --runtime torch==2.6.0+cpu --runtime transformers==4.51.3 --runtime accelerate==1.6.0 --runtime safetensors==YOUR_VERIFIED_VERSION --runtime tokenizers==YOUR_VERIFIED_VERSION
    python scripts/export_offline_bundle.py verify --bundle /private/rainy-bundle

For a tested runnable bundle, replace both YOUR_VERIFIED_VERSION placeholders with the exact installed versions of safetensors and the tokenizer backend used by the artifact. Include PEFT only for a base-plus-adapter runtime. The manifest records the pins supplied by the operator; it does not generate a complete transitive dependency lock.

This is a packaging and byte-integrity check only. It does not prove legal permission, tensor/runtime compatibility, model output quality, or operating-system-level network isolation. The current run did not create a real bundle because no local model artifact was available; no weights or checkpoint were added to Git.

### Offline safetensors bundle inference (experimental)

A new local runner can execute an already-packaged merged safetensors model or a base-plus-adapter bundle. It verifies the bundle against a trusted expected bundle ID, checks every declared runtime pin, refuses a conservative low-RAM preflight, loads only local files with remote code disabled, and records artifact identity, token counts, generation time, throughput and peak RSS where the platform exposes it.

Монгол: энэ runner нь өөрөө жин татахгүй. Эхлээд bundle-ийн ID-г шалгаад, итгэмжлэгдсэн ID-г ажиллуулах үед зааж өгнө.

    python scripts/export_offline_bundle.py verify --bundle /private/rainy-bundle
    python scripts/ask_offline_bundle.py --bundle /private/rainy-bundle --expected-bundle-id TRUSTED_BUNDLE_SHA256 --prompt "Монгол хэлээр товч хариул." --max-new-tokens 128 --threads 4

The expected bundle ID must be copied from a trusted verification result or other trusted channel. Runtime package versions must exactly match the manifest. The memory estimate is deliberately conservative and is not a measured peak-RSS prediction. The runner's offline environment flags and Python socket guard are defense in depth, not OS-level network isolation. No real safetensors bundle/runtime was available for this run; mock tests do not prove model compatibility or Mongolian quality. Use OS/container egress isolation before claiming fully standalone operation.

### Local GGUF CLI — туршилтын боломж

Тохирох runtime, өөрийн хууль ёсоор авсан GGUF файл болон итгэмжлэгдсэн SHA-256 хэрэгтэй.

```bash
python scripts/ask_offline.py --help
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --check-only
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --prompt "Монгол хэлээр өөрийгөө товч танилцуул."
python scripts/ask_offline.py --model /path/to/model.gguf --sha256 YOUR_TRUSTED_SHA256 --prompt "Монгол хэлээр өөрийгөө товч танилцуул." --stream
```

`--check-only` нь зөвхөн файлын hash/header шалгана. `--stream` нь текстийн хэсэг бүрийг `delta`, төгсгөлийн мэдээллийг `done` төрөлтэй тус тусын JSON мөрөөр гаргана (NDJSON); token-уудыг дуусахыг хүлээлгүй хэрэглэж болно. Энэ нь локал CLI бөгөөд HTTP API биш. Бодит GGUF жинтэй inference/offline network isolation хараахан баталгаажаагүй. [Бие даасан загварын шаардлага](docs/STANDALONE_MODEL.md)

### CPU сургалт ба checkpoint

Runtime шаардлага нь стандарт сангийн тестээс тусдаа. Сургалтанд тохирох Python/runtime, local pinned model, санах ой болон Git-ээс гадуурх хадгалалт шаардлагатай.

- [Хүний хянасан өгөгдөл шаарддаг CPU LoRA runner](docs/CPU_TRAINING.md)
- [Хиймэл жишээтэй бодит CPU туршилтыг давтах](docs/SYNTHETIC_CPU_EXPERIMENT.md)
- [Модель татахаас өмнөх resource preflight](docs/BOUNDED_EXPERIMENT.md)
- [Хадгалсан checkpoint сэргээх](docs/CHECKPOINT_RESTORE.md)

2026-10-25-ны хувийн step-16 checkpoint-ийн хуучин NumPy RNG ndarray state-ийг зөвхөн тодорхой NumPy reconstruction globals-оор, `weights_only=True` горимд сэргээх compatibility fix нэмэгдсэн. Танихгүй pickle global-ийг зөвшөөрөхгүй. Гэхдээ архивт base model weights байхгүй тул энэ нь бодит training resume эсвэл uninterrupted/resumed equivalence биш. Энэ repository-д нийтийн model weights, хувийн checkpoint архив багтаахгүй. Adapter дангаараа суурь загварыг орлохгүй. OS түвшний интернэтгүй ажиллагааны баталгаажуулалт, GGUF export болон бүрэн installation package үлдсэн.

## Өгөгдөл бэлтгэх ба үнэлэх

Instruction өгөгдөл UTF-8 JSONL хэлбэртэй. Гол талбарууд: `id`, `instruction`, `input`, `output`, `source`, `license`, `split`. Raw Wikipedia corpus нь өөр schema-тай; шууд instruction сургалт руу өгөхгүй.

1. Эх сурвалж, ашиглах эрх, хэлний чанар, баримт, хувийн мэдээллийг хянана.
2. Давхардал болон evaluation overlap-ийг шалгаж, эх сурвалжаар train/validation/test-ийг тусгаарлана.
3. Монгол заавар, хариултыг бэлтгэн хянаж, hash-тай review evidence хадгална.
4. Сургалтын өмнөх/дараах хариуг ижил тест, decoding тохиргоогоор хэмжинэ.
5. Хүний үнэлгээ, автомат оноо болон хурд/санах ойг тусад нь тайлагнана.

AI-аар хийсэн шалгалтыг хүний review гэж тэмдэглэхгүй. Одоогийн v2 багцын 100 асуулт бүгд pending; production benchmark биш.

[Өгөгдлийн дүрэм](docs/DATA.md) · [Pipeline](docs/PIPELINE.md) · [Corpus review](docs/CORPUS_REVIEW.md) · [Instruction drafts](docs/INSTRUCTION_DRAFTS.md) · [Үнэлгээ](evaluation/README.md) · [V2 review](evaluation/MN_V2_REVIEW.md)

## Дараагийн ажил

- [x] Bulk цуглуулагчийн Unicode JSONL алдааг засаж, 1,015 шинэ эхийн бодит таталт/хадгалалтаар баталсан.
- [ ] Дөрвөн historical cross-branch duplicate болон үлдсэн чанарын flag-уудыг шийдэх.
- [ ] Хүний хянасан, эх сурвалж/лиценз нь баталгаатай Монгол сургалтын сан бүрдүүлэх.
- [ ] Асуулт–хариултыг төрөлжүүлж, 100 асуулттай v2 үнэлгээг хүнээр хянуулах.
- [ ] Child RSS хэмждэг орчинд seed43 туршилт хийж, хадгалсан хоёр-seed үр дүнг харьцуулах.
- [ ] Reviewed corpus дээр LoRA сургаж, held-out чанар болон regression хэмжих.
- [ ] Хувилбартай adapter/model card, export, offline package ба OS сүлжээ тусгаарлах туршилт гаргах.
- [ ] Баталгаажсан загварт local chat/API, дараа нь Docker ба хэрэглэгчийн интерфейс бэлтгэх.

[Дэлгэрэнгүй roadmap](docs/ROADMAP.md) · [Загварын судалгаа](docs/MODEL_WATCH.md)

## Төслийн бүтэц

| Зам | Зориулалт |
| --- | --- |
| `data/` | Raw корпус, эх сурвалжийн бүртгэл, instruction ноорог |
| `evaluation/` | Үнэлгээний ноорог, review packet, overlap тайлан |
| `scripts/` | Цуглуулалт, шалгалт, сургалт, checkpoint, inference хэрэгслүүд |
| `tests/` | Кодын зан төлөв болон хамгаалалтын тестүүд |
| `experiments/` | Суурь загваруудын хадгалсан харьцуулалт |
| `research/results/` | Бодит туршилтын оноо, хариу, hash ба хэмжилт |
| `research/` | Огноотой ажлын тэмдэглэл |
| `docs/` | Давтан ажиллуулах заавар, шийдэл, хязгаар |
| `.github/workflows/` | CPU шалгалт ба bulk цуглуулалтын хуваарь |

## English summary

RAINY LLM is a Mongolian model-adaptation research project directed by **ssboroo**. As of **2026-10-30**, the repository contains real CPU LoRA experiments on synthetic fixtures, exact checkpoint-resume comparisons, archive restoration, fresh-process inference replay, experimental offline-bundle packaging and a mock-tested safetensors offline runner, plus a safe legacy NumPy RNG-state loader. It has **not** released a production Mongolian model trained on a human-reviewed corpus or a real RAINY model bundle.

The inspected main and bulk branch snapshots contain **3,685 raw Wikipedia lead records / 3,681 exact-unique records**. All remain unapproved for corpus training. Bulk collection now targets 1,000 records six times daily. The Unicode JSONL parsing failure was reproduced and fixed, with bounded retries and current-main deduplication added. The daily target is not a delivery guarantee.

Synthetic Qwen3-0.6B experiments measured **0/24 → 6/24** and, in a separate 12-case draft diagnostic, **0/12 → 3/12**. Reload reproduced **12/12 retained predictions**, which measures reproducibility rather than correctness. These results do not establish general Mongolian fluency or production readiness.

## Зохиогч, эрх ба лиценз

**Төслийг үүсгэн байгуулж, чиглүүлэн хөгжүүлэгч: [ssboroo](https://github.com/ssboroo).**

RAINY LLM нь ssboroo-ийн санаачилж, удирдан хөгжүүлж буй бие даасан төсөл. Судалгаа, код боловсруулах ажилд төслийн эзэмшигчийн чиглүүлгээр AI туслах хэрэгсэл ашигладаг.

**Copyright © 2026 ssboroo. All rights reserved, except where a file explicitly specifies otherwise.**

Төслийн өөрийн бүтээсэн материалд нийтлэг open-source лиценз олгоогүй. Тухайн файлд тусгайлан заасан нөхцөл хэвээр үйлчилнэ. `data/examples.jsonl` дахь форматын нэг жишээ CC0-1.0; энэ нь код, бусад dataset эсвэл модель жинд хамаарахгүй. Ашиглах зөвшөөрөл, арилжааны лицензийн асуудлаар эзэмшигчтэй GitHub профайлаар холбогдоно уу.

Гуравдагч талын суурь загвар, жин, өгөгдөл, сангийн эрх холбогдох эзэмшигчиддээ үлдэнэ. Тэдгээрийн лицензийг тусад нь мөрдөнө; RAINY LLM тэдгээрийг өөрөө бүтээсэн гэж мэдэгдэхгүй. AI-ийн оролцоотой бүх үр дүн автоматаар зохиогчийн эрхтэй гэж энэ мэдэгдлээр батлахгүй.

---

**Баримтжуулалтын огноо:** 2026-10-30 (Asia/Ulaanbaatar). Тоон үзүүлэлтүүд нь шалгасан snapshot; бодит шинэчлэлтийг manifest, огноотой судалгааны тайлан болон Actions-оос харна.


## 2026-10-30: fresh-process checkpoint equivalence (technical smoke)

A new optional CPU experiment validates that the repository's sealed checkpoint helpers can resume a tiny deterministic PyTorch network in a fresh Python process. The four-step run is split after step two. Model tensors, optimizer, scheduler, Python/NumPy/Torch RNG and trainer history matched **exactly (5/5)**. Measured on Python 3.13.5, Torch 2.10.0+cpu, NumPy 2.3.5 and safetensors 0.7.0, one CPU thread; fresh-process wall time 7.1075 s including interpreter startup; resume training itself 0.0040 s; parent/child peak RSS 328,832 / 330,240 KiB.

This is a technical state-restore test with eight synthetic numeric rows. It is **not Qwen/PEFT LoRA training, a Mongolian benchmark, or a model-quality improvement**. The actual Qwen Trainer resume still requires the missing base weights and the exact pinned training runtime. See [checkpoint equivalence instructions](docs/CHECKPOINT_RESUME_EQUIVALENCE.md) and [the 2026-10-30 research log](research/2026-10-30.md).


Remote GitHub Actions PR run [#223](https://github.com/ssboroo/rainy_llm/actions/runs/41007166769) passed after this push: **193 tests, 189 passed, 4 optional skips**. All validation, source-policy, draft-evaluation, review-progress, document-search and offline-CLI steps succeeded. This CI run did not perform model training or model inference.