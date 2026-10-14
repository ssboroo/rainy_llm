# Raw corpus splits / Монгол эхийн хуваалт

Run from the repository root, with a new output directory:

```sh
python scripts/split_corpus.py data/mnwiki_pilot/corpus.jsonl --output-dir /tmp/rainy-new-splits
```

Stdlib only. Outputs preserve raw text, attribution, licenses and review status.
These are not SFT pairs or training approval. The original review packet stays valid.
Source strings (NFC, outer whitespace) and text (NFC, collapsed whitespace) form
connected components before assignment; transitive links stay together.
Seeded SHA-256 buckets give approximate 80/10/10 proportions, not quotas.
Empty splits are reported. Input order does not affect assignments.

The frozen pilot manifest records 20 groups: **17 train, 1 validation, 2 test**,
input/record/output hashes. Generate JSONL files with the command above.
Adding linking documents can change groups: freeze the corpus and manifest before
deriving instructions; every derived example must retain its parent's split.
URL aliases, semantic near-duplicates and pretrained-data contamination are not
detected. Wikipedia may already be in pretrained models. Two test articles are
not a representative Mongolian benchmark.

## Монгол

Нэг эх сурвалжийн хувилбар болон ижил текстийг холбоотой бүлгээр нь нэг
багцад хадгална. 20 эхийг 17/1/2 хуваасан ч хүний хяналт хүлээгдэж байгаа,
сургалтад бэлэн биш. Лиценз, эх текстийг өөрчлөхгүй. Хүний хяналт,
instruction хөрвүүлэлт, дахин хяналт шаардлагатай. LoRA runner raw schema-г
шууд ашиглахгүй. Энэ нь өгөгдөл бэлтгэл болохоос чанарын ахицын хэмжилт биш.
