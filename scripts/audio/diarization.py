"""
scripts/audio/diarization.py
─────────────────────────────
Speaker diarisation using NVIDIA's Sortformer model.
The model is loaded once and cached at module level.
"""
import logging
from nemo.collections.asr.models import SortformerEncLabelModel

logger = logging.getLogger(__name__)

# ── Model cache ────────────────────────────────────────────────────────────────
_diar_model = None


def _get_model() -> SortformerEncLabelModel:
    """Return the diarisation model, loading it on first call."""
    global _diar_model
    if _diar_model is None:
        logger.info("Loading diarisation model: nvidia/diar_streaming_sortformer_4spk-v2.1")
        _diar_model = SortformerEncLabelModel.from_pretrained(
            "nvidia/diar_streaming_sortformer_4spk-v2.1"
        )
        _diar_model.eval()
        logger.info("Diarisation model loaded.")
    return _diar_model


# ── Public API ─────────────────────────────────────────────────────────────────

def diarize_audio(wav_file: str) -> list[dict]:
    """
    Run speaker diarisation on a 16 kHz mono WAV file.

    Args:
        wav_file: Path to the WAV file.

    Returns:
        List of {start: float, end: float, speaker: str} dicts.
    """
    logger.info("Diarising: %s", wav_file)
    model = _get_model()

    # Streaming parameters (tuned for accuracy vs. latency)
    model.sortformer_modules.chunk_len             = 340
    model.sortformer_modules.chunk_right_context   = 40
    model.sortformer_modules.fifo_len              = 40
    model.sortformer_modules.spkcache_update_period = 300

    predicted = model.diarize(audio=[wav_file], batch_size=1)

    segments = []
    for line in predicted[0]:
        start, end, speaker = line.split()
        segments.append({"start": float(start), "end": float(end), "speaker": speaker})

    logger.info("Diarisation complete: %d segments found.", len(segments))
    return segments
