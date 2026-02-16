import logging
import time
from nemo.collections.asr.models import SortformerEncLabelModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load model once at module level
_diar_model = None
_model_load_time = None

def _get_diarization_model():
    global _diar_model, _model_load_time
    if _diar_model is None:
        logger.info("Loading diarization model: nvidia/diar_streaming_sortformer_4spk-v2.1")
        model_start = time.time()
        _diar_model = SortformerEncLabelModel.from_pretrained(
            "nvidia/diar_streaming_sortformer_4spk-v2.1"
        )
        _diar_model.eval()
        _model_load_time = time.time() - model_start
        logger.info(f"Diarization model loaded in {_model_load_time:.2f}s")
    else:
        logger.info("Using cached diarization model")
    return _diar_model

def diarize_audio(wav_file: str) -> list[dict]:
    """
    Performs speaker diarization on the given WAV file.
    Identifies who spoke when and assigns speaker labels.
    Returns a list of dictionaries containing start time, end time, and speaker ID.
    """
    start_time = time.time()
    logger.info(f"Starting diarization for: {wav_file}")

    # Get the cached diarization model
    diar_model = _get_diarization_model()

    # Configure streaming-related parameters for diarization
    # chunk_len: size of audio chunks processed at a time
    diar_model.sortformer_modules.chunk_len = 340

    # chunk_right_context: amount of future context used for better accuracy
    diar_model.sortformer_modules.chunk_right_context = 40

    # fifo_len: buffer length for maintaining speaker history
    diar_model.sortformer_modules.fifo_len = 40

    # spkcache_update_period: how often speaker embeddings are updated
    diar_model.sortformer_modules.spkcache_update_period = 300

    # Perform speaker diarization on the input WAV file
    logger.info("Running diarization inference...")
    predicted_segments = diar_model.diarize(
        audio=[wav_file],
        batch_size=1
    )

    # Convert raw diarization output into a structured format
    diarized_segments = []
    for line in predicted_segments[0]:
        # Each line contains: start_time end_time speaker_label
        start, end, speaker = line.split()

        diarized_segments.append({
            "start": float(start),    # Segment start time (seconds)
            "end": float(end),        # Segment end time (seconds)
            "speaker": speaker        # Speaker identifier (e.g., speaker_0)
        })

    elapsed = time.time() - start_time
    logger.info(f"Diarization completed in {elapsed:.2f}s. Found {len(diarized_segments)} segments.")
    # Return the list of diarized speaker segments
    return diarized_segments
