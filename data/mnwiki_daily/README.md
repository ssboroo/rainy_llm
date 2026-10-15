# Daily Mongolian Wikipedia source batches

These are raw article introductions retrieved through the official MediaWiki API,
not model-generated text. Each record preserves the canonical URL, revision ID,
history URL, contributor attribution, CC BY-SA 4.0 license, extraction note and
exact stored-text SHA-256. Wikimedia Terms of Use:
https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use

Each batch is capped at 20 accepted documents. Candidate titles are versioned in
`data/collection_titles/`. Collection fails without writing output unless the
requested count is reached. Supply every earlier corpus through repeated
`--existing` arguments so canonical source/page IDs and normalized exact text are
not recollected. Manifest rejection counts are part of the audit record.

```sh
python scripts/collect_wikipedia.py \
  --titles-file data/collection_titles/2026-10-15-batch-01.txt \
  --existing data/mnwiki_pilot/corpus.jsonl \
  --output-dir /tmp/rainy-batch-01 --limit 20
```

The collection target is operational throughput, not training approval. New rows
remain `unreviewed-real-source-text`; human/privacy/quality/near-duplicate review
and instruction conversion are separate gates. Wikipedia can overlap base-model
pretraining, so these documents cannot establish a contamination-free benchmark.
Do not silently replace a frozen evaluation split when later batches are added.

## Монгол

Өдөр тутмын багц бүр 20 хүртэлх бодит Монгол Wikipedia эхтэй. Эх сурвалж,
хувилбар, зохиогчдын түүх, CC BY-SA 4.0 лиценз, текстийн hash хадгалагдана.
Өмнөх бүх багцыг `--existing`-ээр өгч давхардлыг хориглоно. Цуглуулсан тоо нь
хүний хяналт, сургалтын зөвшөөрөл эсвэл загварын чанарын ахиц гэсэн үг биш.
