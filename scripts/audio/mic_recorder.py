import sounddevice as sd
import soundfile as sf

def record_audio(
    output_file="recorded_audio.wav",
    duration=30,
    sample_rate=16000
):
    """
    Records audio from system microphone and saves it as a WAV file.
    """

    print("🎙️ Recording... Speak now.")

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    sf.write(output_file, audio, sample_rate)

    print(f"✅ Recording saved as {output_file}")
    return output_file
