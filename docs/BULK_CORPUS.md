# Монгол өгөгдлийн өргөтгөсөн сан

Workflow: RAINY bulk Mongolian corpus. Scheduled 01:17, 05:17, 09:17, 13:17, 17:17, 21:17 UTC (01:17, 05:17, 09:17, 13:17, 17:17, 21:17 Asia/Ulaanbaatar, with the UTC+8 day offset). GitHub may delay/skip schedules. Initial run triggered by workflow-file push; manual workflow_dispatch also available.

Target: 1,000 accepted introductions per run, roughly 6,000 per day if enough suitable sources and requests succeed. A discovery page is finished before advancing its cursor, so a run may exceed its target by up to 39. Hard budget 500 logical API requests (each may retry up to four times) and 30-minute job timeout. Full articles are not fetched; volume is measured in accepted records and characters, not assumed tokens or gigabytes.

Persistence: branch `data/bulk-wikipedia`, directory `data/mnwiki_bulk`. Every successful run commits corpus JSONL, SHA-256 manifest and cursor together. On a later network failure, completed discovery pages can be committed with status=partial and a network_error; the failing page's cursor is not advanced. Failure before the first completed page returns nonzero and publishes no progress. Non-force branch pushes prevent silently overwriting competing changes. No expiring Actions artifact is the sole copy. Branch deletion remains a data-loss risk; ordinary Git backups are recommended.

The collector rebuilds an in-memory SQLite index from the current main branch's pilot/daily snapshot and persistent bulk JSONL files. Unique page IDs and NFC/whitespace/case-normalized text SHA-256 prevent repeated pages/text. No automatic refresh of old revisions. All namespace-0 nonredirect pages are traversed with the API continuation cursor until exhausted; completed scans do not automatically restart.

Filters: at least 200 and at most 50,000 characters, at least 65% Cyrillic among alphabetic characters, no known template markers or email patterns. These are heuristic screens, not comprehensive privacy, semantic duplicate, factual or language-quality review. SQLite is an index during collection; durable source records remain JSONL in Git. This design fits an initial Wikipedia corpus; multi-gigabyte corpora require object storage and incremental disk indexing rather than Git/in-memory rebuilds.

Each accepted record preserves source title/page/revision, revision URL, history attribution, CC-BY-SA-4.0 license link, retrieval time and text hash. New batches are unreviewed research material; `training_ready` remains false. The existing registry's 20-document pilot approval does not automatically approve these new bulk records. Do not mix them into frozen evaluation data or claim human review. Human data-rights/quality/privacy review and source-separated splits remain required before the existing training runner accepts a dataset.

Next readiness stages: inventory and inspect accepted batches, flag near-duplicates/PII, review source groups, author varied source-grounded questions, keep held-out sources excluded, then train and measure. Large raw collection alone does not improve a model.

## 2026-10-28 reliability update

Fixed a reproduced Unicode JSONL bug: str.splitlines incorrectly split legal U+0085/U+2028/U+2029 characters inside JSON strings. LF-only record boundaries preserve those sources without deleting or repairing original data. Added regression tests. Requests remain serial, wait 0.5s before each attempt, send maxlag=5, and honor bounded numeric Retry-After with exponential backoff for rate limits/temporary failures; permanent errors stop. Pauses over 120s or nonnumeric Retry-After stop for a later run. Official references: https://www.mediawiki.org/wiki/API:Etiquette and https://www.mediawiki.org/wiki/Manual:Maxlag_parameter .

The increased quota is a target, not a guarantee. The previous 2,666-source snapshot remains historical. Newly collected data remains raw and training_ready=false; no human review or model-quality gain is claimed.
