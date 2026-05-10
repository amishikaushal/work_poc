"""
scripts/audio/audio_preprocess.py
──────────────────────────────────
Converts input audio/video files to 16 kHz mono WAV format
required by speaker diarisation and transcription models.
"""
import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def convert_to_wav(input_file: str) -> str:
    """
    Convert any audio/video file to a 16 kHz mono WAV.

    If the input is already a WAV file it is returned as-is.

    Args:
        input_file: Path to the source audio/video file.

    Returns:
        Path to the resulting WAV file.

    Raises:
        subprocess.CalledProcessError: If FFmpeg conversion fails.
    """
    if input_file.lower().endswith(".wav"):
        logger.info("Input is already WAV; skipping conversion: %s", input_file)
        return input_file

    wav_file = os.path.splitext(input_file)[0] + ".wav"
    logger.info("Converting %s → %s", input_file, wav_file)

    subprocess.run(
        ["ffmpeg", "-y", "-i", input_file, "-ac", "1", "-ar", "16000", wav_file],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    logger.info("Conversion complete: %s", wav_file)
    return wav_file
