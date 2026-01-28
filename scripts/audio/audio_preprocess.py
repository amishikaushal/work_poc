import os
import subprocess

def convert_to_wav(input_file: str) -> str:
    """
    Converts an input audio/video file into a 16kHz mono WAV file.
    This format is required for speaker diarization and transcription models.
    Returns the path to the WAV file.
    """

    # If the input file is already a WAV file, no conversion is needed
    if input_file.lower().endswith(".wav"):
        return input_file

    # Extract the base file name (without extension)
    base_name = os.path.splitext(input_file)[0]

    # Create the output WAV file name
    wav_file = base_name + ".wav"

    # Use FFmpeg to convert the input file to:
    # - mono audio (1 channel)
    # - 16,000 Hz sampling rate
    subprocess.run(
        [
            "ffmpeg", "-y",          # Overwrite output file if it exists
            "-i", input_file,        # Input audio/video file
            "-ac", "1",              # Convert to mono
            "-ar", "16000",          # Set sampling rate to 16kHz
            wav_file                 # Output WAV file
        ],
        check=True                  # Raise error if FFmpeg fails
    )

    # Return the path of the converted WAV file
    return wav_file
