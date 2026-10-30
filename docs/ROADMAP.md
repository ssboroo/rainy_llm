# Хөгжүүлэлтийн дараалал

## 2026-10-30 09:05 — legacy NumPy RNG checkpoint compatibility

- [x] Inspected the retained private 2026-10-25 step-16 archive. Its optimizer and scheduler files load with PyTorch's weights-only loader, but its legacy NumPy MT19937 ndarray in rng_state.pth was rejected because NumPy reconstruction symbols were not allowlisted.
- [x] Added a narrow, weights-only RNG loader for the exact NumPy ndarray/dtype reconstruction symbols required by that legacy payload, followed by strict Python/NumPy/Torch RNG structure validation. New checkpoints continue storing NumPy keys as primitive integers. Unknown pickle globals remain rejected.
- [x] Verified the real archived RNG state in an isolated CPU probe; also checked current list-form payloads and rejection of an untrusted custom global. This is a checkpoint-compatibility fix, not a completed training resume.
- [ ] Run uninterrupted-versus-resumed Trainer equivalence on the same pinned Torch/Transformers/PEFT stack, base snapshot, optimizer, scheduler, RNG, data and config. The inspected archive does not include base model weights, and the current host lacks Transformers/PEFT.
- [ ] Re-run a fresh multi-capability held-out draft evaluation and multiple seeds only after the training/evaluation split and model artifact are available.


## 2026-10-29 21:04 — local safetensors offline inference runner

- [x] Added scripts/ask_offline_bundle.py to run an existing verified merged safetensors bundle or base-plus-adapter bundle with exact runtime-pin checks, explicit chat-template hash verification, local-only loading, disabled remote code, deterministic bounded generation and JSON timing/token/RSS metadata.
- [x] Added a conservative available-RAM preflight and Python socket guard. The estimate is a safety threshold, not measured peak memory; Python guards are not OS-level network isolation.
- [x] Fixed the direct-execution import path after remote CI run #202 exposed a ModuleNotFoundError in the CLI help step; package imports and direct script execution are both supported.
- [x] Post-fix remote CPU CI run #204 (40880161938) passed 188 tests in 2.528 s (187 passed, one optional Torch skip); PR check run #205 also passed on the same commit. This verifies code/data checks and CLI help only, not real model inference.
- [x] Added six focused mock/unit tests covering merged inference wiring, base-plus-adapter loading, trusted bundle ID mismatch, runtime pin mismatch, insufficient RAM and socket-guard restoration.
- [ ] Run against a legally acquired real bundle and its exact runtime; validate output, tensor compatibility, memory and latency with OS-level egress disabled. Current host has no Transformers/PEFT or model artifact.
- [ ] Only after real local inference and cancellation/timeout measurement, add a local HTTP streaming API. No model-quality gain or RAINY release is implied by the mock tests.

## 2026-10-29 16:55 — local GGUF streaming CLI

- [x] Added `--stream` to the existing hash-checked local GGUF CLI. It emits one NDJSON `delta` event per text fragment and a final `done` event with finish reason, optional usage, model hash, template hash and an explicit `trained_rainy_model=false` marker.
- [x] Preserved the single-response JSON path and `--check-only`; the two modes cannot be combined. The streaming generator closes the model on normal completion and exceptions.
- [x] Added four focused tests for delta/final metadata, missing-template refusal/cleanup, NDJSON CLI output and incompatible flags. Remote CPU CI run #198 passed 182 tests in 2.550 s (181 passed, one optional Torch skip); the local isolated module also passed 7/7. These are code/mock checks, not real model inference.
- [ ] Run the stream path against a legally acquired, hash-verified GGUF with the compatible `llama-cpp-python` runtime; record real latency/RAM and verify OS-level egress isolation. Mock tests are not model inference.
- [ ] Build a local HTTP streaming API only after real GGUF inference and cancellation/timeout behavior are measured.

## 2026-10-29 offline bundle packaging

