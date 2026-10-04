# RAINY LLM

**Building a reproducible foundation for Mongolian language models.**  
**Монгол хэлний загварыг хэмжиж, сайжруулж, давтан турших боломжтой суурь төсөл.**

[English](#english) · [Монгол](#монгол) · [Data specification](docs/DATA.md) · [Dataset registry](data/source_registry.json) · [Evaluation protocol](evaluation/README.md) · [Model watch](docs/MODEL_WATCH.md) · [Roadmap](docs/ROADMAP.md)

> **Development stage: research foundation.** Dataset validation and unit tests are available. No trained RAINY weights or service have been released. A first Qwen3-0.6B CPU smoke evaluation is now recorded below.
>
> **Төлөв: судалгаа, хөгжүүлэлтийн суурь.** Өгөгдөл шалгах код болон тест бэлэн. RAINY загварыг сургаагүй, үйлчилгээ гаргаагүй. Qwen3-0.6B CPU туршилтын бодит үр дүнг доор нэмсэн.

---

## New: CPU pipeline / CPU дээр ажиллах шинэ хэрэгслүүд

[Data preparation and evaluation guide / Өгөгдөл бэлтгэл, үнэлгээний заавар](docs/PIPELINE.md)

- Unicode normalization, exact deduplication, source/prompt grouped splits and manifests.
- 24 draft Mongolian smoke questions, offline exact-match scoring, 24 local tests passed.
- Өгөгдөл цэвэрлэх, бүлэглэн хуваах, 24 асуулттай ноорог үнэлгээ, хариу оноолох код бэлэн.
- Qwen3-0.6B inference completed; no training. / Qwen3-0.6B хариулт үүсгэсэн; сургалт хийгдээгүй.

## Data quality and export / Чанар ба хөрвүүлэлт

[Quality tools guide / Хэрэглэх заавар](docs/QUALITY.md)

Available: heuristic privacy/prompt-similarity audit, split-specific chat export with provenance, and local runtime/GPU inspection. These tools do not train a model.

Бэлэн: хувийн мэдээллийн хэв шинж ба төстэй асуултын аудит, эх сурвалжийг хадгалсан chat export, төхөөрөмж шалгах команд. Аудитын үр дүнг хүн хянана.

## First measured baseline / Эхний бодит хэмжилт

- [Real-data and baseline report / Тайлан](research/2026-09-29-real-baseline.md)
- [20 attributed Wikipedia leads / Бодит өгөгдөл](data/mnwiki_pilot/README.md)
- [Reproduction guide / Давтан ажиллуулах](docs/BASELINE.md)

Qwen3-0.6B, CPU float32, non-thinking greedy, 64-token cap: **0/24 exact match**, **7 capped responses**, **120.8175 s** generation time. This small draft test and older tiny model do not establish general Mongolian ability. The collected corpus was not used for training or prompting.

Жижиг загварын энэ тохиргоо 24 асуултын яг тохирсон хариултын шалгуураар 0 авсан. Сургалт хийгдээгүй; бодит хариу, тохиргоо, хугацааг ил тод хадгалсан.

## English

### Overview

RAINY LLM is a research and engineering project focused on adapting open-weight language models for Mongolian. It brings model selection, data preparation, evaluation, and future training work into one version-controlled repository.

The intended outcome is a Mongolian assistant whose language quality and resource requirements can be measured and reproduced. The initial direction is to adapt an existing model with suitable Mongolian data, using parameter-efficient training methods such as LoRA or QLoRA after hardware and baseline performance have been established.

A final base model has not been selected. Model size, release date, or a vendor's general benchmark score alone will not determine the choice.

### Goals

- Improve Mongolian instruction following, writing, reading comprehension, and translation.
- Evaluate Cyrillic Mongolian and common Latin transliterations separately.
- Build datasets with documented sources, usage rights, and reproducible splits.
- Measure improvements against an unchanged, held-out evaluation set.
- Record model revisions, configuration, dependencies, hardware, and results.
- Prepare a path toward an inference API and Docker deployment after validation.

These are development objectives, not claims about an already trained model. Traditional Mongolian script coverage has not yet been established.

### Current capabilities

| Area | Status | What exists today |
| --- | --- | --- |
| Project documentation | Available | Roadmap, data specification, research notes, model watch |
| Dataset validation | Available | Python CLI for instruction-format JSONL |
| Duplicate detection | Basic | Repeated IDs and normalized instruction/input/output tuples within one file |
| Unit tests | Available | 24 tests covering validation, grouping, leakage checks and scoring |
| Training corpus | Pending | 20 real Wikipedia leads collected; unreviewed pilot, not a curated training corpus |
| Mongolian evaluation | Draft tooling | 24 draft smoke cases; Qwen3-0.6B CPU exact match 0/24 |
| LoRA / QLoRA training | Planned | No training runner or trained adapter |
| Inference API / Docker | Planned | No runnable service or container configuration |

The initial six tests passed during project setup. This is a recorded local result, not a live CI status badge.

### Quick start

**Requirements:** Git and Python 3.10 or newer. The current validator uses only the Python standard library. No GPU, model download, API key, or package installation is required for these commands.

Run from a terminal:

```bash
git clone https://github.com/ssboroo/rainy_llm.git
cd rainy_llm
python --version
python scripts/validate_data.py data/examples.jsonl
python -m unittest discover -s tests -v
```

Expected validator summary:

```text
records=1, errors=0
```

On systems where Python is named `python3`, replace `python` with `python3`. On Windows, `py -3` can be used when the Python launcher is installed.

These commands validate an example and run unit tests. They do not train or launch a language model.

### Dataset format

Use UTF-8 JSONL: one complete JSON object per line. The example below is shown as a single record:

```json
{"id":"example-001","instruction":"Монгол хэлээр товч мэндчил.","input":"","output":"Сайн байна уу!","source":"project-authored-format-example","license":"CC0-1.0","split":"train"}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | Non-empty record identifier, unique within the checked file |
| `instruction` | Yes | The instruction or question |
| `input` | No | Additional context; a string when present |
| `output` | Yes | The intended response |
| `source` | Yes | Traceable origin; preferably a stable document or dataset reference |
| `license` | Yes | Documented usage license or rights statement |
| `split` | Yes | `train`, `validation`, or `test` |

Validate your own file:

```bash
python scripts/validate_data.py path/to/dataset.jsonl
```

The command exits with `0` when validation succeeds and `1` when validation or file reading fails. Blank lines are skipped; a file with no records fails validation.

**Validation boundaries**

The validator checks JSON syntax, required non-empty string fields, the optional input type, split values, repeated IDs, and repeated content tuples. Content comparison applies Unicode NFC normalization and trims surrounding whitespace.

It does not verify licensing, detect personal information, score Mongolian quality, identify semantic duplicates, or compare separate files. To detect exact content duplicates across splits with this tool, records must be checked together in one file. Repeated prompts with different outputs are not treated as duplicate content.

See [the data specification](docs/DATA.md) for the current contract and limitations.

### Model selection and upgrades

The [model watch](docs/MODEL_WATCH.md) records candidates and official sources. The research snapshot dated **2026-09-29** includes Qwen3.8-27B, Qwen3.8-Flash-Next, the Gemma 4 family, and DeepSeek-V4.1-Flash. Earlier Qwen3-4B and Gemma 3-4B entries remain historical baseline candidates.

This list is a research shortlist, not a supported-model matrix or a claim that these are the best Mongolian models.

Before adopting a candidate:

1. Verify the publisher, exact model identifier, weight availability, and license.
2. Pin an immutable revision and document the tokenizer and chat template.
3. Check runtime support, total weight storage, peak memory, and training feasibility.
4. Evaluate against the same Mongolian test set and generation budget.
5. Compare quality, latency, and resource use with the existing baseline.
6. Preserve the previous configuration and results so the change can be reversed.

Open weights do not automatically imply that all training data and code are open source. Licenses are assessed per artifact. Existing adapters must not be assumed compatible with a new base model or architecture.

### Evaluation plan

| Dimension | Intended evidence |
| --- | --- |
| Mongolian language quality | Spelling, grammar, natural wording, human review |
| Instruction following | Task completion and format compliance |
| Comprehension | Answers grounded in supplied Mongolian passages |
| Translation and transliteration | Meaning preservation and script-specific accuracy |
| Reasoning | Checked answers and task-specific scoring |
| Reliability | Appropriate uncertainty and unsupported-claim analysis |
| Efficiency | Latency, throughput, peak VRAM, documented hardware |

Evaluation data must remain separate from training. Source/prompt grouping is available in the preparation tool. Near-duplicate checks remain planned. Human judgments and automated scores will be reported separately.

A lower training loss is not sufficient evidence of better assistant behavior. No numeric quality target or hardware requirement is claimed until measurements are available.

### Repository guide

| Path | Purpose |
| --- | --- |
| [`scripts/validate_data.py`](scripts/validate_data.py) | Dataset validation CLI |
| [`tests/test_validate_data.py`](tests/test_validate_data.py) | Validator unit tests |
| [`data/examples.jsonl`](data/examples.jsonl) | One format example, not a training corpus |
| [`docs/DATA.md`](docs/DATA.md) | Dataset contract and limitations |
| [`docs/MODEL_WATCH.md`](docs/MODEL_WATCH.md) | Model candidates and upgrade criteria |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Development backlog |
| [`research/2026-09-29.md`](research/2026-09-29.md) | Initial research record |

### Development roadmap

1. **Data research:** identify Mongolian sources and document licenses and provenance.
2. **Evaluation foundation:** prepare a human-reviewed initial test set and baseline runner.
3. **Model comparison:** compare feasible candidates on Mongolian quality and resource use.
4. **Training pipeline:** implement data preparation and a reproducible LoRA/QLoRA configuration.
5. **Measured experiments:** run a GPU smoke test, then compare trained adapters with the baseline.
6. **Delivery:** publish an appropriate model card and artifacts, followed by an API and Docker setup.

Dates and training costs depend on data readiness, hardware access, and measured results. See [the roadmap](docs/ROADMAP.md) for task-level progress.

### Research automation

An external ChatGPT scheduled task is configured for approximately **09:00 Asia/Ulaanbaatar each day**. Its intended workflow is to inspect repository progress, research relevant releases, implement a bounded improvement, run appropriate checks, and push changes to a development branch with a Mongolian report.

The schedule is external to this repository; cloning the project does not install it. Runs depend on scheduler availability, permissions, and connected tools. No GitHub Actions training workflow is included. Paid GPU jobs are not authorized by this schedule.

### Contributing and reproducibility

Useful contributions include source and license research, reviewed Mongolian evaluation questions, validator improvements, and reproducible experiments.

- Describe the problem and the expected change.
- Keep evaluation questions out of training data.
- Include sources and rights information for contributed data.
- Run the relevant checks and report what was actually executed.
- Record exact revisions and configurations for model experiments.
- Distinguish a proposed feature from a tested implementation.

Do not commit credentials, private data, raw corpora without redistribution rights, or large model weights. The repository ignores common environment files, raw/processed data directories, checkpoints, and model artifacts; ignore rules do not replace a content review.

### License and release status

Original project materials are subject to the ownership notice below. No general open-source license is granted; explicitly licensed files retain their own terms.

The single project-authored format example in `data/examples.jsonl` is designated CC0-1.0 in [the data specification](docs/DATA.md). That designation does not apply to the repository's code, third-party datasets, or model weights. Upstream models and datasets retain their own terms.

---

## Монгол

### Төслийн тухай

RAINY LLM нь нээлттэй жинтэй хэлний загваруудыг Монгол хэлний хэрэглээнд тохируулан хөгжүүлэх судалгаа, инженерчлэлийн төсөл юм. Загварын сонголт, өгөгдөл бэлтгэл, үнэлгээ, цаашдын сургалтын ажлыг нэг repository-д хувилбарын түүхтэйгээр хөтөлнө.

Зорилго нь Монгол хэлний чанар, ажиллуулах нөөцийн шаардлага нь хэмжигддэг, туршилтыг нь давтан хийж болдог туслах загвар хөгжүүлэх. Эхний чиглэл бол тохирох бэлэн загварыг Монгол өгөгдлөөр нэмэлт сургах бөгөөд GPU болон анхны үнэлгээг тогтоосны дараа LoRA/QLoRA аргыг туршина.

Суурь загвар эцэслэн сонгогдоогүй. Зөвхөн шинэ гарсан огноо, параметрийн хэмжээ, үйлдвэрлэгчийн ерөнхий оноонд тулгуурлан сонгохгүй.

### Үндсэн зорилтууд

- Монгол хэлээр заавар дагах, бичих, уншиж ойлгох, орчуулах чадварыг сайжруулах.
- Кирилл Монгол болон түгээмэл латин галигийг тусад нь үнэлэх.
- Эх сурвалж, ашиглах эрх, хуваарилалт нь тодорхой өгөгдөл бүрдүүлэх.
- Сургалтаас тусгаарласан тогтмол тестээр ахицыг хэмжих.
- Загварын хувилбар, тохиргоо, dependency, төхөөрөмж, үр дүнг бүртгэх.
- Чанарыг баталгаажуулсны дараа API болон Docker хувилбар бэлтгэх.

Эдгээр нь хөгжүүлэлтийн зорилтууд. Сургагдсан загварын батлагдсан чадвар гэсэн үг биш. Уламжлалт Монгол бичгийн дэмжлэг хараахан тогтоогдоогүй.

### Одоогийн боломж

| Хэсэг | Төлөв | Бэлэн байгаа зүйл |
| --- | --- | --- |
| Баримтжуулалт | Бэлэн | Төлөвлөгөө, өгөгдлийн дүрэм, судалгаа, загварын бүртгэл |
| Өгөгдөл шалгах | Бэлэн | JSONL файл шалгах Python команд |
| Давхардал илрүүлэх | Анхан шат | Нэг файл доторх ID болон агуулгын давхардал |
| Unit test | Бэлэн | Өгөгдөл, бүлэглэлт, үнэлгээ шалгах 24 тест |
| Сургалтын корпус | Бэлтгэгдээгүй | 20 бодит Wikipedia эх; хянаагүй туршилтын багц |
| Монгол үнэлгээ | Анхны хэрэгсэл | 24 ноорог асуулт; Qwen3-0.6B CPU туршилт 0/24 |
| LoRA / QLoRA сургалт | Төлөвлөсөн | Сургалтын код, сургагдсан adapter гараагүй |
| API / Docker | Төлөвлөсөн | Ажиллуулах үйлчилгээ, container тохиргоо гараагүй |

Төслийг эхлүүлэх үед зургаан тест амжилттай ажилласан. Энэ нь тухайн үеийн локал шалгалтын үр дүн бөгөөд байнга шинэчлэгддэг CI төлөв биш.

### Ажиллуулж эхлэх

**Шаардлага:** Git болон Python 3.10 буюу түүнээс шинэ хувилбар. Одоогийн шалгагч Python-ийн стандарт сан ашигладаг тул нэмэлт package, GPU, API key, модель таталт шаардлагагүй.

Терминал дээр:

```bash
git clone https://github.com/ssboroo/rainy_llm.git
cd rainy_llm
python --version
python scripts/validate_data.py data/examples.jsonl
python -m unittest discover -s tests -v
```

Жишээ файлын шалгалтын хүлээгдэх үр дүн:

```text
records=1, errors=0
```

Таны системд `python3` гэж бүртгэлтэй бол `python`-ийг `python3`-аар солино. Windows-ийн Python launcher суусан бол `py -3` ашиглаж болно.

Эдгээр команд нь өгөгдлийн жишээ болон тестийг шалгана. LLM сургах, чат загвар эхлүүлэх команд биш.

### Өгөгдлийн бүтэц

Өгөгдлийг **UTF-8 JSONL** хэлбэрээр хадгална. Нэг мөр бүр нэг бүтэн JSON object байна.

| Талбар | Заавал эсэх | Тайлбар |
| --- | --- | --- |
| `id` | Заавал | Шалгаж буй файл дотор давтагдахгүй, хоосон биш ID |
| `instruction` | Заавал | Асуулт эсвэл гүйцэтгэх заавар |
| `input` | Сонголттой | Нэмэлт нөхцөл; байвал string төрөлтэй |
| `output` | Заавал | Хүлээгдэх хариулт |
| `source` | Заавал | Мэдээллийн гарал, тогтвортой эх сурвалж |
| `license` | Заавал | Баримтжуулсан лиценз эсвэл ашиглах эрхийн тайлбар |
| `split` | Заавал | `train`, `validation`, `test` утгын аль нэг |

Өөрийн файлыг шалгах:

```bash
python scripts/validate_data.py path/to/dataset.jsonl
```

Шалгалт амжилттай бол exit code `0`, өгөгдөл эсвэл файл унших алдаатай бол `1` гарна. Хоосон мөрийг алгасана; нэг ч бичлэггүй файл алдаа болно.

Шалгагч нь JSON бүтэц, шаардлагатай талбарууд, утгын төрөл, split, давхардсан ID болон instruction/input/output гурвалын давхардлыг шалгана. Агуулгыг харьцуулахдаа Unicode NFC хэлбэрт оруулж, эхлэл төгсгөлийн хоосон зайг хасна.

Лиценз үнэхээр хүчинтэй эсэх, хувийн мэдээлэл, Монгол хэлний чанар, утгын ойролцоо давхардлыг шалгахгүй. Тусдаа файлуудыг хооронд нь харьцуулахгүй. Өөр split-ийн яг ижил агуулгыг илрүүлэхийн тулд бичлэгүүдийг нэг файлд хамтад нь шалгана. Ижил асуулт өөр хариулттай байвал агуулгын давхардал гэж тооцохгүй.

Дэлгэрэнгүйг [өгөгдлийн дүрмээс](docs/DATA.md) үзнэ үү.

### Шинэ загвар сонгох, шинэчлэх

[Загварын бүртгэлд](docs/MODEL_WATCH.md) нэр дэвшигчид болон албан ёсны эх сурвалжийг хадгална. **2026-09-29**-ний судалгаанд Qwen3.8-27B, Qwen3.8-Flash-Next, Gemma 4, DeepSeek-V4.1-Flash багтсан. Qwen3-4B болон Gemma 3-4B нь өмнөх харьцуулалтын нэр дэвшигчид хэвээр байна.

Энэ нь судлах загваруудын жагсаалт; ажилладаг интеграц эсвэл Монгол хэлээр хамгийн сайн гэсэн баталгаа биш.

Шинэ загвар нэвтрүүлэхдээ:

1. Үйлдвэрлэгч, яг model ID, жинг татах боломж, лицензийг баталгаажуулна.
2. Өөрчлөгдөхгүй revision болон tokenizer, chat template-ийг бүртгэнэ.
3. Runtime нийцэл, бүх жингийн хадгалалт, санах ой, сургалтын боломжийг шалгана.
4. Ижил Монгол тест, ижил хариулт үүсгэх нөөцийн хязгаарт туршина.
5. Чанар, хурд, нөөцийн хэрэглээг өмнөх суурьтай харьцуулна.
6. Өмнөх тохиргоо, үр дүнг хадгалж, шаардлагатай үед буцаах боломжтой шинэчилнэ.

Нээлттэй жинтэй загварын бүх код, сургалтын өгөгдөл заавал нээлттэй байдаггүй. Шинэ архитектурт хуучин adapter шууд таарна гэж үзэхгүй.

### Үнэлгээний чиглэл

| Чадвар | Шалгах зүйл |
| --- | --- |
| Монгол хэлний чанар | Зөв бичих, дүрэм, найруулга, хүний үнэлгээ |
| Заавар дагах | Даалгавар болон хүссэн форматыг мөрдөх |
| Уншиж ойлгох | Өгсөн Монгол эхэд тулгуурлан хариулах |
| Орчуулга, галиг | Утга хадгалах, бичгийн хэлбэрийн зөв байдал |
| Үндэслэл гаргах | Шалгаж болох хариу, даалгаврын оноо |
| Найдвартай байдал | Мэдэхгүйгээ илэрхийлэх, баримтгүй мэдэгдэл |
| Нөөцийн үр ашиг | Хугацаа, хурд, VRAM, төхөөрөмжийн мэдээлэл |

Үнэлгээний асуултуудыг сургалтад оруулахгүй. Эх сурвалж, ижил асуултаар бүлэглэн хуваах код бэлэн. Утгын ойролцоо давхардлыг илрүүлэх шалгалт цаашид нэмэгдэнэ. Хүний үнэлгээ, автомат оноог тусад нь тайлагнана.

Сургалтын loss буурсан нь хэрэглээний чанар сайжирсны хангалттай баталгаа биш. Бодит хэмжилтгүй үед чанарын оноо, GPU шаардлага зохиож зарлахгүй.

### Файлуудын зориулалт

| Зам | Зориулалт |
| --- | --- |
| [`scripts/validate_data.py`](scripts/validate_data.py) | Өгөгдөл шалгах команд |
| [`tests/test_validate_data.py`](tests/test_validate_data.py) | Шалгагчийн тест |
| [`data/examples.jsonl`](data/examples.jsonl) | Форматын нэг жишээ |
| [`docs/DATA.md`](docs/DATA.md) | Өгөгдлийн дүрэм, хязгаар |
| [`docs/MODEL_WATCH.md`](docs/MODEL_WATCH.md) | Загварын судалгаа, шинэчлэх шалгуур |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Хөгжүүлэлтийн ажлын жагсаалт |
| [`research/2026-09-29.md`](research/2026-09-29.md) | Анхны судалгааны тэмдэглэл |

### Хөгжүүлэлтийн дараалал

1. **Өгөгдлийн судалгаа:** Монгол эх сурвалж, лиценз, гарал үүслийг бүртгэх.
2. **Үнэлгээний суурь:** хүний хянасан эхний тест болон baseline ажиллуулах код бэлтгэх.
3. **Загварын харьцуулалт:** Монгол чадвар, нөөцийн хэрэглээг хэмжих.
4. **Сургалтын код:** өгөгдөл бэлтгэл, LoRA/QLoRA тохиргоог хэрэгжүүлэх.
5. **Туршилт:** GPU дээр жижиг шалгалт хийж, adapter-ийг суурь загвартай харьцуулах.
6. **Хэрэглээнд гаргах:** model card, тохирох файлууд, дараа нь API, Docker бэлтгэх.

Хугацаа, зардал нь өгөгдлийн бэлэн байдал, төхөөрөмж, хэмжилтийн үр дүнгээс хамаарна. Ажил тус бүрийн төлөвийг [хөгжүүлэлтийн жагсаалтаас](docs/ROADMAP.md) харна.

### Өдөр тутмын хөгжүүлэлт

ChatGPT-ийн гадаад scheduled task-ийг **Улаанбаатарын цагаар өдөр бүр 09:00 орчим** ажиллахаар тохируулсан. Repository-ийн явцыг уншиж, шинэ загвар судлан, тодорхой хүрээтэй сайжруулалт хийж, тохирох шалгалтыг ажиллуулаад хөгжүүлэлтийн branch-д push хийж Монгол хэлээр тайлагнах зорилготой.

Энэ хуваарь repository-оос тусдаа. Төслийг clone хийхэд автоматаар суухгүй. Ажиллах боломж нь scheduler, эрх болон холбогдсон хэрэгслээс хамаарна. Repository-д GPU сургалт ажиллуулах GitHub Actions workflow байхгүй. Энэ хуваарь төлбөртэй GPU ажиллуулах зөвшөөрөл болохгүй.

### Хувь нэмэр оруулах

Монгол өгөгдлийн эх сурвалж, лицензийн судалгаа, хүний хянасан тестийн асуулт, шалгах код, давтан ажиллуулах боломжтой туршилтаар хувь нэмэр оруулж болно.

- Ямар асуудал шийдэж байгааг тайлбарлах.
- Үнэлгээний өгөгдлийг сургалтаас тусгаарлах.
- Өгөгдлийн эх сурвалж, ашиглах эрхийг хавсаргах.
- Холбогдох шалгалтыг ажиллуулж, бодит үр дүнг бичих.
- Загварын туршилтын revision, тохиргоог хадгалах.
- Төлөвлөсөн боломж болон туршсан хэрэгжилтийг ялгаж тайлагнах.

Нууц түлхүүр, хувийн мэдээлэл, дахин түгээх эрхгүй корпус, том модель жинг commit хийхгүй. Ignore дүрэм нь файлын агуулгыг хянах ажлыг орлохгүй.

### Лиценз ба хувилбарын төлөв

Төслийн өөрийн бүтээсэн материалд доорх эрхийн мэдэгдэл үйлчилнэ. Нийтлэг open-source лиценз олгоогүй; тусгай лицензтэй файлын нөхцөл хэвээр байна.

`data/examples.jsonl` дахь төслийн бичсэн ганц жишээг [өгөгдлийн дүрэмд](docs/DATA.md) CC0-1.0 гэж тэмдэглэсэн. Энэ нөхцөл код, бусад dataset, модель жинд хамаарахгүй. Ашиглах суурь загвар болон өгөгдөл тус бүрийн өөрийн лицензийг мөрдөнө.

---

**Project / Төсөл:** [ssboroo/rainy_llm](https://github.com/ssboroo/rainy_llm)  
**Documentation snapshot / Баримтжуулалтын огноо:** 2026-09-29

---

## Author and project ownership / Зохиогч ба төслийн эзэмшил

**Founded, directed, and developed by [ssboroo](https://github.com/ssboroo).**

RAINY LLM is an independent project created and maintained by ssboroo. Development uses AI-assisted research and coding tools under the project owner's direction.

**Copyright © 2026 ssboroo. All rights reserved, except where a file explicitly specifies otherwise.**

This notice applies to original RAINY LLM project materials to the extent that copyright protection applies. No general license to use, modify, or redistribute those materials is granted by this notice. For permission or commercial licensing inquiries, contact the project owner through their [GitHub profile](https://github.com/ssboroo).

Third-party models, weights, datasets, libraries, and other upstream materials remain subject to their respective owners' rights and licenses. RAINY LLM does not claim authorship or ownership of those upstream materials. The explicitly designated CC0-1.0 format example retains its stated terms. This notice does not assert that every AI-assisted output is independently copyrightable.

**Төслийг үүсгэн байгуулж, чиглүүлэн хөгжүүлэгч: [ssboroo](https://github.com/ssboroo).**

RAINY LLM нь ssboroo-ийн санаачилж, удирдан хөгжүүлж буй бие даасан төсөл. Судалгаа, код боловсруулах ажилд төслийн эзэмшигчийн чиглүүлгээр AI туслах хэрэгсэл ашигладаг.

**Зохиогчийн эрх © 2026 ssboroo. Тухайн файлд өөрөөр заагаагүй бол бүх эрхийг хадгална.**

Энэ тэмдэглэгээ нь зохиогчийн эрхээр хамгаалагдах хэмжээнд RAINY LLM төслийн өөрийн бүтээсэн материалд хамаарна. Энэ мэдэгдлээр тэдгээр материалыг ашиглах, өөрчлөх, дахин түгээх нийтлэг лиценз олгохгүй. Ашиглах зөвшөөрөл болон арилжааны лицензийн асуудлаар төслийн эзэмшигчийн [GitHub профайлаар](https://github.com/ssboroo) холбогдоно уу.

Гуравдагч талын суурь загвар, модель жин, өгөгдөл, сан болон бусад эх материалын эрх нь холбогдох эзэмшигчиддээ хэвээр үлдэнэ. Тэдгээрийн лицензийг тусад нь мөрдөнө. RAINY LLM тэдгээр эх материалыг өөрөө бүтээсэн, эзэмшдэг гэж мэдэгдэхгүй. CC0-1.0 гэж тусгайлан заасан форматын жишээний нөхцөл хэвээр байна. AI-ийн оролцоотой бүх үр дүн автоматаар зохиогчийн эрхтэй гэж энэ мэдэгдлээр батлахгүй.
