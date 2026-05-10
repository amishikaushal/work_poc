"""
scripts/audio/role_inference.py
────────────────────────────────
Infers Doctor / Patient roles from diarised, transcribed segments
using keyword scoring on the spoken content.
"""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Keywords that are statistically more likely to be spoken by a doctor
_DOCTOR_KEYWORDS = [
    "since when", "how long", "do you have", "any history",
    "diagnosis", "treatment", "prescribe", "recommend", "you should",
]


def infer_roles(segments: list[dict]) -> dict:
    """
    Map each speaker ID to either "Doctor" or "Patient".

    The speaker whose aggregated text contains the most doctor-like
    keywords is labelled "Doctor"; all others are "Patient".

    Args:
        segments: List of {start, end, speaker, text} dicts.

    Returns:
        Dict mapping speaker IDs to role strings, e.g.
        {"speaker_0": "Doctor", "speaker_1": "Patient"}.
    """
    # Aggregate all text per speaker
    speaker_text: dict[str, str] = defaultdict(str)
    for seg in segments:
        speaker_text[seg["speaker"]] += " " + seg["text"]

    def _doctor_score(text: str) -> int:
        text = text.lower()
        return sum(kw in text for kw in _DOCTOR_KEYWORDS)

    scores = {spk: _doctor_score(txt) for spk, txt in speaker_text.items()}
    doctor_speaker = max(scores, key=scores.get)

    role_map = {
        spk: "Doctor" if spk == doctor_speaker else "Patient"
        for spk in scores
    }

    logger.info(
        "Role inference complete — Doctor: %s | Speakers: %s",
        doctor_speaker, list(role_map.keys()),
    )
    return role_map
