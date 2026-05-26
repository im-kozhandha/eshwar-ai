"""
Ingest markdown knowledge-base files into ChromaDB.

Run from project root:
    python -m backend.ingest
    python -m backend.ingest --reset
"""

import argparse
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.vectorstore import add_documents, reset_vectorstore
from utils.config import Settings, get_settings
from utils.paths import DOCS_DIR


def load_markdown_docs(docs_dir: Path | None = None) -> list[Document]:
    """Load all .md files from data/docs with source metadata."""
    folder = docs_dir or DOCS_DIR
    if not folder.exists():
        return []

    documents: list[Document] = []
    for path in sorted(folder.glob("**/*.md")):
        loader = TextLoader(str(path), encoding="utf-8")
        for doc in loader.load():
            doc.metadata["source"] = path.name
            doc.metadata["filepath"] = str(path.relative_to(folder.parent.parent))
            documents.append(doc)
    return documents


def chunk_documents(
    documents: list[Document],
    settings: Settings | None = None,
) -> list[Document]:
    """Split documents into small chunks for focused retrieval."""
    if not documents:
        return []

    cfg = settings or get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size,
        chunk_overlap=cfg.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)


def ingest_knowledge_base(
    docs_dir: Path | None = None,
    *,
    reset: bool = False,
    settings: Settings | None = None,
) -> dict[str, int]:
    """
    Full pipeline: load markdown → chunk → embed → persist in Chroma.

    Returns counts: files, chunks_added.
    """
    cfg = settings or get_settings()
    folder = docs_dir or DOCS_DIR

    if reset:
        reset_vectorstore(cfg)

    raw_docs = load_markdown_docs(folder)
    chunks = chunk_documents(raw_docs, cfg)
    added = add_documents(chunks, cfg)

    file_count = len({d.metadata.get("source") for d in raw_docs})
    return {"files": file_count, "chunks": added}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Eshwar knowledge base into ChromaDB")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing vectors before ingesting",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Override docs folder (default: data/docs)",
    )
    args = parser.parse_args()

    stats = ingest_knowledge_base(args.docs_dir, reset=args.reset)
    print(f"Ingested {stats['files']} file(s), {stats['chunks']} chunk(s) into ChromaDB.")


if __name__ == "__main__":
    main()
