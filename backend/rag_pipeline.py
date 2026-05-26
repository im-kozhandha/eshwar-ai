"""
RAG pipeline: retrieve → build prompt → Gemini answer.

Example query flow
------------------
1. User asks: "Why is my motor overheating?"
2. retrieve_scored() pulls top-k chunks from Chroma (motor-overheating.md).
3. If best match score is good → inject context into a short prompt.
4. If retrieval is weak → fallback prompt (general safe guidance, no fake facts).
5. generate_response() returns a concise, structured reply.

Usage:
    from backend.rag_pipeline import ask
    result = ask("Why is my motor overheating?")
    print(result["answer"])
"""

from langchain_core.documents import Document

from backend.llm import generate_response
from backend.vectorstore import get_vectorstore
from utils.config import Settings, get_settings

# Keep instructions compact to save tokens on every request.
_SYSTEM_RULES = """You are Eshwar AI — a practical water, pump & motor assistant for Indian homes, farms and small buildings.

Rules:
- Use ONLY the provided context for specific facts. Do not invent product specs or wiring steps.
- If context is marked WEAK, say you're not fully sure, give cautious general guidance, and suggest a local technician for electrical work.
- Give a complete answer (~120–180 words). Do not stop mid-sentence. Friendly, clear.
- Prefer this structure when relevant (short bullets):
  Likely causes → Quick checks → Suggested fixes → Prevention
- Never tell users to open panels, bypass safety devices, or work on live wiring.
- Mention Eshwar auto-cut/timer only when it naturally fits (one line, not salesy)."""

_FALLBACK_CONTEXT = (
    "[WEAK — no reliable knowledge-base match]\n"
    "Give cautious general water/pump safety guidance only. "
    "Encourage describing symptoms (noise, heat, flow, trips) and calling a licensed electrician for panel work."
)


def retrieve_scored(
    query: str,
    top_k: int | None = None,
    settings: Settings | None = None,
) -> list[tuple[Document, float]]:
    cfg = settings or get_settings()
    k = top_k if top_k is not None else cfg.rag_top_k
    store = get_vectorstore(cfg)
    return store.similarity_search_with_score(query, k=k)


def _is_weak_retrieval(
    scored: list[tuple[Document, float]],
    settings: Settings,
) -> bool:
    if not scored:
        return True
    best_score = min(score for _, score in scored)
    return best_score > settings.rag_score_threshold


def format_context(scored: list[tuple[Document, float]]) -> str:
    blocks: list[str] = []
    for doc, score in scored:
        source = doc.metadata.get("source", "knowledge-base")
        text = doc.page_content.strip().replace("\n", " ")
        if len(text) > 700:
            text = text[:700] + "..."
        blocks.append(f"[{source} | score={score:.3f}]\n{text}")
    return "\n\n".join(blocks)


def _format_history(
    chat_history: list[tuple[str, str]] | None,
    max_turns: int = 2,
) -> str:
    if not chat_history:
        return ""
    recent = chat_history[-max_turns:]
    lines = [f"User: {u}\nAssistant: {a}" for u, a in recent]
    return "Recent chat:\n" + "\n".join(lines) + "\n\n"


def build_prompt(
    question: str,
    context: str,
    *,
    weak: bool,
    chat_history: list[tuple[str, str]] | None = None,
) -> str:
    ctx_block = _FALLBACK_CONTEXT if weak else f"Context:\n{context}"
    history = _format_history(chat_history)
    return (
        f"{_SYSTEM_RULES}\n\n"
        f"{history}"
        f"{ctx_block}\n\n"
        f"User question: {question}\n\n"
        f"Answer:"
    )


def ask(
    question: str,
    chat_history: list[tuple[str, str]] | None = None,
    settings: Settings | None = None,
) -> dict:
    """
    Run full RAG query.

    Returns:
        answer (str), sources (list[str]), retrieval_weak (bool), chunks_used (int)
    """
    cfg = settings or get_settings()
    scored = retrieve_scored(question, settings=cfg)
    weak = _is_weak_retrieval(scored, cfg)
    context = format_context(scored) if scored and not weak else ""
    prompt = build_prompt(question, context, weak=weak, chat_history=chat_history)
    answer = generate_response(prompt, cfg)

    sources = list(
        dict.fromkeys(
            doc.metadata.get("source", "unknown") for doc, _ in scored
        )
    )

    return {
        "answer": answer,
        "sources": sources,
        "retrieval_weak": weak,
        "chunks_used": len(scored),
    }