- [x] Added an executable offline bundle packager for existing full/merged safetensors artifacts and base-plus-adapter layouts. It requires an immutable upstream revision, separate weight/code license labels, explicit upstream URLs, exact runtime pins and an explicit tokenizer chat template.
- [x] Added byte/hash manifest, template identity, exclusive destination, outside-Git guard, 16 GiB default source cap, symlink/pickle-weight refusal and incomplete-publication marker. This is not adapter merging, model inference, a release or proof of legal permission.
- [x] Added 15 focused unit tests for valid layouts, file/manifest tampering, template absence, mutable revisions, dependency ranges, overwrite refusal, symlinks, pickle-style state-file refusal, Git-path refusal, source/destination overlap, byte caps and incomplete bundles.
- [x] Hardened base-plus-adapter identity: require a non-empty adapter base ID, match Hub/cache identity and immutable snapshot revision where encoded, and require explicit recorded attestations for opaque local paths. Added seven mismatch/attestation tests; this is metadata integrity, not tensor compatibility or inference.
- [x] Remote CPU CI run #187 (40799259514) passed 171 tests in 2.535 s (170 passed, one optional Torch test skipped); source-policy, draft-evaluation integrity, review-progress, document-search smoke and offline CLI interface steps passed. Local execution remains blocked by container DNS.
- [ ] Package a real model only after its local artifact and redistribution rights are confirmed. Verify actual inference with OS-level egress disabled; the current run created no model bundle and measured no model quality.
- [ ] Complete repeat-seed seed43 evidence only on a host whose child-RSS preflight returns valid samples. Do not weaken the existing training guard.
- [ ] Resume the 20-source daily collection only with a complete cross-branch source/text-hash audit; no sources were counted in this run because a trustworthy global dedup audit was unavailable.

## 2026-10-28 checkpoint restoration

- [x] Executable no-model child-RSS preflight and zero-sample-exit safety fix;
  real host probe fails closed. No guarded training or quality gain claimed.
- [x] Batches03–04:40 additional sources; day80/100,20missing,reviewed/ready0/0.
- [ ] On a host passing preflight, complete retained seed43 comparison; if this
  host remains incompatible, pursue offline artifact packaging without weakening
  training guards. Do not repeatedly download weights before preflight.

- [x] Batch02:20 additional licensed sources,48,392characters; day40/100,
  human-reviewed/training-ready0/0. No backdated collection.

- [x] Batch01:20 new licensed sources,11,779characters; day20/100,
  human-reviewed/training-ready0/0. Global dedup includes all six bulk files.

- [x] Trusted-archive restore CLI: bounded safe extraction outside Git, exclusive
  destination, checkpoint identity/hash verification; real seed42 archive restored.
- [x] Restore pinned base/runtime and perform fresh-process inference reload:
  12/12 retained predictions match,27.76s,4.60GiB peak RSS; Python network guards only.
- [ ] Complete seed43 with immediate durable retention. RSS guard remains intact;
  host child-process RSS visibility is still required for bounded training.
- [ ] Full offline export and quantization follow retained repeat-seed evidence;
  reviewed-corpus training remains separately gated.

## 2026-10-27 bounded experiment execution

- [x] Batches02–04:60 additional unique licensed sources; day80/100,63,323characters, human-reviewed/training-ready0/0. One20-source batch remains missing; no fabricated backfill.

- [x] Retained seed42 transfer experiment:16 real CPU LoRA steps, draft0/12→3/12; private final checkpoint preserved. Detected and fixed unobservable-RSS fail-open bug.
- [ ] Seed43 complete raw artifacts were lost after execution; repeat-seed evidence remains incomplete. Next: restore retained checkpoint and verify offline reload, then rerun seed43 only after immediate artifact retention is ready. Do not retrain seed42 unnecessarily.

