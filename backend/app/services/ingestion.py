import csv
import hashlib
import io
import re
import uuid
from pathlib import Path

from app.store import Document, checksum_index, documents

MAX_FILE_BYTES = 25 * 1024 * 1024
ALLOWED = {".pdf", ".txt", ".md", ".csv"}


def extract_pages(filename: str, content: bytes) -> list[str]:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError("Supported file types: PDF, TXT, MD, CSV")
    if suffix == ".pdf":
        try:
            import fitz
            with fitz.open(stream=content, filetype="pdf") as pdf:
                return [page.get_text("text") for page in pdf]
        except ImportError as exc:
            raise ValueError("PDF support requires PyMuPDF") from exc
    text = content.decode("utf-8-sig", errors="replace")
    if suffix == ".csv":
        rows = csv.reader(io.StringIO(text))
        return [" | ".join(cell.strip() for cell in row) for row in rows if any(cell.strip() for cell in row)]
    return text.split("\f")


def split_chunks(text: str, size: int = 900, overlap: int = 120) -> list[str]:
    words = re.findall(r"\S+", text)
    if not words:
        return []
    step = max(1, size - overlap)
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


def ingest(filename: str, content: bytes) -> tuple[Document, bool]:
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("File exceeds the 25 MB limit")
    checksum = hashlib.sha256(content).hexdigest()
    existing_id = checksum_index.get(checksum)
    if existing_id:
        return documents[existing_id], True
    pages = extract_pages(filename, content)
    doc = Document(id=str(uuid.uuid4()), filename=Path(filename).name, checksum=checksum, page_count=len(pages))
    for page_no, page_text in enumerate(pages, 1):
        for idx, chunk in enumerate(split_chunks(page_text)):
            doc.chunks.append({"id": f"{doc.id}-{page_no}-{idx}", "document_id": doc.id,
                               "filename": doc.filename, "page": page_no, "text": chunk})
    doc.status = "COMPLETED" if doc.chunks else "COMPLETED_EMPTY"
    documents[doc.id] = doc
    checksum_index[checksum] = doc.id
    return doc, False
