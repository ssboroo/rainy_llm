# CPU data and evaluation workflow / Өгөгдөл ба үнэлгээ

Run from the repository root with Python 3.10+. No model or GPU required.

```bash
python -m unittest discover -s tests -v
python scripts/prepare_data.py data/examples.jsonl --heldout evaluation/mn_smoke.jsonl --output-dir outputs/prepared-v1
python scripts/evaluate.py --cases evaluation/mn_smoke.jsonl --predictions outputs/predictions.jsonl --output outputs/report.json
```

The first command tests the implementation. The second prepares the single example only; empty validation/test splits are expected. The third requires real predictions that you supply; it does not generate model responses.

Prediction file format:
```json
{"id":"mn-smoke-001","output":"42"}
```

All 24 case IDs should be supplied for a complete run. Missing predictions count as incorrect, unknown/duplicate IDs fail. The scorer normalizes Unicode, whitespace and case only; explanations or punctuation may fail exact match even when the meaning is correct. Report this as a format-sensitive smoke score, never as comprehensive Mongolian ability.

## Data preparation

- Required fields: id, instruction, output, source, license; optional input defaults to empty.
- Existing split values are intentionally replaced. Do not use this command on previously frozen train/test data.
- NFC normalization and edge whitespace removal; duplicate content removed, duplicate IDs rejected.
- Sources and identical instruction/input pairs are connected into groups. Each retained group belongs to one split.
- Seeded SHA-256 hash buckets approximate 80/10/10; small datasets can have empty splits.
- Source must identify the actual document/group. A whole-corpus source value groups the entire corpus together.
- Exact duplicate removal retains the first encountered record and its provenance; keep input ordering fixed. Near duplicates, translated paraphrases and hidden upstream contamination are not detected.
- Adding records that connect groups can change assignments. Freeze outputs and their manifest for each experiment.
- --heldout rejects exact normalized instruction matches to the evaluation prompts. It is not semantic leakage detection.
- Existing output directories are refused. The manifest records input SHA-256, seed, counts, group count and warnings.
- All records are loaded into RAM. This is an initial small-dataset tool, not a streaming web-corpus pipeline.

## Монгол тайлбар

Эхний команд бүх тестийг ажиллуулна. Хоёр дахь нь өгөгдлийг цэвэрлэж, эх сурвалж болон ижил асуултаар бүлэглээд train/validation/test файл гаргана. Нэг жишээтэй учир validation/test хоосон гарах нь хэвийн.

Гурав дахь команд нь өөрийн бэлдсэн хариултыг 24 асуулттай харьцуулна. Модель хариу үүсгэхгүй. Хариулаагүй асуултыг буруу гэж тооцно. Оноо нь богино хариултын форматад мэдрэмтгий тул Монгол хэлний бүрэн чадварыг илэрхийлэхгүй.

evaluation/mn_smoke.jsonl нь AI-аар боловсруулсан анхны ноорог; хүний хэл найруулгын хяналт хийгдээгүй. Сургалтад оруулахгүй. Corpus, GPU inference, training, human review, near-duplicate detection дараагийн ажил хэвээр.