- [x] Whole-process wall/RSS supervisor, retained logs and explicit failure reports; actual subprocess fault tests. Model execution under this wrapper remains pending.
- [x] Batch01: 20 new licensed sources, 15,888 characters; today 20/100, human-reviewed/training-ready 0/0.
- [ ] Next: restore pinned runtime and private durable checkpoint retention, then complete seed-42/43 transfer comparisons under the supervisor. Do not repeat public-smoke tuning or promote a base from one seed.
- [ ] Offline merged/base-plus-adapter export and quantization comparisons follow retained evidence; human corpus review is a separate gate.

## 2026-10-26 checkpoint continuation

- [x] 17:15 corpus batch01:20 new sources,21,400 characters; today20/100, human-reviewed/training-ready0/0. Remaining80 are not backdated or counted as completed.

- [x] Configurable hash-bound synthetic training seed and a separate frozen 12-case transfer diagnostic with lexical separation regression test.
- [ ] Complete and durably retain seed-42/43 before/after reports. Interrupted seed-42 attempt is not a completed comparison; no promotion.

- [x] Synthetic CPU session/resume CLI; actual Qwen3 four-step versus two-plus-two fresh-process equality of adapter/optimizer/scheduler/RNG/losses.
- [ ] Fresh held-out evaluation, private durable export, reviewed-data training and GPU/stochastic equivalence remain separate work. Today's source collection is still 0/100; do not count the synthetic test.

## 2026-10-25 real model execution

- [x] Pinned Qwen3-0.6B download, real offline-flagged CPU inference, 16-step synthetic LoRA, identical draft diagnostic 0/24 → 6/24, private checkpoint retention and 24/24 fresh-process reload equivalence. See [experiment](SYNTHETIC_CPU_EXPERIMENT.md).
- [ ] Highest model-first prerequisite: human-reviewed licensed instruction data plus a fresh held-out multi-capability evaluation; synthetic smoke is not a substitute.
- [ ] Bounded reviewed-data training, tested optimizer resume equivalence and repeat-seed comparison; then full licensed offline export. No automatic base promotion.

## 2026-10-25 daily corpus
- [x] Batch 01: 20 globally deduplicated history, economics, health, technology, chemistry, literature and biology sources / 22,576 characters; daily 20/100. Daily/pilot 900 plus bulk 1,570 = 2,466 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0. Frozen evaluation data unchanged.
- [x] Batch 02: 20 globally deduplicated language, technology, geography, medicine, chemistry, literature, law, mathematics and biology sources / 18,422 characters; daily 40/100. Daily/pilot 920 plus bulk 1,570 = 2,486 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0. Frozen evaluation data unchanged.
- [ ] Batches 03–05: 60 more licensed, globally deduplicated sources in three 20-document manifests.
- [ ] Human privacy/quality/license review and source-linked instruction authoring before training.

## 2026-10-24 daily corpus
- [x] Batch 01: 20 globally deduplicated culture, geography, technology, science and general-knowledge sources / 14,066 characters; daily 20/100. Daily/pilot 800 plus bulk 1,570 = 2,366 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0.
- [x] Batch 02: 20 globally deduplicated history, geography, science, culture and general-knowledge sources / 17,378 characters; daily 40/100. Daily/pilot 820 plus bulk 1,570 = 2,386 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0.
- [x] Batch 03: 20 globally deduplicated geography, culture, language, computing and science sources / 28,741 characters; daily 60/100. Daily/pilot 840 plus bulk 1,570 = 2,406 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0.
- [x] Batches 04–05: 40 globally deduplicated mathematics, science, health, technology, language, literature, economics and civics sources / 25,200 + 21,546 characters. Today 100/100 and 106,931 characters; daily/pilot 880 plus bulk 1,570 = 2,446 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0. Frozen evaluation data unchanged.
- [ ] Human privacy/quality/license review and source-linked instruction authoring before training.

