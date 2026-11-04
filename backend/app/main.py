import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, Citation, DocumentView
from app.services.ingestion import ingest
from app.services.llm import generate
from app.services.retrieval import retrieve
from app.store import conversations, documents, usage

app = FastAPI(title=settings.app_name, version="0.1.0", description="Grounded enterprise document intelligence")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def view(doc):
    return DocumentView(id=doc.id, filename=doc.filename, status=doc.status, page_count=doc.page_count,
                        chunk_count=len(doc.chunks), uploaded_at=doc.uploaded_at)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


@app.post("/api/documents/upload", response_model=DocumentView, status_code=202)
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        doc, duplicate = ingest(file.filename or "upload.txt", content)
        return view(doc)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/documents", response_model=list[DocumentView])
async def list_documents():
    return [view(d) for d in sorted(documents.values(), key=lambda x: x.uploaded_at, reverse=True)]


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    doc = documents.pop(document_id, None)
    if not doc:
        raise HTTPException(404, "Document not found")
    from app.store import checksum_index
    checksum_index.pop(doc.checksum, None)
    return {"deleted": document_id}


@app.post("/api/chat/query", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    history = conversations.setdefault(session_id, [])
    query = request.question
    # Resolve simple conversational references using recent user context.
    if history and any(word in query.lower() for word in ("that", "it", "those", "they", "there")):
        prior = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        query = f"{prior}. Follow-up: {query}"
    chunks = retrieve(query, request.document_ids)
    if chunks and max(c["score"] for c in chunks) < settings.min_evidence_score:
        answer_text, provider, abstained = "Insufficient documentation available to answer this question.", "evidence-filter", True
        chunks = []
    else:
        answer = await generate(query, history, chunks)
        answer_text, provider, abstained = answer.content, answer.provider, not bool(chunks)
    history.extend([{"role": "user", "content": request.question}, {"role": "assistant", "content": answer_text}])
    citations = [Citation(document_id=c["document_id"], filename=c["filename"], page=c["page"], chunk_id=c["id"],
                          quote=c["text"][:360], score=c["score"]) for c in chunks]
    usage.append({"timestamp": datetime.now(timezone.utc).isoformat(), "provider": provider})
    return ChatResponse(answer=answer_text, citations=citations, session_id=session_id, provider=provider, abstained=abstained)


@app.post("/api/agents/report")
async def report(request: ChatRequest):
    # Deterministic bounded search -> analysis -> synthesis workflow.
    evidence = retrieve(request.question, request.document_ids, limit=8)
    if not evidence:
        return {"report": "Insufficient documentation available.", "steps": ["search", "abstain"], "citations": []}
    findings = [{"source": c["filename"], "page": c["page"], "excerpt": c["text"][:300]} for c in evidence]
    response = await generate("Produce an executive report using only these findings: " + request.question, [], evidence)
    return {"report": response.content, "steps": ["search_knowledge_base", "analyze_document_findings", "generate_structured_report"],
            "iteration_count": 1, "citations": findings}


@app.get("/api/analytics")
async def analytics():
    providers = {}
    for event in usage:
        providers[event["provider"]] = providers.get(event["provider"], 0) + 1
    return {"documents": len(documents), "chunks": sum(len(d.chunks) for d in documents.values()),
            "queries": len(usage), "provider_usage": providers,
            "average_latency_ms": 0, "note": "Latency instrumentation is a deployment follow-up."}
