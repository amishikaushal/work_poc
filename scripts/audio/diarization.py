from nemo.collections.asr.models import SortformerEncLabelModel

def diarize_audio(wav_file: str) -> list[dict]:
    """
    Performs speaker diarization on the given WAV file.
    Identifies who spoke when and assigns speaker labels.
    Returns a list of dictionaries containing start time, end time, and speaker ID.
    """

    # Load the pre-trained NVIDIA NeMo Sortformer diarization model
    # This model is optimized for streaming and multi-speaker scenarios
    diar_model = SortformerEncLabelModel.from_pretrained(
        "nvidia/diar_streaming_sortformer_4spk-v2.1"
    )

    # Set the model to evaluation mode (no training)
    diar_model.eval()

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

    # Return the list of diarized speaker segments
    return diarized_segments
