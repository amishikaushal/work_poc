"""
scripts/translate_utils.py
───────────────────────────
Language detection and text translation utilities used by the processing
pipelines, plus a helper for persisting diarised audio transcripts to disk.
"""
import os
import logging
import requests
from langdetect import detect

logger = logging.getLogger(__name__)

# Google Translate unofficial endpoint — no API key required, handles chunking
_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
_MAX_CHUNK_CHARS = 4_500


# ── Language detection ─────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """
    Detect the language of *text* using langdetect.

    Returns an ISO 639-1 language code (e.g. "en", "fr").
    Falls back to "en" on any error.
    """
    try:
        return detect(text[:500])
    except Exception:
        logger.warning("Language detection failed; defaulting to 'en'.")
        return "en"


# ── Text translation ───────────────────────────────────────────────────────────

def translate_text(
    text: str,
    source_lang: str = "auto",
    target_lang: str = "en",
) -> str:
    """
    Translate *text* from *source_lang* to *target_lang*.

    Long texts are split into chunks of up to 4 500 characters so they
    fit within the unofficial Google Translate endpoint's limits.

    Returns the original text unchanged if source == target, or on error.
    """
    if source_lang == target_lang:
        return text

    chunks = [text[i : i + _MAX_CHUNK_CHARS] for i in range(0, len(text), _MAX_CHUNK_CHARS)]
    translated_parts: list[str] = []

    try:
        for chunk in chunks:
            params = {"client": "gtx", "sl": source_lang, "tl": target_lang, "dt": "t", "q": chunk}
            resp   = requests.get(_TRANSLATE_URL, params=params, timeout=15)
            result = resp.json()
            translated_parts.append("".join(part[0] for part in result[0] if part[0]))

        return " ".join(translated_parts)

    except Exception as exc:
        logger.error("Translation error: %s — returning original text.", exc)
        return text


# ── Audio transcript persistence ───────────────────────────────────────────────

def save_audio_output(segments: list[dict], role_map: dict, input_file: str) -> None:
    """
    Write the diarised, role-labelled transcript to output/transcript.txt.

    Args:
        segments:   List of {speaker, text, …} dicts from transcription.
        role_map:   Speaker-ID → role mapping from role_inference.
        input_file: Original source audio path (used only for logging).
    """
    output_dir  = "output"
    output_path = os.path.join(output_dir, "transcript.txt")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            role = role_map.get(seg["speaker"], seg["speaker"])
            f.write(f"{role}: {seg['text']}\n")

    logger.info("Audio transcript saved: %s (source: %s)", os.path.abspath(output_path), input_file)