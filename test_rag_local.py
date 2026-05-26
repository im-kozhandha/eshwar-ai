"""
Local smoke test for RAG + Gemini.

Prerequisites:
  1. pip install -r requirements.txt
  2. copy .env.example .env  → set GOOGLE_API_KEY
  3. python -m backend.ingest --reset

Run from project root:
  python test_rag_local.py
  python test_rag_local.py "Why does my motor overheat?"
"""

import sys

from backend.ingest import ingest_knowledge_base
from backend.rag_pipeline import ask


def main() -> None:
    question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Why is my motor overheating?"
    )

    print("Indexing knowledge base (skip if already ingested)...")
    stats = ingest_knowledge_base(reset=False)
    print(f"  Docs: {stats['files']} file(s), {stats['chunks']} chunk(s) in store.\n")

    print(f"Question: {question}\n")
    print("Running RAG + Gemini...\n")

    result = ask(question)

    print("--- Answer ---")
    print(result["answer"])
    print("\n--- Meta ---")
    print(f"Sources: {result['sources'] or 'none'}")
    print(f"Chunks used: {result['chunks_used']}")
    print(f"Weak retrieval: {result['retrieval_weak']}")


if __name__ == "__main__":
    main()
