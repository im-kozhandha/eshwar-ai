# Deploy Eshwar AI (GitHub + Streamlit Cloud)

## Before you push

- [ ] `.env` is **not** committed (already in `.gitignore`)
- [ ] You have a [Gemini API key](https://aistudio.google.com/apikey)
- [ ] Local app works: `streamlit run app/app.py`

---

## Step 1 — Push to GitHub

### A. Create an empty repo on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Name: `eshwar-ai` (or any name)
3. **Do not** add README / .gitignore (you already have them)
4. Click **Create repository**

### B. Push from your PC

```powershell
cd c:\eshwar_chatbot

git init
git add .
git status
# Confirm .env is NOT listed

git commit -m "Eshwar AI MVP — Streamlit + Gemini + RAG"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/eshwar-ai.git
git push -u origin main
```

Replace `YOUR_USERNAME` and repo name with yours.

---

## Step 2 — Deploy on Streamlit Cloud

1. Open [share.streamlit.io](https://share.streamlit.io) and sign in with **GitHub**
2. **New app**
3. **Repository:** your `eshwar-ai` repo  
4. **Branch:** `main`  
5. **Main file path:** `app/app.py`
6. **App URL:** pick something like `eshwar-ai`

Click **Deploy** (first deploy may fail until secrets are set — that’s normal).

### Important: Python version

This project requires **Python 3.10–3.12**. If Streamlit Cloud uses **Python 3.14**, `tokenizers` will fail to build.

- This repo includes `runtime.txt` with `python-3.11.9`
- In Streamlit Cloud, also check **App settings → Python version** (if shown) and set it to **3.11**

---

## Step 3 — Add secrets (required)

In the app → **Settings** → **Secrets**, paste:

```toml
GOOGLE_API_KEY = "paste_your_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_MAX_OUTPUT_TOKENS = 2048
GEMINI_TEMPERATURE = 0.4
RAG_TOP_K = 3
CHROMA_PERSIST_DIR = "./data/chroma_db"
```

Save → **Reboot app** (menu or Settings).

---

## Step 4 — First load on Cloud

- First visitor triggers **embedding download + Chroma ingest** (~2–5 minutes).
- Show a “loading” message to demo users on first open.
- Later visits are faster until the app cold-starts again.

---

## Troubleshooting

| Issue | Fix |
|--------|-----|
| `ModuleNotFoundError` | Main file must be `app/app.py`; `requirements.txt` at repo root |
| Build fails on Python 3.14 | `runtime.txt` pins `python-3.11` |
| Quota / 429 errors | Use `gemini-2.5-flash`, wait 1 min, retry |
| Empty / weak answers | Reboot app after secrets; wait for ingest to finish |
| App sleeps on free tier | Normal — first click may wake it (30s) |

---

## Optional — custom domain

Streamlit Cloud → app **Settings** → **General** → connect domain (paid plans / team features vary).

---

## Security

- Never commit `.env` or API keys
- Rotate key if it was ever exposed in chat or screenshots
