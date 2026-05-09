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
import logging
import time
import sounddevice as sd
import soundfile as sf
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def record_audio(
    output_file="recorded_audio.wav",
    duration=30,
    sample_rate=16000
):
    """
    Records audio from the system microphone and saves it as a WAV file.
    Returns the absolute path to the saved file.
    """
    
    start_time = time.time()
    # Ensure the directory exists
    output_dir = os.path.dirname(os.path.abspath(output_file))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger.info(f"Starting audio recording for {duration} seconds")
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
        
        elapsed = time.time() - start_time
        abs_path = os.path.abspath(output_file)
        logger.info(f"Recording saved in {elapsed:.2f}s: {abs_path}")
        print(f"✅ Recording saved as {abs_path}")
        return abs_path

    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return None


# Non-blocking start/stop recording API for UI toggle use
_stream = None
_frames = []
_output_file = None

def start_recording(output_file="recorded_audio.wav", sample_rate=16000):
    """
    Starts a non-blocking recording in the background. Returns the intended output file path.
    Call `stop_recording()` to finish and save the file.
    """
    global _stream, _frames, _output_file
    if _stream is not None:
        return None

    _frames = []
    _output_file = output_file

    def callback(indata, frames, time_info, status):
        if status:
            logger.warning(f"InputStream status: {status}")
        # copy to avoid referencing recycled buffer
        _frames.append(indata.copy())

    try:
        _stream = sd.InputStream(samplerate=sample_rate, channels=1, callback=callback)
        _stream.start()
        logger.info(f"Started non-blocking recording -> {_output_file}")
        return os.path.abspath(_output_file)
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        _stream = None
        return None


def stop_recording():
    """
    Stops a previously started non-blocking recording and writes it to disk.
    Returns the absolute path to the saved WAV file, or None on error.
    """
    global _stream, _frames, _output_file
    if _stream is None:
        logger.warning("stop_recording called but no active stream")
        return None

    try:
        _stream.stop()
        _stream.close()
    except Exception:
        pass

    if not _frames:
        logger.warning("No audio frames captured")
        _stream = None
        return None

    try:
        audio = np.concatenate(_frames, axis=0)
        sf.write(_output_file, audio, 16000)
        abs_path = os.path.abspath(_output_file)
        logger.info(f"Recording saved: {abs_path}")
    except Exception as e:
        logger.error(f"Failed to write recorded file: {e}")
        abs_path = None

    # Cleanup
    _stream = None
    _frames = []
    _output_file = None

    return abs_path