# import sounddevice as sd
# import soundfile as sf

# def record_audio(
#     output_file="recorded_audio.wav",
#     duration=30,
#     sample_rate=16000
# ):
#     """
#     Records audio from system microphone and saves it as a WAV file.
#     """

#     print("🎙️ Recording... Speak now.")

#     audio = sd.rec(
#         int(duration * sample_rate),
#         samplerate=sample_rate,
#         channels=1,
#         dtype="int16"
#     )

#     sd.wait()

#     sf.write(output_file, audio, sample_rate)

#     print(f"✅ Recording saved as {output_file}")
#     return output_file


import os
import sounddevice as sd
import soundfile as sf
import numpy as np

def record_audio(
    output_file="recorded_audio.wav",
    duration=30,
    sample_rate=16000
):
    """
    Records audio from the system microphone and saves it as a WAV file.
    Returns the absolute path to the saved file.
    """
    # Ensure the directory exists
    output_dir = os.path.dirname(os.path.abspath(output_file))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🎙️ Recording for {duration} seconds... Speak now.")

    try:
        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()  # Wait for the recording to finish
        
        # Save the file
        sf.write(output_file, audio, sample_rate)
        
        abs_path = os.path.abspath(output_file)
        print(f"✅ Recording saved as {abs_path}")
        return abs_path

    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return None