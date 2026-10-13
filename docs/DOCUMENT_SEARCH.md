# Local document search / Баримтын хайлт

Run from the repository root with Python 3.10+ and SQLite FTS5:

```bash
python scripts/search_documents.py --documents examples/knowledge --query "Хүргэлт"
```

UTF-8 .txt/.md documents are split into 12-line passages. SQLite FTS5 Unicode tokenization and BM25 rank lexical matches; results include original excerpt, relative file path, exact line range and SHA-256. The index is built in memory each time, so changed/deleted files are reflected on the next call. No model, GPU, network or package download is needed. This is a bounded local prototype, not a semantic search or generated-answer service.

Монгол кирилл үгийг том/жижиг үсгээр хайж болно. Хариу нь эх баримтын хэсэг бөгөөд AI зохиосон хариу биш. Таарах үггүй бол results хоосон байна. Латин-кирилл хөрвүүлэлт, Монгол үгийн нөхцөл задлах, PDF/OCR, эрхийн удирдлага хараахан байхгүй. Query words are OR-matched; relevance does not establish that an answer exists.

Use a dedicated folder containing only documents you intend to search. Hidden entries and symlinks are skipped. Maximum 200 files, 1 MiB per file, 10 MiB total and 20,000 passages; invalid UTF-8 and limit failures abort without partial results. Query max 1,000 characters/32 distinct words; limit 1–20 results. Do not modify the folder concurrently: this is not a filesystem-wide atomic snapshot or a multi-user security boundary.

Output contains source text. Keep private results outside the public repository; no automatic result logging is performed. No index database is persisted. Example data is fictional. Production requires authorization, atomic ingestion, deletion handling, retrieval evaluation and grounded-generation checks.

Source: https://www.sqlite.org/fts5.html (checked 2026-10-13). SQLite documents FTS5 Unicode tokenization, MATCH and BM25. Choice here is a reproducible zero-service-cost lexical baseline, not a claim of best Mongolian retrieval quality.
