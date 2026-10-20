# Монгол өгөгдлийн өргөтгөсөн сан

Workflow: RAINY bulk Mongolian corpus. Scheduled 01:15, 05:15, 09:15, 13:15 UTC (09:15, 13:15, 17:15, 21:15 Asia/Ulaanbaatar). GitHub may delay/skip schedules. Initial run triggered by workflow-file push; manual workflow_dispatch also available.

Target: 250 accepted introductions per run, roughly 1,000 per day if enough suitable sources and requests succeed. A discovery page is finished before advancing its cursor, so a run may exceed its target by up to 39. Hard budget 100 API requests and 30-minute job timeout. Full articles are not fetched; volume is measured in accepted records and characters, not assumed tokens or gigabytes.

Persistence: branch `data/bulk-wikipedia`, directory `data/mnwiki_bulk`. Every successful run commits corpus JSONL, SHA-256 manifest and cursor together. Failed collection steps do not publish partial progress. Non-force branch pushes prevent silently overwriting competing changes. No expiring Actions artifact is the sole copy. Branch deletion remains a data-loss risk; ordinary Git backups are recommended.

The collector rebuilds an in-memory SQLite index from tracked pilot, daily and bulk JSONL files. Unique page IDs and NFC/whitespace/case-normalized text SHA-256 prevent repeated pages/text. No automatic refresh of old revisions. All namespace-0 nonredirect pages are traversed with the API continuation cursor until exhausted; completed scans do not automatically restart.

Filters: at least 200 and at most 50,000 characters, at least 65% Cyrillic among alphabetic characters, no known template markers or email patterns. These are heuristic screens, not comprehensive privacy, semantic duplicate, factual or language-quality review. SQLite is an index during collection; durable source records remain JSONL in Git. This design fits an initial Wikipedia corpus; multi-gigabyte corpora require object storage and incremental disk indexing rather than Git/in-memory rebuilds.

Each accepted record preserves source title/page/revision, revision URL, history attribution, CC-BY-SA-4.0 license link, retrieval time and text hash. New batches are unreviewed research material; `training_ready` remains false. The existing registry's 20-document pilot approval does not automatically approve these new bulk records. Do not mix them into frozen evaluation data or claim human review. Human data-rights/quality/privacy review and source-separated splits remain required before the existing training runner accepts a dataset.

Next readiness stages: inventory and inspect accepted batches, flag near-duplicates/PII, review source groups, author varied source-grounded questions, keep held-out sources excluded, then train and measure. Large raw collection alone does not improve a model.
