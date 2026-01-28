import os
import whisper
from pydub import AudioSegment

def transcribe_segments(
    wav_file: str,
    diarized_segments: list[dict]
) -> list[dict]:
    """
    Transcribes each diarized speaker segment into English text
    using the Whisper speech-to-text model.
    """

    # Load the full WAV audio file
    audio = AudioSegment.from_wav(wav_file)

    # Load the Whisper model for speech recognition and translation
    whisper_model = whisper.load_model("medium")

    # List to store the final transcribed output
    final_transcript = []

    # Loop through each diarized speaker segment
    for i, segment in enumerate(diarized_segments):
        # Convert start and end times from seconds to milliseconds
        start_ms = int(segment["start"] * 1000)
        end_ms = int(segment["end"] * 1000)

        # Extract the audio chunk corresponding to the speaker segment
        chunk = audio[start_ms:end_ms]

        # Save the audio chunk temporarily as a WAV file
        chunk_file = f"chunk_{i}.wav"
        chunk.export(chunk_file, format="wav")

        # Transcribe and translate the audio chunk to English
        # Whisper automatically detects the spoken language
        result = whisper_model.transcribe(
            chunk_file,
            task="translate"
        )

        # Store the transcribed text along with speaker and timing information
        final_transcript.append({
            "start": segment["start"],      # Segment start time (seconds)
            "end": segment["end"],          # Segment end time (seconds)
            "speaker": segment["speaker"],  # Speaker ID (e.g., speaker_0)
            "text": result["text"].strip()  # Cleaned transcribed text
        })

        # Remove the temporary audio chunk file to save disk space
        os.remove(chunk_file)

    # Sort the transcript so that the conversation appears in correct time order
    final_transcript.sort(key=lambda x: x["start"])

    # Return the fully transcribed and ordered conversation
    return final_transcript
