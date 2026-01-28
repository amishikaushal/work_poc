import requests

LIBRE_URL = "https://libretranslate.com"

def detect_language(text):
    try:
        response = requests.post(
            f"{LIBRE_URL}/detect",
            json={"q": text},
            timeout=10
        )
        data = response.json()

        # Case 1: Expected list response
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("language", "en")

        # Case 2: Dict response (fallback)
        if isinstance(data, dict):
            return data.get("language", "en")

    except Exception as e:
        print(f" Language detection failed: {e}")

    # Safe default
    return "en"


def translate_to_english(text, source_lang):
    if source_lang == "en":
        return text

    translated_chunks = []
    CHUNK_SIZE = 800  # safe size for LibreTranslate

    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i:i + CHUNK_SIZE]

        try:
            response = requests.post(
                f"{LIBRE_URL}/translate",
                json={
                    "q": chunk,
                    "source": source_lang,
                    "target": "en",
                    "format": "text"
                },
                timeout=15
            )

            data = response.json()
            translated_chunks.append(
                data.get("translatedText", chunk)
            )

        except Exception as e:
            print(f" Translation chunk failed: {e}")
            translated_chunks.append(chunk)

    return "".join(translated_chunks)
