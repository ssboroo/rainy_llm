# Real-source corpus review / Бодит эхийн хяналт

`scripts/review_corpus.py` produces a read-only offline HTML reading pack and editable JSON decisions. It does not generate instruction answers, approve records, train a model or authenticate the reviewer.

## Use the existing 20-document pilot

Download the [HTML reading pack](../data/mnwiki_pilot/review_pack/review.html) and [pending decisions](../data/mnwiki_pilot/review_pack/review.pending.json). Open HTML locally; GitHub may show its source. It contains no JavaScript, remote fonts/images or automatic network requests. Source links require a click. The HTML does not save decisions; edit the JSON separately.

```bash
python scripts/review_corpus.py export data/mnwiki_pilot/corpus.jsonl --output-dir /path/to/new-review-pack
```

A human reviewer edits a private copy of `review.pending.json`:

1. Set the actual `reviewer` reference, `reviewer_role` to `human-reviewer`, and an ISO `reviewed_at` date.
2. Choose `accept` or `reject` for every document. Pending decisions block apply.
3. Accept only after checking Mongolian quality, facts, privacy and rights; all four checks must be JSON `true`. Record evidence or a rejection reason in `notes`.
4. Preserve IDs, fingerprints and corpus hash. Text/provenance corrections require updating the original corpus/text hash and a new packet with fresh review.

```bash
python scripts/review_corpus.py apply data/mnwiki_pilot/corpus.jsonl --reviews /private/completed-review.json --output-dir /private/new-reviewed-corpus
```

Apply exports accepted raw documents with original text/provenance/license and supplied review evidence. Rejected documents remain in the original corpus, not the output. All-rejected review produces an empty file and explicit summary. Output must be a new directory; existing work is not overwritten. I/O failure may leave a partial new directory: inspect it and retry into a different one.

This is **not instruction-format training data**, and no CPU runner training approval is emitted. Downstream transformations need renewed review, source-separated splits and evaluation-contamination checks. The reviewer identity is a supplied claim, not authenticated by the script. Never let an AI fill human-review fields. Private notes and reviewer details must stay out of public Git.

## Rights and limits

The pilot text remains Mongolian Wikipedia contributors' CC BY-SA 4.0 material. HTML copies it without rewriting, preserving attribution and article/history/revision/license links and extraction notes. See [pilot attribution](../data/mnwiki_pilot/README.md). This does not determine legal treatment of future model weights. Public Wikipedia may be in base pretraining; it is not a contamination-free benchmark.

Bounds: 1–200 documents, input maximum 10 MiB. Hash/provenance checks do not verify truth, privacy or legal rights. HTML escaping and inactive unsafe URL schemes are tested; browser rendering/accessibility QA has not been performed.

Монгол: Бодит 20 эхийг эх сурвалж, хувилбар, лицензтэй нь offline уншина. JSON шийдвэрийг **хүн өөрөө** бөглөнө. Одоогоор бүгд pending, зөвшөөрсөн эх байхгүй. Энэ бол эх баримтын хяналтын алхам; сургалт, бэлэн instruction өгөгдөл биш.
