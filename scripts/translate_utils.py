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