## 2026-10-23 daily corpus
- [x] Batch 01: 20 infrastructure, industry, regional-history and technology sources / 55,101 characters; daily 20/100.
- [x] Batch 02: 20 geography, history, culture and sport sources / 19,706 characters; daily 40/100. Daily/pilot 720 plus bulk 1,305 = 2,024 exact-unique after excluding the known cross-branch `JavaScript` duplicate; human-reviewed/training-ready 0/0.
- [x] Batch 03: 20 science, environment, infrastructure and culture sources / 19,411 characters; daily 60/100. Daily/pilot 740 plus bulk 1,570 = 2,306 exact-unique after excluding four cross-branch duplicates; human-reviewed/training-ready 0/0.
- [x] Batches 04–05: 40 globally deduplicated general-knowledge sources / 21,456 + 14,848 characters. Today 100/100 and 130,522 characters; daily/pilot 780 plus bulk 1,570 = 2,346 exact-unique raw leads after excluding four known cross-branch duplicates; human-reviewed/training-ready 0/0.
- [ ] Human privacy/quality/license review and source-linked instruction authoring before training.

## 2026-10-22 daily corpus
- [x] Batch 01: 20 agriculture/environment/sustainability sources / 42,331 characters; today 20/100. Daily/pilot corpus 640; separately persisted bulk branch 794; combined exact-unique raw leads 1,434; human-reviewed/training-ready 0/0.
- [x] Batch 02: 20 education/transport/culture sources / 16,458 characters; today 40/100. Daily/pilot corpus 660; separately persisted bulk branch 794; combined exact-unique raw leads 1,454; human-reviewed/training-ready 0/0.
- [x] Batch 03: 20 culture/history/science sources / 21,754 characters; today 60/100. Daily/pilot corpus 680; bulk branch 1,048 rows; combined 1,727 exact-unique sources after excluding one known cross-branch `JavaScript` duplicate; human-reviewed/training-ready 0/0.
- [ ] Batches 04–05: 40 more licensed, globally deduplicated sources with frozen evaluation data unchanged.
- [ ] Human privacy/quality/license review and source-linked instruction authoring before training.

## 2026-10-21 daily corpus
- [x] Batch 01: 20 medical/anatomy/genetics sources / 19,976 characters; today 20/100. Main daily/pilot corpus 540; separately persisted bulk branch 264; combined exact-unique raw leads 804; human-reviewed/training-ready 0/0.
- [x] Batch 02: 20 law/government/economics sources / 19,837 characters; today 40/100. Main daily/pilot corpus 560; separately persisted bulk branch 264; combined exact-unique raw leads 824; human-reviewed/training-ready 0/0.
- [x] Batch 03: 20 mathematics/astronomy/earth-science/humanities sources / 27,702 characters; today 60/100. Daily-branch daily/pilot corpus 580; separately persisted bulk branch 518; combined exact-unique raw leads 1,098; human-reviewed/training-ready 0/0.
- [x] Batches 04–05: 20 humanities/culture and 20 computing/engineering sources / 20,287 + 23,097 characters. Today 100/100 and 110,899 characters; daily/pilot 620 plus bulk 518 = 1,138 exact-unique raw leads; human-reviewed/training-ready 0/0.
- [ ] Human rights/privacy/quality review and source-linked instruction authoring. Do not treat 10 AI-authored grounded QA drafts or raw collection as human approval.

## 2026-10-20 daily corpus
- [x] Batch 01: 20 chemistry-element sources / 11,214 characters; today 20/100, repository 440 raw records; human-reviewed/training-ready 0/0.
- [x] Batch 02: 20 further sources / 9,351 characters; today 40/100, repository 460. All pending; no training.
- [x] Batch 03: 20 technology/energy sources / 26,104 characters; today 60/100, repository 480 raw records; reviewed/ready 0/0.
- [x] Batches 04–05: 40 chemistry/technology/animal sources, 28,625 characters; today 100/100, repository 520; reviewed/ready 0/0. October 19's missing 20 remain historical, not backdated.
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
- [x] Checkpoint completion manifest, SHA-256 integrity, interrupted-save fault tests and safe legacy NumPy RNG restoration; exact uninterrupted-versus-resumed Trainer equivalence still pending.
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
