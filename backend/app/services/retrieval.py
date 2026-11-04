import hashlib
import math
import re
from collections import Counter

from app.store import documents

STOP = {"the", "and", "for", "that", "with", "from", "what", "when", "where", "does", "this", "are", "was", "how", "why"}


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-Z0-9_.-]+", text.lower()) if t not in STOP]


def vector(text: str, dimensions: int = 192) -> list[float]:
    vec = [0.0] * dimensions
    for token in tokens(text):
        digest = hashlib.sha256(token.encode()).digest()
        idx = int.from_bytes(digest[:4], "big") % dimensions
        vec[idx] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def retrieve(query: str, allowed_ids: list[str] | None = None, limit: int = 4) -> list[dict]:
    qtokens = set(tokens(query))
    qvec = vector(query)
    all_chunks = [c for d in documents.values() if d.status.startswith("COMPLETED")
                  and (allowed_ids is None or d.id in allowed_ids) for c in d.chunks]
    dense = sorted(all_chunks, key=lambda c: cosine(qvec, vector(c["text"])), reverse=True)[:15]
    sparse = sorted(all_chunks, key=lambda c: len(qtokens & set(tokens(c["text"]))) / max(1, len(qtokens)), reverse=True)[:15]
    ranks: dict[str, float] = {}
    refs = {c["id"]: c for c in all_chunks}
    for result_set in (dense, sparse):
        for rank, item in enumerate(result_set, 1):
            ranks[item["id"]] = ranks.get(item["id"], 0) + 1 / (60 + rank)
    # The inexpensive cross-encoder proxy favors direct query term coverage after RRF.
    ordered = sorted(ranks, key=lambda key: ranks[key], reverse=True)[:15]
    ordered.sort(key=lambda key: (len(qtokens & set(tokens(refs[key]["text"]))) / max(1, len(qtokens)), ranks[key]), reverse=True)
    result = []
    for key in ordered[:limit]:
        item = dict(refs[key])
        item["score"] = round(len(qtokens & set(tokens(item["text"]))) / max(1, len(qtokens)), 4)
        result.append(item)
    return result
