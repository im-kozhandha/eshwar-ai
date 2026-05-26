# Eshwar AI

**AI Copilot for Water & Pump Intelligence**

Practical troubleshooting for Indian households, farmers, and small buildings — motors, tanks, borewells, pressure, electricity, and safe water basics. Built as a lean MVP to support customers today and Eshwar hardware + SaaS tomorrow.

---

> **GitHub repo description (copy-paste)**  
> `AI copilot for Indian water & pump troubleshooting — Streamlit, Gemini, and RAG over a practical knowledge base.`
>
> **Tagline**  
> *Pump and tank intelligence for every home, farm, and rooftop.*

---

## Problem

Millions of users face recurring issues — motor heat, tank overflow, weak pressure, tripping, muddy water, drying bores, and rising pump electricity bills. Answers are scattered across dealers, WhatsApp groups, and trial-and-error. **Eshwar AI** gives structured, safety-aware guidance in simple language and creates a natural path to Eshwar products and services.

## Features (MVP)

- Streamlit chat UI with session memory
- **Google Gemini** for concise, practical replies
- **RAG** over a curated markdown knowledge base
- **ChromaDB** + local **sentence-transformers** embeddings
- Source attribution and weak-retrieval warnings
- Sample questions sidebar — no login required

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User  →  Streamlit (app/app.py)                            │
│              │                                              │
│              ▼                                              │
│         rag_pipeline.ask()                                  │
│              │                                              │
│     ┌────────┴────────┐                                     │
│     ▼                 ▼                                     │
│  ChromaDB          Gemini API                               │
│  (top-k RAG)       (short prompt, capped tokens)            │
│     ▲                                                       │
│     │  ingest: markdown → chunks → embeddings               │
│  data/docs/*.md                                             │
└─────────────────────────────────────────────────────────────┘
```

## Tech stack

| Layer | Choice |
|--------|--------|
| UI | Streamlit |
| LLM | Google Gemini API |
| RAG | LangChain (minimal) |
| Vectors | ChromaDB |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Deploy | Streamlit Community Cloud |

## Project structure

```
eshwar_chatbot/
├── app/app.py              # Chat UI
├── backend/
│   ├── llm.py              # Gemini wrapper
│   ├── rag_pipeline.py     # Retrieve → prompt → answer
│   ├── vectorstore.py      # Chroma + embeddings
│   └── ingest.py           # Knowledge-base indexing
├── data/docs/              # Markdown knowledge base
├── data/chroma_db/         # Persisted vectors (local / rebuilt on deploy)
├── utils/                  # Config & paths
├── test_rag_local.py       # CLI smoke test
├── requirements.txt
└── .env.example
```

## Local setup

**Requirements:** Python **3.10–3.12** (3.14+ may fail on some ML wheels), Git, Gemini API key.

```powershell
# Clone
git clone https://github.com/YOUR_ORG/eshwar-chatbot.git
cd eshwar-chatbot

# Virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate         # Mac/Linux

pip install -r requirements.txt

# Environment
copy .env.example .env              # Windows
# cp .env.example .env              # Mac/Linux
# Edit .env → set GOOGLE_API_KEY
```

## Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GOOGLE_API_KEY` | Yes | — | Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Model name |
| `GEMINI_MAX_OUTPUT_TOKENS` | No | `512` | Reply length cap |
| `GEMINI_TEMPERATURE` | No | `0.4` | Creativity |
| `CHROMA_PERSIST_DIR` | No | `./data/chroma_db` | Vector store path |
| `CHROMA_COLLECTION` | No | `eshwar_knowledge` | Collection name |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Local embeddings |
| `RAG_TOP_K` | No | `3` | Chunks retrieved |
| `RAG_SCORE_THRESHOLD` | No | `1.15` | Weak-match cutoff |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | No | `500` / `50` | Ingestion chunks |

See [.env.example](.env.example) for the full list.

## Knowledge base ingestion

Markdown guides live in `data/docs/`. Index them into Chroma:

```powershell
python -m backend.ingest --reset
```

- **`--reset`** — clears the collection before re-indexing (use after doc updates).
- Without `--reset` — appends chunks (can duplicate; prefer reset when editing docs).

**Included topics:** motor overheating, tank overflow, low pressure, motor tripping, muddy water, borewell drying, electricity overuse, water contamination basics, Eshwar auto-cut timer.

### Quick RAG test (optional)

```powershell
python test_rag_local.py
python test_rag_local.py "Why does my tank overflow daily?"
```

## Running the app

```powershell
streamlit run app/app.py
```

Open `http://localhost:8501`.

---

## Deployment (Streamlit Cloud)

### 1. Push to GitHub

```powershell
git init
git add .
git commit -m "Eshwar AI MVP — Streamlit + Gemini + RAG"
git branch -M main
git remote add origin https://github.com/YOUR_ORG/eshwar-chatbot.git
git push -u origin main
```

Do **not** commit `.env` or secrets. `data/chroma_db/` is gitignored — vectors are rebuilt on the server (see below).

### 2. Create Streamlit Cloud app

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
2. Connect your GitHub repo.
3. **Main file path:** `app/app.py`
4. **Branch:** `main`

### 3. Secrets / environment variables

In the app → **Settings → Secrets**, paste TOML (map to the same names as `.env`):

```toml
GOOGLE_API_KEY = "your_key_here"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_MAX_OUTPUT_TOKENS = 512
GEMINI_TEMPERATURE = 0.4
RAG_TOP_K = 3
RAG_SCORE_THRESHOLD = 1.15
CHROMA_PERSIST_DIR = "./data/chroma_db"
```

Streamlit injects these as environment variables. `python-dotenv` in the app also loads `.env` locally only.

### 4. Chroma persistence on Cloud

| Topic | Guidance |
|--------|----------|
| **Not in Git** | `data/chroma_db/` is ignored — keeps the repo small. |
| **Ephemeral disk** | Cloud apps may lose local Chroma after cold starts or redeploys. |
| **Recommended** | Run ingestion when the vector store is empty (bootstrap on startup). |

Add this **once** near the top of `main()` in `app/app.py` (after `init_session()`):

```python
@st.cache_resource
def ensure_vector_index():
    from backend.ingest import ingest_knowledge_base
    from backend.vectorstore import get_vectorstore
    store = get_vectorstore()
    if store._collection.count() == 0:
        ingest_knowledge_base(reset=False)

# inside main():
ensure_vector_index()
```

First load builds the index (~1–3 min depending on CPU). Later loads reuse the cached resource until the app restarts.

**Alternative:** Run `python -m backend.ingest --reset` in CI and commit `data/chroma_db/` temporarily — not recommended for long-term (large binaries, stale embeddings).

### 5. Deploy

Click **Deploy**. Watch logs for:

- Successful `pip install -r requirements.txt`
- First-run embedding model download
- Ingest completion (if bootstrap is enabled)

### Common deployment issues

| Issue | Fix |
|--------|-----|
| `GOOGLE_API_KEY` missing | Add secret in Streamlit; redeploy. |
| `ModuleNotFoundError` | Confirm **Main file** is `app/app.py` and repo root has `backend/`, `utils/`. |
| App slow on first open | Normal — embeddings + ingest on cold start. Enable `@st.cache_resource` bootstrap. |
| Weak / generic answers | Chroma empty → run ingest or enable bootstrap; check logs. |
| `tokenizers` / build errors | Use Python 3.10–3.12 in Cloud runtime settings if available. |
| Out of memory | Reduce `RAG_TOP_K`, use smaller docs, or upgrade Cloud tier. |
| Secrets not picked up | Use Secrets TOML keys exactly as in `.env.example` (uppercase). |

---

## Troubleshooting (local)

| Symptom | What to try |
|---------|-------------|
| `No module named 'langchain_community'` | Activate venv; `pip install -r requirements.txt` |
| API key error | Set `GOOGLE_API_KEY` in `.env` |
| Empty or weak answers | `python -m backend.ingest --reset` |
| Import errors running UI | Run from repo root: `streamlit run app/app.py` |
| Pip fails on Python 3.14 | Install Python 3.11 or 3.12 |
| Duplicate/conflicting chunks | Re-ingest with `--reset` |

---

## Screenshots (placeholders)

Add to `docs/images/` when ready:

| File | Caption |
|------|---------|
| `docs/images/chat-home.png` | Home — title, sample questions, first reply |
| `docs/images/chat-sources.png` | Answer with knowledge-base sources |
| `docs/images/chat-weak-warning.png` | Weak retrieval warning state |
| `docs/images/sidebar.png` | Sidebar — samples + about |

```markdown
![Eshwar AI Chat](docs/images/chat-home.png)
```

---

## Future roadmap

Planned extensions (not in this MVP):

- Multilingual (Hindi, Tamil, Telugu, etc.)
- WhatsApp / SMS channel
- Voice input and photo upload (panel / tank / water colour)
- IoT telemetry from Eshwar hardware
- Predictive maintenance and usage analytics
- Subscriptions, dealer dashboards, CRM handoff

Architecture stays modular: swap channels, keep `rag_pipeline.ask()` as the core.

---

## Disclaimer

AI-generated guidance for education and triage only. **Consult a licensed technician** for electrical panels, rewiring, and drinking-water safety decisions.

---

## License

Proprietary — Eshwar. Update before open-sourcing.

---

**Built for Eshwar** — from rooftop tanks to farm borewells, one practical answer at a time.
