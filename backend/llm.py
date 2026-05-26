"""Gemini API wrapper — single entry point for text generation."""

import re
import time

import google.generativeai as genai

from utils.config import Settings, get_settings

_configured = False

# Visible answers shorter than this are usually truncated (2.5-flash thinking tokens)
_MIN_ANSWER_CHARS = 200


def _ensure_client(settings: Settings) -> genai.GenerativeModel:
    global _configured
    if not settings.google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    if settings.google_api_key.startswith("your_"):
        raise ValueError(
            "GOOGLE_API_KEY still looks like a placeholder. Paste a real key from Google AI Studio."
        )
    if not _configured:
        genai.configure(api_key=settings.google_api_key)
        _configured = True

    return genai.GenerativeModel(
        model_name=settings.gemini_model,
        generation_config=genai.GenerationConfig(
            max_output_tokens=settings.gemini_max_tokens,
            temperature=settings.gemini_temperature,
        ),
    )


def _extract_text(response) -> str:
    """Collect all text parts from the Gemini response."""
    if getattr(response, "text", None):
        return response.text.strip()
    parts: list[str] = []
    for candidate in response.candidates or []:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in content.parts or []:
            if getattr(part, "text", None):
                parts.append(part.text)
    return "\n".join(parts).strip()


def _retry_seconds(exc: Exception) -> int:
    match = re.search(r"retry in (\d+)", str(exc).lower())
    if match:
        return min(int(match.group(1)) + 2, 90)
    return 30


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "resourceexhausted" in msg or "quota" in msg


def _friendly_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if _is_rate_limit(exc):
        return (
            "Gemini rate limit hit (too many requests). Wait about 1 minute, "
            "click **New conversation**, and try again. "
            "Use `GEMINI_MODEL=gemini-2.5-flash` in `.env` — avoid `gemini-2.0-flash` on free tier."
        )
    if "api key" in msg or "invalid" in msg or "401" in msg or "403" in msg:
        return (
            "Invalid Gemini API key. Check `GOOGLE_API_KEY` in `.env` "
            "(from https://aistudio.google.com/apikey)."
        )
    if "not found" in msg and "model" in msg:
        return (
            "Model not available: check `GEMINI_MODEL` in `.env` "
            "(try gemini-2.5-flash)."
        )
    return f"Gemini error: {exc}"


def generate_response(
    prompt: str,
    settings: Settings | None = None,
) -> str:
    """
    Send a complete prompt to Gemini and return plain-text reply.

    Prompt should already include instructions + context (built by rag_pipeline).
    """
    cfg = settings or get_settings()
    model = _ensure_client(cfg)
    last_error: Exception | None = None

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            last_error = None
            break
        except Exception as e:
            last_error = e
            if _is_rate_limit(e) and attempt < 2:
                time.sleep(_retry_seconds(e))
                continue
            raise RuntimeError(_friendly_error(e)) from e

    if last_error is not None:
        raise RuntimeError(_friendly_error(last_error))

    text = _extract_text(response)
    if len(text) < _MIN_ANSWER_CHARS:
        raise RuntimeError(
            "Reply was cut off (token limit too low). "
            "Set GEMINI_MAX_OUTPUT_TOKENS=2048 in .env and restart the app."
        )
    return text
