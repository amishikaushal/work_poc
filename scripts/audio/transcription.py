"""
scripts/audio/transcription.py
──────────────────────────────
Transcribes diarised speaker segments or a whole WAV file to English text.
Prefers faster-whisper when installed; falls back to openai-whisper.
"""
import logging
import time
import numpy as np
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# ── Backend selection (done once at import time) ───────────────────────────────
try:
    from faster_whisper import WhisperModel as _FasterWhisperModel
    _USE_FASTER = True
    logger.info("Transcription backend: faster-whisper")
except ImportError:
    import whisper as _openai_whisper
    _USE_FASTER = False
    logger.info("Transcription backend: openai-whisper (faster-whisper not installed)")

# ── Model cache ────────────────────────────────────────────────────────────────
# If Streamlit is available the model is cached at the app level via
# @st.cache_resource in app.py; here we keep a simple module-level cache
# for non-Streamlit usage (e.g. CLI / tests).
_cached_model = None


def _load_model():
    """Load and return the appropriate Whisper model (cached after first call)."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    t0 = time.time()
    if _USE_FASTER:
        logger.info("Loading faster-whisper 'medium' (cpu / int8)…")
        _cached_model = _FasterWhisperModel("medium", device="cpu", compute_type="int8")
    else:
        logger.info("Loading openai-whisper 'medium'…")
        _cached_model = _openai_whisper.load_model("medium")

    logger.info("Model loaded in %.2fs", time.time() - t0)
    return _cached_model


# ── Public API ─────────────────────────────────────────────────────────────────

def transcribe_segments(wav_file: str, diarized_segments: list[dict]) -> list[dict]:
    """
    Transcribe each diarised speaker segment into English.

    Args:
        wav_file:          Path to the source WAV file.
        diarized_segments: List of {start, end, speaker} dicts from diarize_audio().

    Returns:
        List of {start, end, speaker, text} dicts sorted by start time.
    """
    t0 = time.time()
    logger.info("Transcribing %d segments from %s", len(diarized_segments), wav_file)

    audio = AudioSegment.from_wav(wav_file).set_channels(1).set_frame_rate(16_000)
    model = _load_model()
    results = []

    for i, seg in enumerate(diarized_segments):
        chunk    = audio[int(seg["start"] * 1000) : int(seg["end"] * 1000)]
        samples  = np.array(chunk.get_array_of_samples())
        audio_np = samples.astype(np.float32) / float(2 ** (8 * chunk.sample_width - 1))

        if _USE_FASTER:
            segs_iter, _ = model.transcribe(audio_np, beam_size=5, language="en", task="translate")
            text = "".join(s.text for s in segs_iter).strip()
        else:
            text = model.transcribe(audio_np, language="en", task="translate")["text"].strip()

        results.append({
            "start":   seg["start"],
            "end":     seg["end"],
            "speaker": seg["speaker"],
            "text":    text,
        })
        logger.debug("Segment %d/%d done", i + 1, len(diarized_segments))

    results.sort(key=lambda x: x["start"])
    logger.info("Transcription completed in %.2fs (%d segments)", time.time() - t0, len(results))
    return results


def transcribe_file(wav_file: str) -> str:
    """
    Transcribe an entire WAV file and return plain English text.

    Args:
        wav_file: Path to the WAV file.

    Returns:
        Transcribed text string.
    """
    logger.info("Transcribing full file: %s", wav_file)
    model = _load_model()

    if _USE_FASTER:
        segs, _ = model.transcribe(wav_file, beam_size=5, language="en", task="translate")
        return "".join(s.text for s in segs).strip()
    else:
        return model.transcribe(wav_file, language="en", task="translate").get("text", "").strip()
