"""
scripts/final_summarize.py
──────────────────────────
Calls Sarvam AI to generate a medical summary from a given perspective.
Uses a persistent HTTP session for connection reuse across calls.
"""
import os
import re
import logging
import requests

logger = logging.getLogger(__name__)

# ── API configuration ──────────────────────────────────────────────────────────
_API_URL = "https://api.sarvam.ai/v1/chat/completions"
_API_KEY = os.getenv("SARVAM_API_KEY", "sk_lj92wr1i_R7P7HB77NAGA9T3O6yJRL96k")

# Persistent session — reuses the TCP connection across multiple calls
# (avoids the overhead of a full TLS handshake on every summarisation request)
_session = requests.Session()
_session.headers.update({
    "Authorization": f"Bearer {_API_KEY}",
    "Content-Type": "application/json",
})


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean_response(text: str) -> str:
    """Strip <think>…</think> reasoning blocks and stray XML tags from output."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<.*?>", "", text)
    return text.strip()


# ── Public API ─────────────────────────────────────────────────────────────────

def run_summarization(text: str, perspective: str) -> str:
    """
    Summarise a medical consultation transcript from the given perspective.

    Args:
        text:        Raw or cleaned transcript text.
        perspective: "Patient" or "Doctor".

    Returns:
        A clean summary string, or an error message on failure.
    """
    if not text.strip():
        return "Error: No input text provided for summarization."

    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a professional medical scribe. "
                    f"Provide ONLY a clean, concise {perspective} perspective summary. "
                    f"Do NOT include reasoning steps or tags like <think>."
                ),
            },
            {
                "role": "user",
                "content": f"Summarize the following medical consultation for a {perspective}:\n{text}",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }

    try:
        logger.info("Requesting %s summary from Sarvam AI…", perspective)
        response = _session.post(_API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            raw = response.json()["choices"][0]["message"]["content"]
            return _clean_response(raw)
        logger.error("Sarvam API error %s: %s", response.status_code, response.text)
        return f"API Error {response.status_code}: {response.text}"
    except Exception as exc:
        logger.error("Sarvam API request failed: %s", exc)
        return f"Request failed: {exc}"