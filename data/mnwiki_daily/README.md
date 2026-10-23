# Daily Mongolian Wikipedia source batches

Current snapshot, 2026-10-23: batches 01–02 add 40 infrastructure, regional-history, geography, culture and sport sources / 74,807 characters.
Today: 40/100; daily-branch daily/pilot corpus: 720 raw documents; separately persisted bulk branch: 1,305 rows. Across both branches there are 2,024 exact-unique sources because the bulk branch repeats one earlier daily source (`JavaScript`); human-reviewed/training-ready: 0/0.
October 22 remains 60/100; its missing final two batches are not backdated.
October 19 remains 80/100; its incomplete earlier attempt is not counted or backdated.
October 16 and 18 completed 100/100; October 15 and 17 remain 60/100, with no backdated additions.

2026-10-23: өнөөдөр 40/100 шинэ эх, 74,807 тэмдэгт; daily branch-ийн daily/pilot 720,
тусдаа bulk branch 1,305 мөр. Bulk багцад өмнөх daily-ийн `JavaScript` нэг удаа давтагдсан тул хоёр branch-ийн нийлбэр 2,024 exact-unique эх; хүний хяналттай болон сургалтад бэлэн эх 0/0. 10-р сарын 22 нь 60/100 хэвээр, дутуу хоёр багцыг нөхөж тооцоогүй.
10-р сарын 20-нд 100/100; 19-нд 80/100; 16, 18-нд 100/100; 15, 17-ны тус бүр 40 эх дутуу хэвээр.

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

For later batches, repeat `--existing` once for every earlier corpus. On
2026-10-15, batches 01–03 contain 60 new daily documents; combined with the
20-document pilot, the repository holds 80 raw documents. None is human-reviewed
or training-ready.

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
2026-10-15-ны эхний гурван багцад 60 шинэ эх, pilot-той нийлээд 80 raw эх байна;
хүний хяналттай болон training-ready эх одоогоор 0.

## Automated screening (batch 03 onward)

The collector rejects template markers, email-like contact strings, and lexical
near-duplicates (casefolded NFC/whitespace-normalized character 5-gram multiset
Jaccard >= 0.80) against supplied prior texts and accepted current texts.
Rejections record titles/reasons, not suspect text or contact values. This is not
comprehensive PII detection, semantic similarity, factual validation or human
review. The batch-03 screening audit separately lists 6 historical template flags;
those immutable earlier rows remain unchanged and must not be used for training
without resolving review. Collection totals include raw flagged historical rows,
not approved/clean training examples.
