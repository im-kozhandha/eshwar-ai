import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from utils.paths import CHROMA_DIR, ROOT

load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    google_api_key: str
    gemini_model: str
    gemini_max_tokens: int
    gemini_temperature: float
    chroma_persist_dir: Path
    chroma_collection: str
    embedding_model: str
    rag_top_k: int
    rag_score_threshold: float
    chunk_size: int
    chunk_overlap: int


def get_settings() -> Settings:
    persist = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    persist_path = Path(persist)
    if not persist_path.is_absolute():
        persist_path = ROOT / persist_path

    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        # 2.5-flash uses "thinking" tokens; 512 leaves almost no visible answer
        gemini_max_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "2048")),
        gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.4")),
        chroma_persist_dir=persist_path,
        chroma_collection=os.getenv("CHROMA_COLLECTION", "eshwar_knowledge"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        rag_top_k=int(os.getenv("RAG_TOP_K", "3")),
        rag_score_threshold=float(os.getenv("RAG_SCORE_THRESHOLD", "1.15")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
    )


def ensure_data_dirs() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
