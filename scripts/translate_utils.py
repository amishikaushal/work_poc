from langdetect import detect
from deep_translator import GoogleTranslator

def detect_language(text):
    try:
        # We only need the first few hundred characters for accurate detection
        return detect(text[:500])
    except:
        return "en"

def translate_to_english(text, source_lang):
    if source_lang == "en":
        return text
    
    try:
        # deep-translator handles long text by chunking it automatically
        return GoogleTranslator(source=source_lang, target='en').translate(text)
    except Exception as e:
        print(f"!!! Translation Error: {e}")
        return text
    

import os

def save_audio_output(
    segments: list[dict],
    role_map: dict,
    input_file: str
):
    # Define the output directory where the final transcript will be stored
    output_dir = "Output"

    # Create the output directory if it does not already exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract the base name of the input audio/video file (without extension)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Create the final output file path
    output_path = os.path.join(
        output_dir,
        base_name + "_diarized_english.txt"
    )

    # Write the final diarized transcript to a text file
    # Speaker IDs are replaced with inferred roles (Doctor / Patient)
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            role = role_map[seg["speaker"]]
            f.write(f"{role}: {seg['text']}\n")

    # Print confirmation message after saving the output
    print(f"✅ Output saved at {output_path}")
