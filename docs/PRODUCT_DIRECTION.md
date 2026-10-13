# RAINY product direction / Бүтээгдэхүүний чиглэл
Date: 2026-10-13. Status: proposed product backlog; not shipped functionality.

## First product: Mongolian business knowledge assistant
RAINY helps employees find a grounded answer in their organization's approved documents, inspect the exact source, and prepare a draft reply. Initial customer hypothesis: Mongolian SMEs handling repeated product, service and internal-policy questions. Validate willingness to pay with a real pilot before setting prices or claiming demand.

Эхний бүтээгдэхүүн: байгууллагын зөвшөөрөгдсөн баримтаас Монгол хэлээр хариулж, ашигласан эхийг харуулдаг туслах. Хэрэглэгч асуулт асуух → баримтын холбогдох хэсэг харах → хариуны ноорог авах → өөрөө батлах урсгалтай.

Generic document chat already exists. Open WebUI documents RAG/citations and Onyx documents permission-aware connectors. RAINY's proposed differentiation must be measured Mongolian Cyrillic/Latin query handling, organization-specific workflows, and simple local deployment; none is assumed unique or proven today.

## Ordered implementation slices
| Priority | Deliverable | Acceptance evidence |
| --- | --- | --- |
| P0 | Local text/Markdown document search with source excerpts | Actual Mongolian queries return file and line references; changed/deleted documents invalidate old index entries; no-match returns empty results. No generated answer or semantic-search claim. |
| P0 | Local browser chat + inference API using a pinned model | A real request produces a streamed response; cancel, timeout and unavailable-model paths work; record hardware, runtime, tokens, elapsed time and memory. Bind locally by default. |
| P1 | Grounded document answers | Returned citations resolve to retrieved excerpts; answerable and unanswerable Mongolian cases are separately evaluated; fabricated citations rejected. Retrieved content is untrusted data, never permission to run tools. |
| P1 | PDF/DOCX ingestion, then scanned-document OCR | Preserve page/section attribution; show extraction failures; delete document and derived data together. Add parsers only with pinned, reviewed dependencies. |
| P1 | Mongolian Cyrillic/Latin query benchmark | Separate query variants and test split; compare lexical, hybrid and reranker approaches on frozen source/question sets. No guessed support claims. |
| P2 | Organization access and audit | Server-side access checks before retrieval and generation; cross-organization isolation tests; audit log avoids raw confidential document text. No public multi-user launch before this gate. |
| P2 | Business reply templates and integrations | Product FAQ, service reply and internal-policy drafts; API contract and integration test before connecting RAINY Receptionist/Studio. External actions require explicit authorization. |
| P2 | CPU/quantized and GPU deployment profiles | Docker/local setup tested from clean environment; declared memory limits, model download consent, health checks and failure recovery. No paid infrastructure without approved budget. |
| P3 | LoRA/QLoRA and domain adaptation | Licensed training data, reproducible run configuration, held-out before/after comparison and rollback; training loss alone never qualifies as success. |

## Product validation
Recruit pilot users only with owner authorization; do not contact organizations automatically.
Measure task completion, supported-answer correctness, citation correctness, abstention on unanswerable questions, time saved against manual document search, p50/p95 latency and cost per resolved task.
Define target thresholds with pilot requirements before evaluating; no invented conversion, revenue or market-size figures.
Commercial options to validate: initial setup plus support, organization subscription, or self-hosted deployment/support. Pricing waits for measured costs and customer interviews.

## Current state
Repository already has data/evaluation validators, a 100-case pending AI-authored review packet, local GGUF inference scripts and retained draft smoke runs. It does not yet establish a trained RAINY model, production SaaS or human-reviewed Mongolian quality.
Human review is needed for evaluation release, but does not block building the product slices above. Never convert AI review into human review.
Preserve ssboroo ownership notices and third-party licenses. Do not upload customer documents, secrets or model weights to this public repository.

## Sources checked 2026-10-13
- https://docs.openwebui.com/features/chat-conversations/rag/
- https://docs.openwebui.com/features/workspace/knowledge/
- https://docs.onyx.app/overview/core_features/connectors
These sources establish existing feature categories, not RAINY implementation or Mongolian performance.
