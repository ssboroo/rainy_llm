# Хөгжүүлэлтийн дараалал

## 2026-10-20 daily corpus
- [x] Batch 01: 20 chemistry-element sources / 11,214 characters; today 20/100, repository 440 raw records; human-reviewed/training-ready 0/0.
- [x] Batch 02: 20 further sources / 9,351 characters; today 40/100, repository 460. All pending; no training.
- [ ] Remaining 60 sources with broader topics; October 19's missing 20 remain historical, not backdated.
- [ ] Human review and source-linked instructions before real CPU training. DeepSeek Flash-1017 is watch-only and outside local resource capacity; retain existing base/results.

## 2026-10-19 daily corpus
- [x] Batch 01: 20 new sources / 15,531 characters; today 20/100, repository 360 raw records. Human-reviewed/training-ready 0/0.
- [x] Batch 02: 20 plant/food-related sources / 39,485 characters; today 40/100, repository 380. Completed at 17:05 after an incomplete earlier attempt; not backdated.
- [x] Batches 03–04: 40 new sources / 40,001 characters; daily 80/100, repository 420 raw records.
- [ ] One 20-source batch remains missing after the earlier incomplete attempt; do not claim 100/100 or backdate additions. Broaden non-geography topics next.
- [ ] Human review and source-linked instruction authoring; real CPU training still needs reviewed data, runtime and durable private checkpoint storage.

## 2026-10-18 daily corpus
- [x] Batch 01: 20 new sources / 20,455 characters; 260 globally exact-unique raw records with verified hashes.
- [x] Batch 02: 20 new sources / 29,096 characters; all 280 raw records globally exact-unique and hashes verified.
- [x] Batch 03: 20 new sources / 25,724 characters; all 300 raw records globally exact-unique and hashes verified.
- [x] Batches 04–05: 20 + 20 new sources / 15,945 + 23,356 characters. Today 100/100; all 340 raw records globally exact-unique and hashes verified. Human-reviewed/training-ready 0/0.
- [ ] Human review and source-linked instructions before training. October 17 remains 60/100, not backfilled.

## 2026-10-17 daily corpus
- [x] Batch 01: 20 new sources / 20,622 characters; 200 repository-wide unique raw sources, all hashes checked.
- [x] Batch 02: 20 new sources / 20,750 characters; all 220 records globally exact-unique with verified hashes.
- [x] Batch 03: 20 new sources / 26,487 characters; all 240 records globally exact-unique with verified hashes.
- [ ] Batches 04–05: 40 more unique sources. Human-reviewed/training-ready: 0/0.
- [ ] Human rights/privacy/quality review and source-linked instruction authoring before training release.

## 2026-10-16 daily corpus
- [x] Batch 01: 20 new sources / 36,872 characters; 100 repository-wide unique raw records, all hashes checked.
- [x] Batch 02: 20 new sources / 13,522 characters; 120 repository-wide unique records, all hashes checked.
- [x] Batch 03: 20 arts/culture/education/sport sources / 22,599 characters; 140 repository-wide unique records, all hashes checked.
- [x] Batch 04: 20 new sources / 14,547 characters; batch 05: 20 new sources / 16,450 characters. Today 100/100, repository 180 unique raw sources; all hashes checked.
- [ ] Human rights/privacy/quality review and instruction conversion. Human-reviewed/training-ready: 0/0; collection target completion is not training readiness.
- 2026-10-15 remains 60/100 in the remote ledger; missing batches are not counted or backdated.

**2026-10-13 priority change:** [Бие даасан Монгол загвар](STANDALONE_MODEL.md) нь үндсэн зорилго. Licensed corpus → multi-capability base comparison → SFT/LoRA → evaluated standalone export. Document assistant бол нэмэлт integration.

## Хийгдсэн
- [x] Local TXT/Markdown lexical search: SQLite FTS5/BM25, source file/line/hash, bounded in-memory snapshot; [usage](DOCUMENT_SEARCH.md)
- [x] Repository суурь, өгөгдлийн формат
- [x] Offline corpus reading pack and hash-bound review export/apply; 20 existing documents remain pending, not training-ready. [Guide](CORPUS_REVIEW.md)
- [x] JSONL шалгалт, basic duplicate detection, unit tests

