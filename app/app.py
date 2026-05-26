"""
Eshwar AI — Streamlit chat UI (premium SaaS layout).

Run from project root:
    streamlit run app/app.py
"""

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")

import streamlit as st

from backend.rag_pipeline import ask

# --- Branding ---

APP_TITLE = "Eshwar AI"
SUBTITLE = "AI Copilot for Water & Pump Intelligence"
TAGLINE = "Motors · Tanks · Borewells · Pressure · Power"
DISCLAIMER = (
    "AI-generated guidance — consult a licensed technician for critical electrical work."
)

SAMPLE_QUESTIONS: list[tuple[str, str]] = [
    ("🌡️", "Why is my motor overheating?"),
    ("💧", "Why does my tank overflow daily?"),
    ("📉", "Why is water pressure low?"),
    ("⚡", "Why does my motor trip repeatedly?"),
    ("🏜️", "Is my borewell drying?"),
    ("🟤", "Why is muddy water coming?"),
    ("🔌", "Why is electricity usage high?"),
    ("⏱️", "Which auto-cut timer setup is suitable?"),
]

LOADING_HTML = """
<div class="eshwar-loader">
  <div class="eshwar-loader-glow"></div>
  <div class="eshwar-loader-row">
    <span class="eshwar-shimmer"></span>
    <span class="eshwar-loader-text">Searching knowledge base · reasoning</span>
  </div>
</div>
"""

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-deep: #040b14;
  --bg-mid: #071525;
  --bg-card: rgba(12, 28, 48, 0.72);
  --border: rgba(56, 189, 248, 0.14);
  --border-strong: rgba(56, 189, 248, 0.28);
  --text: #e8f4fc;
  --text-muted: #8fb4cc;
  --text-dim: #5a7f96;
  --cyan: #22d3ee;
  --cyan-soft: #38bdf8;
  --glow: rgba(34, 211, 238, 0.35);
  --radius: 14px;
  --radius-lg: 20px;
  --shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
  --font: 'Inter', system-ui, -apple-system, sans-serif;
  --chat-max: 720px;
}

/* App shell */
.stApp {
  background: var(--bg-deep);
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34, 211, 238, 0.12), transparent),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(30, 136, 229, 0.08), transparent),
    linear-gradient(180deg, #040b14 0%, #071525 50%, #061018 100%);
  font-family: var(--font);
  color: var(--text);
}

#MainMenu, footer, header[data-testid="stHeader"] {
  visibility: hidden;
  height: 0;
  pointer-events: none;
}

.block-container {
  padding-top: 1.25rem !important;
  padding-bottom: 7rem !important;
  max-width: var(--chat-max) !important;
  margin: 0 auto !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #050f1a 0%, #071a2e 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25);
}

[data-testid="stSidebar"] > div:first-child {
  padding-top: 1.25rem;
}

[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] h3 {
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--text-dim) !important;
  margin-bottom: 0.75rem !important;
}

[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  text-align: left;
  justify-content: flex-start;
  background: var(--bg-card) !important;
  backdrop-filter: blur(12px);
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.65rem 0.85rem !important;
  min-height: 2.6rem !important;
  box-shadow: none !important;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}

[data-testid="stSidebar"] .stButton > button:hover {
  border-color: var(--border-strong) !important;
  box-shadow: 0 0 20px var(--glow) !important;
  transform: translateY(-1px);
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.2), rgba(30, 136, 229, 0.25)) !important;
  border-color: var(--border-strong) !important;
  color: var(--cyan) !important;
  font-weight: 600 !important;
}

[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
  margin: 1.25rem 0 !important;
}

/* Logo & brand blocks */
.eshwar-logo-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.5rem;
  padding: 0.85rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow);
}

.eshwar-logo {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #0ea5e9 0%, #22d3ee 50%, #0369a1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  box-shadow: 0 0 24px var(--glow);
  flex-shrink: 0;
}

.eshwar-logo-text .brand {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--text);
  line-height: 1.2;
}

.eshwar-logo-text .tag {
  font-size: 0.68rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.eshwar-side-about {
  font-size: 0.8rem;
  line-height: 1.55;
  color: var(--text-muted);
  padding: 0.9rem 1rem;
  background: rgba(8, 20, 36, 0.6);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.eshwar-side-about strong { color: var(--cyan-soft); }

.eshwar-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 0.75rem;
}

.eshwar-pill {
  font-size: 0.65rem;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(34, 211, 238, 0.08);
  border: 1px solid var(--border);
  color: var(--text-dim);
}

/* Main header */
.eshwar-hero {
  text-align: center;
  padding: 0.5rem 0 1.75rem;
  margin-bottom: 0.5rem;
}

.eshwar-hero-glow {
  width: 120px;
  height: 4px;
  margin: 0.75rem auto 0;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
  border-radius: 2px;
  animation: pulse-glow 2.5s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.4; transform: scaleX(0.85); }
  50% { opacity: 1; transform: scaleX(1); }
}

