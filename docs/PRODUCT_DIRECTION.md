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

## Expanded integrated backlog / Нэгдсэн нэмэлт боломжууд
Requested 2026-10-13. All rows below are planned, not shipped. Build against one shared model gateway, document store, organization identity and evaluation harness. Deliver vertical slices in dependency order rather than starting disconnected products.

| Stage | Capability / Боломж | Completion evidence |
| --- | --- | --- |
| After document search | Document comparison / Хувилбарын ялгаа | Added/deleted/changed clauses link to both document versions; dates and amounts preserved. |
| After ingestion | Spreadsheet questions / Хүснэгтээс тооцоо | Read-only table queries; calculations executed deterministically; source cells and formula shown; ambiguous columns require clarification. |
| After grounding | Structured extraction / Мэдээлэл ялгах | Invoice/product/contact fields validated against schema; unknown values remain null; original source reference retained. |
| After chat | Mongolian writing assistant / Найруулга | Formal letters, summaries, translation and terminology glossary; user can compare original and edits; factual additions marked for verification. |
| After language evaluation | Traditional Mongolian script / Монгол бичиг | Separate OCR, conversion and generation benchmarks; dictionary/human review for ambiguous mappings; never assume lossless transliteration. |
| After identity and consent | Voice input/output / Дуу хоолой | STT -> text review -> answer -> TTS; measure Mongolian word error, latency and cost; use existing RAINY Voice integration only after API contract verification. No unapproved paid calls or cloning. |
| After document answers | Meeting assistant / Хурлын туслах | Consented recording -> speaker-attributed draft transcript -> summary/action items with timestamps; user verifies speaker labels and tasks. |
| After access controls | Approved workflows / Ажлын урсгал | Draft lead/order/appointment operations; preview and explicit confirmation for external writes; idempotency, audit and error recovery. No sending messages without authorization. |
| After quality telemetry | Feedback loop / Алдаанаас сайжруулах | User corrections recorded with consent; private feedback excluded from public repo; training opt-in, license and held-out separation enforced. |
| After runtime measurement | Model routing / Загвар сонгох | Explicit offline/cloud policy; choose feasible model by measured task quality/cost; cloud use requires opt-in and approved budget; record exact model revision. |
| Before business rollout | Admin and usage / Удирдлага | Team roles, quotas, document retention/deletion, usage accounting, backups and restore test; no customer content in ordinary logs. |
| After pilot validation | Packaging / Борлуулалтын багц | Web widget, API key scope, self-host package and documentation; pricing based on observed usage/cost and pilot willingness to pay. |

### Delivery discipline
Continue the P0 local source-cited document search and working chat/API first. Then implement the extensions above as complete tested features. Do not repeatedly add roadmap-only commits when an executable slice is feasible. The four scheduled daily runs share the same backlog and remote branch history; each reports shipped code, executed tests, measured model results and remaining gaps separately.
