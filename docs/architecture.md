# EnterpriseIQ architecture

```mermaid
flowchart LR
  U[React dashboard] -->|HTTP API| A[FastAPI]
  A --> I[Ingestion and chunking]
  I --> S[(Document repository)]
  A --> R[Hybrid retrieval: lexical + vector proxy + RRF]
  R --> G[Evidence threshold and prompt grounding]
  G --> L[OpenAI / Gemini / local evidence]
  A --> C[(Conversation history)]
  A --> M[Analytics]
  Q[PostgreSQL + pgvector] -. deployment target .-> S
  X[Redis + Celery] -. async worker target .-> I
```

The current local implementation keeps data in process memory so it starts without infrastructure. The Compose file provisions PostgreSQL with pgvector and Redis, but persistence and background worker adapters remain explicit extension points. Retrieved document text is untrusted input: the model prompt separates it from instructions and the backend owns authorization and filtering decisions.
