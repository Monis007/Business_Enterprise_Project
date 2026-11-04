"""Small retrieval smoke benchmark. Reports retrieval presence; it is not an LLM quality score."""
import json
from pathlib import Path

from app.services.retrieval import retrieve


def main():
    dataset = json.loads((Path(__file__).parent / "golden.json").read_text(encoding="utf-8"))
    results = [{"category": row["category"], "question": row["question"],
                "retrieved": bool(retrieve(row["question"])), "expected_behavior": row["expected"]} for row in dataset]
    print(json.dumps({"questions": len(results), "retrieval_hits": sum(r["retrieved"] for r in results),
                      "results": results}, indent=2))


if __name__ == "__main__":
    main()
