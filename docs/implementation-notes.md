# Implementation notes and assessment roadmap

## Completed foundation

The service validates file extensions and size, computes a SHA-256 checksum, extracts text from PDF/TXT/MD/CSV, records page and filename metadata, and divides text into overlapping windows. Duplicate byte-identical uploads return the existing document. Retrieval combines a deterministic hashed-vector proxy with sparse token overlap, merges ranks using reciprocal rank fusion, and selects a small evidence set. Responses include citation objects with source filename, page, excerpt, and score. When evidence does not clear the configured minimum, the API abstains. When provider credentials are absent or a provider call fails, a local evidence-only answer is returned.

## Roadmap to production parity

1. Replace process memory with PostgreSQL models and Alembic migrations; add pgvector and full-text indexes.
2. Move extraction and embedding to Celery/Redis jobs with retries, distributed idempotency locks, and progress events.
3. Use a real embedding endpoint and a trained cross-encoder reranker; tune confidence cutoffs on representative evaluation data.
4. Add account authentication, organization membership, tenant-scoped queries, audit records, and rate limits before handling confidential data.
5. Implement LangGraph nodes and tool schemas with explicit recursion and wall-clock limits; the current report endpoint is a bounded sequential workflow.
6. Add measured latency/token-cost telemetry and a golden-set runner that calculates retrieval precision/recall, faithfulness, citation correctness, and abstention quality. The provided 20 prompts are scaffolding, not measured pass results.
7. Add streaming responses and ingestion progress updates, then configure Vercel/Render or equivalent hosting with secrets stored outside source control.

## Deliberate scope notes

The local vector implementation is deterministic and dependency-light; it is not a substitute for a learned embedding model. The initial repository is in-memory, so restart clears documents. Authentication and tenant boundaries are not yet implemented; do not expose this build publicly until they are. These boundaries are made visible rather than presented as completed enterprise controls.