.eshwar-hero h1 {
  font-size: clamp(1.5rem, 4vw, 1.85rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  margin: 0;
  background: linear-gradient(135deg, #f0f9ff 0%, #7dd3fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.eshwar-hero .sub {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0.4rem 0 0;
  font-weight: 500;
}

.eshwar-hero .meta {
  font-size: 0.72rem;
  color: var(--text-dim);
  margin-top: 0.35rem;
  letter-spacing: 0.04em;
}

/* Empty state */
.eshwar-empty {
  text-align: center;
  padding: 2.5rem 1.5rem;
  margin: 1rem 0 2rem;
  background: var(--bg-card);
  border: 1px dashed var(--border);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(12px);
}

.eshwar-empty .icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  filter: drop-shadow(0 0 12px var(--glow));
}

.eshwar-empty h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 0.5rem;
}

.eshwar-empty p {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0.35rem 0 !important;
}

div[data-testid="stChatMessage"] > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow);
  padding: 0.85rem 1.1rem !important;
}

/* User bubble accent */
div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(8, 20, 36, 0.9)) !important;
  border-color: rgba(56, 189, 248, 0.22) !important;
}

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li {
  font-size: 0.9rem !important;
  line-height: 1.65 !important;
  color: var(--text) !important;
}

div[data-testid="stChatMessage"] strong {
  color: var(--cyan-soft) !important;
}

/* Source chips & alerts */
.eshwar-sources-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 0.65rem;
  padding-top: 0.55rem;
  border-top: 1px solid var(--border);
}

.eshwar-sources-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-dim);
}

.eshwar-chip {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid var(--border);
  color: var(--cyan-soft);
}

.eshwar-alert {
  margin-top: 0.6rem;
  padding: 0.55rem 0.75rem;
  font-size: 0.78rem;
  line-height: 1.45;
  color: #fcd34d;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.25);
  border-radius: 10px;
}

/* Loader */
.eshwar-loader {
  position: relative;
  padding: 1rem 1.1rem;
  margin: 0.5rem 0 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.eshwar-loader-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(34, 211, 238, 0.08) 50%, transparent 60%);
  animation: shimmer-slide 1.8s infinite;
}

@keyframes shimmer-slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.eshwar-loader-row {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.eshwar-shimmer {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cyan);
  box-shadow: 0 0 12px var(--glow);
  animation: pulse-dot 1s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 0.5; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

.eshwar-loader-text {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}

/* Sticky input area */
[data-testid="stBottomBlockContainer"] {
  position: sticky !important;
  bottom: 0 !important;
  z-index: 999 !important;
  background: linear-gradient(180deg, transparent 0%, rgba(4, 11, 20, 0.92) 24%, #040b14 100%) !important;
  border-top: 1px solid var(--border) !important;
  padding: 0.75rem 0 1rem !important;
  margin-top: 1rem !important;
}

[data-testid="stChatInput"] {
  max-width: var(--chat-max);
  margin: 0 auto;
}

[data-testid="stChatInput"] > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-lg) !important;
  backdrop-filter: blur(16px);
  box-shadow: 0 0 28px rgba(34, 211, 238, 0.08);
}

[data-testid="stChatInput"] textarea {
  font-family: var(--font) !important;
  font-size: 0.9rem !important;
  color: var(--text) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: var(--text-dim) !important;
}

.eshwar-disclaimer {
  text-align: center;
  font-size: 0.68rem;
  color: var(--text-dim);
  padding: 0.5rem 0 0;
  max-width: var(--chat-max);
  margin: 0 auto;
}

/* Hide default spinner text styling */
.stSpinner > div {
  border-top-color: var(--cyan) !important;
}

