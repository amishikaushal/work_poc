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