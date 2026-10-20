# Хөгжүүлэлтийн дараалал

## Хийгдсэн
- [x] Repository суурь, өгөгдлийн формат
- [x] JSONL шалгалт, basic duplicate detection, unit tests

## Дараагийн ажлууд
- [x] Монгол датасетуудын эх сурвалж, лицензийн машин унших анхны shortlist ба validator (хэмжээ/lineage review үргэлжилнэ)
- [ ] Монгол хэлний хүний хянасан 100 асуулттай анхны evaluation багц
- [x] Held-out evaluation schema, exact training-overlap check, hash report ба human-review release gate
- [x] Human-review packet, case fingerprint, checklist/evidence validator; бодит хүний review хүлээгдэж байна
- [x] Суурь inference runner ба benchmark comparison gate; revision, eval hash, decoding, latency/resource completeness шалгана
- [x] Benchmark numeric integrity: NaN/Infinity, буруу төрөл, нийцэхгүй counts болон baseline-ийн дутуу хариуг блоклох
- [x] Хадгалсан experiment integrity: raw prediction-оос оноо/нийлбэрийг дахин тооцож, evaluation/file hash-тэй тайлан хадгалах
- [x] Qwen3.5-4B pinned Q4_K_M artifact, runtime, explicit non-thinking chat template ба 24-case Монгол CPU smoke туршилт (12/24; production promotion хийгдээгүй)
- [ ] Gemma 4 жижиг хувилбарын pinned quantized artifact, runtime, chat template preflight ба бодит Монгол туршилт
- [ ] Qwen3-4B, Gemma 3-4B Монгол чанар, tokenizer үр ашиг, лиценз, нөөц харьцуулах
- [ ] GPU нэр, VRAM, төсөв тогтоох
- [ ] Dataset normalization, source-based split, near-duplicate detection
- [ ] Баталгаажуулсан хувилбартай сургалтын dependencies ба LoRA/QLoRA script
- [ ] GPU smoke run, loss ба held-out evaluation; baseline-тай харьцуулах
- [ ] Model card, adapter artifact, inference API, Docker

## Чанарын шалгуур
Зөв бичих, заавар дагах, кирилл/латин галиг, орчуулга, Монгол мэдлэг, үндэслэл, мэдэхгүйгээ хэлэх чадварыг тус тус үнэлнэ. Хүний үнэлгээ болон автомат оноог салган тайлагнана. Сургалтын loss буурсан нь чат чанар сайжирсны баталгаа биш.
