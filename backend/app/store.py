"""Small zero-dependency in-memory repository for local assessment runs."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Document:
    id: str
    filename: str
    checksum: str
    status: str = "PROCESSING"
    page_count: int = 0
    uploaded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    chunks: list[dict[str, Any]] = field(default_factory=list)


documents: dict[str, Document] = {}
checksum_index: dict[str, str] = {}
conversations: dict[str, list[dict[str, str]]] = {}
usage: list[dict[str, Any]] = []
