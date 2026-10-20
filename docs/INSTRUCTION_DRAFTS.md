# Source-linked instruction drafts / Эхтэй холбоотой сургалтын ноорог

This offline stdlib tool converts explicitly authored extractive QA annotations
to the repository's instruction/input/output schema. It does not invent questions,
approve raw sources, authenticate reviewers or train a model.

```sh
python scripts/build_instruction_drafts.py template data/mnwiki_pilot/corpus.jsonl --splits data/mnwiki_pilot/split_manifest.json --output-dir /tmp/rainy-authoring
```

Read the source review pack, then copy/edit annotations.pending.json. Supply a
meaningful Mongolian instruction plus answer_start (inclusive) and answer_end
(exclusive), measured in Python Unicode characters, NOT UTF-8 bytes or UTF-16
browser indices. The answer is taken verbatim from the parent's text. Keep parent
ID/hash intact; use unique IDs for multiple questions. Remove unannotated entries
from a working subset; a pending entry rejects the entire build without output.

```sh
python scripts/build_instruction_drafts.py build data/mnwiki_pilot/corpus.jsonl --splits data/mnwiki_pilot/split_manifest.json --annotations /path/to/authored.json --output-dir /tmp/rainy-drafts
```

Output: instructions.draft.jsonl plus input/output hash summary. Source text,
attribution and license are preserved in provenance; the frozen parent split is
inherited, never chosen by an annotation. Changed parents or inconsistent split
manifests are rejected. Use a new output directory for every export.

Drafts remain training_ready=false even if source review is complete. An answer
being an exact substring does not establish correctness or answerability. Review
question quality, span, privacy, rights and evaluation overlap separately, then
issue the CPU runner's hash-bound human training attestation for train-only data.
Do not run prepare_data.py to repartition these derived examples. This slice does
not yet implement an instruction-review UI or a reviewed release exporter.
Frozen hashes detect accidental change, not malicious replacement of all artifacts.

## Монгол

Эхийг уншаад асуулт болон хариуны эхлэх/дуусах тэмдэгтийн байрлалыг бөглөнө.
Хариу эхээс шууд авна; асуулт, хариуг автоматаар зохиохгүй. Эх баримтын
хуваалт, лиценз, атрибуц хадгалагдана. Хоосон эсвэл хуучирсан тэмдэглэгээтэй
бол экспортлохгүй. Ноорог гарсан нь хүний хяналт эсвэл сургалтын зөвшөөрөл биш.
Одоогийн 20 эхийн загвар бүгд хоосон; баталсан асуулт-хариулт байхгүй.