/* Mobile */
@media (max-width: 768px) {
  .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
  .eshwar-hero { padding-bottom: 1rem; }
  [data-testid="stSidebar"] { min-width: 280px !important; }
}
</style>
"""


# --- Session & backend (unchanged logic) ---


def init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


@st.cache_resource
def ensure_vector_index() -> None:
    """Build Chroma index on first run (needed on Streamlit Cloud — DB is not in Git)."""
    from backend.ingest import ingest_knowledge_base
    from backend.vectorstore import get_vectorstore

    store = get_vectorstore()
    try:
        count = store._collection.count()
    except Exception:
        count = 0
    if count == 0:
        ingest_knowledge_base(reset=False)


def get_chat_history() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    pending_user: str | None = None
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            pending_user = msg["content"]
        elif msg["role"] == "assistant" and pending_user:
            pairs.append((pending_user, msg["content"]))
            pending_user = None
    return pairs


def clear_chat() -> None:
    st.session_state.messages = []
    st.session_state.pending_question = None


def inject_css() -> None:
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class="eshwar-logo-wrap">
          <div class="eshwar-logo">💧</div>
          <div class="eshwar-logo-text">
            <div class="brand">Eshwar AI</div>
            <div class="tag">Water & Pump Intelligence</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        render_sidebar_brand()
        st.markdown("#### Quick prompts")
        st.caption("One tap — investor-demo ready")

        for i, (icon, question) in enumerate(SAMPLE_QUESTIONS):
            label = f"{icon}  {question}"
            if st.button(label, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()

        st.divider()
        st.markdown("#### About")
        st.markdown(
            f"""
            <div class="eshwar-side-about">
              <strong>Eshwar AI</strong> guides Indian households, farmers, and small buildings
              on motors, tanks, borewells, pressure, and pump electricity.
              <div class="eshwar-pill-row">
                <span class="eshwar-pill">Gemini</span>
                <span class="eshwar-pill">RAG</span>
                <span class="eshwar-pill">ChromaDB</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        if st.button("↻  New conversation", use_container_width=True, type="primary"):
            clear_chat()
            st.rerun()


def render_header() -> None:
    st.markdown(
        f"""
        <div class="eshwar-hero">
          <h1>{APP_TITLE}</h1>
          <p class="sub">{SUBTITLE}</p>
          <p class="meta">{TAGLINE}</p>
          <div class="eshwar-hero-glow"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="eshwar-empty">
          <div class="icon">🛠️</div>
          <h2>Ask anything about your water system</h2>
          <p>Pick a prompt from the sidebar or type below — answers use your
          knowledge base with source citations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources_html(sources: list[str]) -> str:
    if not sources:
        return ""
    chips = "".join(f'<span class="eshwar-chip">{s}</span>' for s in sources)
    return f"""
    <div class="eshwar-sources-row">
      <span class="eshwar-sources-label">Sources</span>
      {chips}
    </div>
    """


def render_assistant_extras(msg: dict) -> None:
    html_parts: list[str] = []
    if msg.get("retrieval_weak"):
        html_parts.append(
            '<div class="eshwar-alert">⚠ Limited KB match — answer may be general. '
            "Add detail or consult a local technician.</div>"
        )
    html_parts.append(render_sources_html(msg.get("sources") or []))
    if html_parts:
        st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_chat_history() -> None:
    for msg in st.session_state.messages:
        # Streamlit avatars: single emoji or None (✦ / ZWJ emojis crash)
        avatar = "💧" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                render_assistant_extras(msg)


def process_question(question: str) -> None:
    question = question.strip()
    if not question:
        return

    history = get_chat_history()
    st.session_state.messages.append({"role": "user", "content": question})

    loader = st.empty()
    loader.markdown(LOADING_HTML, unsafe_allow_html=True)

    try:
        result = ask(question, chat_history=history)
        answer = result["answer"]
    except ValueError as e:
        answer = f"**Setup issue:** {e}"
        result = {"sources": [], "retrieval_weak": True}
    except RuntimeError as e:
        answer = f"**Could not reach Gemini:** {e}"
        result = {"sources": [], "retrieval_weak": True}
    except Exception as e:
        answer = f"**Unexpected error:** {e}"
        result = {"sources": [], "retrieval_weak": True}
    finally:
        loader.empty()

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": result.get("sources", []),
            "retrieval_weak": result.get("retrieval_weak", False),
        }
    )


def main() -> None:
    st.set_page_config(
        page_title="Eshwar AI",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    init_session()
    ensure_vector_index()
    render_sidebar()

    # Centered chat column via CSS max-width on block-container
    render_header()

    if not st.session_state.messages:
        render_empty_state()

    render_chat_history()

    pending = st.session_state.pending_question
    if pending:
        st.session_state.pending_question = None
        process_question(pending)
        st.rerun()

    st.markdown(f'<p class="eshwar-disclaimer">{DISCLAIMER}</p>', unsafe_allow_html=True)

    if user_input := st.chat_input("Ask about motors, tanks, borewells, pressure…"):
        process_question(user_input)
        st.rerun()


if __name__ == "__main__":
    main()
