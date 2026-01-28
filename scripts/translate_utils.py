import requests
from langdetect import detect

def detect_language(text):
    """Local and Free detection using langdetect."""
    try:
        return detect(text[:500])
    except:
        return "en"

def translate_text(text, source_lang="auto", target_lang="en"):
    """
    Universal Translator for Stage 1 (OCR Cleanup) and Stage 2 (Final Summary).
    """
    if source_lang == target_lang:
        return text

    # Handle character limits by chunking
    MAX_CHARS = 4500 
    chunks = [text[i:i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
    translated_parts = []

    url = "https://translate.googleapis.com/translate_a/single"
    
    try:
        for chunk in chunks:
            params = {
                "client": "gtx",
                "sl": source_lang,
                "tl": target_lang,
                "dt": "t",
                "q": chunk
            }
            
            response = requests.get(url, params=params, timeout=15)
            result = response.json()
            
            # Reconstruct the text from the JSON response structure
            chunk_translation = "".join([part[0] for part in result[0] if part[0]])
            translated_parts.append(chunk_translation)

        return " ".join(translated_parts)

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
