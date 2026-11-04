from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    filename: str
    page: int
    chunk_id: str
    quote: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    session_id: str | None = None
    document_ids: list[str] | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    session_id: str
    provider: str
    abstained: bool = False


class DocumentView(BaseModel):
    id: str
    filename: str
    status: str
    page_count: int
    chunk_count: int
    uploaded_at: str
