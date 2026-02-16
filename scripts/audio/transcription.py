import os
import logging
import time
import numpy as np
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try faster-whisper first, fallback to openai-whisper
_use_faster_whisper = False
try:
    from faster_whisper import WhisperModel
    _use_faster_whisper = True
    logger.info("Using faster-whisper backend")
except ImportError:
    logger.warning("faster-whisper not available, falling back to openai-whisper")
    import whisper as openai_whisper
    _use_faster_whisper = False

# Optional Streamlit caching
try:
    import streamlit as st
    _have_streamlit = True
except Exception:
    _have_streamlit = False

# Module-level cache
_whisper_model = None


def _load_faster_whisper():
    logger.info("Loading faster-whisper model: medium (device=cpu, compute_type=int8)")
    start = time.time()
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    elapsed = time.time() - start
    logger.info(f"Faster-Whisper model loaded in {elapsed:.2f}s")
    return model


def _load_openai_whisper():
    logger.info("Loading openai-whisper model: medium")
    start = time.time()
    model = openai_whisper.load_model("medium")
    elapsed = time.time() - start
    logger.info(f"OpenAI Whisper model loaded in {elapsed:.2f}s")
    return model


if _have_streamlit:
    @st.cache_resource
    def _get_whisper_model():
        if _use_faster_whisper:
            return _load_faster_whisper()
        else:
            return _load_openai_whisper()
else:
    def _get_whisper_model():
        global _whisper_model
        if _whisper_model is None:
            if _use_faster_whisper:
                _whisper_model = _load_faster_whisper()
            else:
                _whisper_model = _load_openai_whisper()
        else:
            logger.info("Using cached model")
        return _whisper_model


def transcribe_segments(
    wav_file: str,
    diarized_segments: list[dict]
) -> list[dict]:
    """
    Transcribes each diarized speaker segment into English text.
    Uses faster-whisper if available, otherwise falls back to openai-whisper.
    """
    start_time = time.time()
    logger.info(f"Starting transcription for: {wav_file} with {len(diarized_segments)} segments")
    logger.info(f"Backend: {'faster-whisper' if _use_faster_whisper else 'openai-whisper'}")

    # Load the full WAV audio file once and normalize format
    audio = AudioSegment.from_wav(wav_file)
    audio = audio.set_channels(1).set_frame_rate(16000)

    model = _get_whisper_model()
    final_transcript = []

    for i, segment in enumerate(diarized_segments):
        seg_start_time = time.time()

        # Convert times to milliseconds and extract chunk
        start_ms = int(segment["start"] * 1000)
        end_ms = int(segment["end"] * 1000)
        chunk = audio[start_ms:end_ms]

        # Convert to numpy float32 (-1.0 .. 1.0)
        samples = np.array(chunk.get_array_of_samples())
        sample_width = chunk.sample_width
        max_val = float(2 ** (8 * sample_width - 1))
        audio_np = samples.astype(np.float32) / max_val

        # Transcribe based on backend
        if _use_faster_whisper:
            # faster-whisper returns (segments_iter, info)
            segments_iter, info = model.transcribe(
                audio_np,
                beam_size=5,
                language="en",
                task="translate"
            )
            chunk_text = "".join([s.text for s in segments_iter]).strip()
        else:
            # openai-whisper returns dict with "text" key
            result = model.transcribe(
                audio_np,
                language="en",
                task="translate"
            )
            chunk_text = result["text"].strip()

        final_transcript.append({
            "start": segment["start"],
            "end": segment["end"],
            "speaker": segment["speaker"],
            "text": chunk_text,
        })

        seg_elapsed = time.time() - seg_start_time
        logger.info(f"Segment {i+1}/{len(diarized_segments)} ({segment['speaker']}) transcribed in {seg_elapsed:.2f}s")

    final_transcript.sort(key=lambda x: x["start"])
    elapsed = time.time() - start_time
    logger.info(f"Transcription completed in {elapsed:.2f}s. Total text segments: {len(final_transcript)}")
    return final_transcript
