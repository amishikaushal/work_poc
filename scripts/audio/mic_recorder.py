"""
scripts/audio/mic_recorder.py
─────────────────────────────
Provides two recording APIs:
  - record_audio()   : blocking fixed-duration recording
  - start/stop_recording(): non-blocking toggle-style recording
"""
import os
import logging
import sounddevice as sd
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)


def record_audio(
    output_file: str = "recorded_audio.wav",
    duration: int = 30,
    sample_rate: int = 16_000,
) -> str | None:
    """
    Record audio from the default microphone for a fixed duration.

    Returns:
        Absolute path to the saved WAV file, or None on error.
    """
    output_dir = os.path.dirname(os.path.abspath(output_file))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    logger.info("Recording %ds → %s", duration, output_file)
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()
        sf.write(output_file, audio, sample_rate)
        return os.path.abspath(output_file)
    except Exception as exc:
        logger.error("Recording failed: %s", exc)
        return None


# ── Non-blocking start / stop API ──────────────────────────────────────────────
_stream = None
_frames: list = []
_output_file: str | None = None


def start_recording(
    output_file: str = "recorded_audio.wav",
    sample_rate: int = 16_000,
) -> str | None:
    """
    Start a background (non-blocking) recording stream.
    Call stop_recording() to finish and save.

    Returns:
        Absolute path of the intended output file, or None if already recording.
    """
    global _stream, _frames, _output_file
    if _stream is not None:
        logger.warning("Recording already in progress; ignoring start request.")
        return None

    _frames = []
    _output_file = output_file

    def _callback(indata, frames, time_info, status):
        if status:
            logger.warning("Stream status: %s", status)
        _frames.append(indata.copy())

    try:
        _stream = sd.InputStream(samplerate=sample_rate, channels=1, callback=_callback)
        _stream.start()
        logger.info("Started background recording → %s", _output_file)
        return os.path.abspath(_output_file)
    except Exception as exc:
        logger.error("Failed to start recording: %s", exc)
        _stream = None
        return None


def stop_recording() -> str | None:
    """
    Stop the active background recording and write audio to disk.

    Returns:
        Absolute path to the saved WAV file, or None on error.
    """
    global _stream, _frames, _output_file
    if _stream is None:
        logger.warning("stop_recording called but no stream is active.")
        return None

    try:
        _stream.stop()
        _stream.close()
    except Exception:
        pass

    if not _frames:
        logger.warning("No audio frames captured.")
        _stream = None
        return None

    try:
        audio    = np.concatenate(_frames, axis=0)
        sf.write(_output_file, audio, 16_000)
        abs_path = os.path.abspath(_output_file)
        logger.info("Recording saved: %s", abs_path)
    except Exception as exc:
        logger.error("Failed to write audio: %s", exc)
        abs_path = None

    _stream, _frames, _output_file = None, [], None
    return abs_path