## Дараагийн ажлууд
- [x] Монгол датасетуудын эх сурвалж, лицензийн машин унших анхны shortlist ба validator (хэмжээ/lineage review үргэлжилнэ)
- [ ] Монгол хэлний хүний хянасан 100 асуулттай анхны evaluation багц (100-case v2 draft ба pending packet бэлэн)
- [x] Held-out evaluation schema, exact training-overlap check, hash report ба human-review release gate
- [x] Human-review packet, case fingerprint, checklist/evidence validator; бодит хүний review хүлээгдэж байна
- [x] Human-review progress summary; prompt задруулахгүй category/status count ба unready CI exit
- [x] Суурь inference runner ба benchmark comparison gate; revision, eval hash, decoding, latency/resource completeness шалгана
- [x] Benchmark numeric integrity: NaN/Infinity, буруу төрөл, нийцэхгүй counts болон baseline-ийн дутуу хариуг блоклох
- [x] Хадгалсан experiment integrity: raw prediction-оос оноо/нийлбэрийг дахин тооцож, evaluation/file hash-тэй тайлан хадгалах
- [x] Qwen3.5-4B pinned Q4_K_M artifact, runtime, explicit non-thinking chat template ба 24-case Монгол CPU smoke туршилт (12/24; production promotion хийгдээгүй)
- [ ] Gemma 4 жижиг хувилбарын pinned quantized artifact, runtime, chat template preflight ба бодит Монгол туршилт
- [ ] Qwen3-4B, Gemma 3-4B Монгол чанар, tokenizer үр ашиг, лиценз, нөөц харьцуулах
- [ ] GPU нэр, VRAM, төсөв тогтоох
- [x] Dataset normalization, source-based split, exact dedup болон evaluation/training character n-gram near-overlap audit (semantic detection үргэлжилнэ)
- [x] Experimental local CPU LoRA runner with assistant-only masking and resume guards; [limits](CPU_TRAINING.md). Guard tests only, no backend training yet.
- [x] Checkpoint completion manifest, SHA-256 integrity and interrupted-save fault tests; real Trainer save/resume still pending.
- [ ] Баталгаажуулсан хувилбартай сургалтын dependencies, бодит CPU LoRA resume equivalence test ба QLoRA script
- [ ] GPU smoke run, loss ба held-out evaluation; baseline-тай харьцуулах
- [ ] Model card, adapter artifact, inference API, Docker

## Чанарын шалгуур
Зөв бичих, заавар дагах, кирилл/латин галиг, орчуулга, Монгол мэдлэг, үндэслэл, мэдэхгүйгээ хэлэх чадварыг тус тус үнэлнэ. Хүний үнэлгээ болон автомат оноог салган тайлагнана. Сургалтын loss буурсан нь чат чанар сайжирсны баталгаа биш.

- [x] GGUF runtime/context/decoding comparison guard; matching hardware required for latency delta

- [x] Raw source/text connected-component partitions; pilot 17/1/2 with frozen hashes (not training approval).
- [ ] Human-reviewed instruction conversion retaining parent split; audit URL aliases and semantic overlap.

- [x] Source-linked extractive QA authoring template and draft exporter; inherited frozen splits, original provenance, no automatic approval.
- [ ] Instruction-level human review and train-only release export; actual questions/answers remain unauthored.

## 2026-10-15 daily corpus target
- [x] Batch 01: 20 new attributed CC BY-SA 4.0 documents; 19,162 characters; global exact source/page/text dedup passed.
- [x] Batch 02: 20 new attributed CC BY-SA 4.0 documents; 14,493 characters; 60/60 repository-wide exact source/page/text uniqueness passed.
- [x] Batch 03: 20 science/technology sources, 31,389 characters; template/email and lexical near-duplicate heuristic screening; 80/80 exact uniqueness.
- [ ] Batches 04–05: 40 more unique documents, each in a separate 20-document manifest.
- [ ] Resolve 6 historical template-artifact quarantine flags without silently changing frozen source/split hashes; see batch-03 screening audit.
- [ ] Human privacy/quality/rights review and semantic near-duplicate audit. Current daily human-reviewed/training-ready counts: 0/0.
