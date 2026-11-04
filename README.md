# EnterpriseIQ

Enterprise document intelligence starter built from the supplied technical roadmap. It includes a FastAPI service, a React dashboard, local document ingestion, hybrid lexical/semantic retrieval, grounded answers with citations, conversation history, provider adapters, a guarded analysis workflow, an evaluation set, and container configuration.

## Quick start

Requirements: Python 3.11+, Node.js 20+, and (optionally) Docker Compose.

1. Copy `backend/.env.example` to `backend/.env` and add model API keys if desired.
2. In one terminal: `cd backend && python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
3. In another terminal: `cd frontend && npm install && npm run dev`
4. Open the Vite URL, upload TXT/MD/CSV/PDF files, then ask questions. API docs are at `http://localhost:8000/docs`.

For containerized services, use `docker compose up --build`. The API currently uses a lightweight SQLite repository for zero-setup local use; the compose file also starts PostgreSQL/pgvector and Redis as the production-oriented service baseline. Configure `DATABASE_URL` and `REDIS_URL` when wiring the repository/worker to those services.

## What is implemented

- Upload validation, 25 MB limit, SHA-256 deduplication, text extraction, overlapping chunks and asynchronous-compatible status tracking.
- Hybrid retrieval combining token overlap and deterministic hashing-vector cosine similarity, reciprocal rank fusion, and citations carrying document and page information.
- Evidence threshold and abstention behavior; retrieved content is marked untrusted in the generation prompt.
- OpenAI and Gemini-compatible provider adapters with primary/fallback selection; a local evidence-grounded answer path works without keys.
- A bounded analysis/report workflow, session memory, basic analytics, and a 20-item evaluation dataset.
- React dashboard for uploads, document status, chat, citations, and system metrics.

## Important limits

This is a runnable assessment implementation, not a deployed service. SQLite and deterministic local retrieval make the first run self-contained. For larger datasets, replace the repository with PostgreSQL/pgvector, run extraction/embedding in Celery workers, configure real embedding and reranking models, enable authentication/tenant authorization, and deploy using the supplied container files. Do not expose this local development configuration to the public internet.

## Layout

See `docs/architecture.md` and `docs/implementation-notes.md`. Run the benchmark with `python -m app.evaluation.run` from `backend/`.
