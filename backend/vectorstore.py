"""ChromaDB vector store and local sentence-transformer embeddings."""

import os

# Quieter logs on Windows (telemetry bug with some chromadb/posthog versions)
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from utils.config import Settings, ensure_data_dirs, get_settings

_embeddings: Embeddings | None = None
_vectorstore: Chroma | None = None


def get_embeddings(settings: Settings | None = None) -> Embeddings:
    global _embeddings
    if _embeddings is None:
        cfg = settings or get_settings()
        _embeddings = HuggingFaceEmbeddings(
            model_name=cfg.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def get_vectorstore(
    settings: Settings | None = None,
    *,
    force_new: bool = False,
) -> Chroma:
    """Return a persisted Chroma collection (creates empty store if missing)."""
    global _vectorstore
    if _vectorstore is not None and not force_new:
        return _vectorstore

    cfg = settings or get_settings()
    ensure_data_dirs()
    cfg.chroma_persist_dir.mkdir(parents=True, exist_ok=True)

    _vectorstore = Chroma(
        collection_name=cfg.chroma_collection,
        embedding_function=get_embeddings(cfg),
        persist_directory=str(cfg.chroma_persist_dir),
    )
    return _vectorstore


def add_documents(
    documents: list[Document],
    settings: Settings | None = None,
) -> int:
    """Embed and store documents. Returns number of chunks added."""
    if not documents:
        return 0
    store = get_vectorstore(settings)
    ids = store.add_documents(documents)
    return len(ids)


def retrieve(
    query: str,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> list[Document]:
    """Similarity search — only top-k relevant chunks (low token usage)."""
    cfg = settings or get_settings()
    k = top_k if top_k is not None else cfg.rag_top_k
    store = get_vectorstore(cfg)
    return store.similarity_search(query, k=k)


def reset_vectorstore(settings: Settings | None = None) -> None:
    """Delete the collection so the next ingest starts fresh."""
    global _vectorstore, _embeddings
    cfg = settings or get_settings()
    client = Chroma(
        collection_name=cfg.chroma_collection,
        embedding_function=get_embeddings(cfg),
        persist_directory=str(cfg.chroma_persist_dir),
    )
    client.delete_collection()
    _vectorstore = None
