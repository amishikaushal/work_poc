import os
from pdf2image import convert_from_path
import pytesseract

from preprocess import clean_medical_report
from translate_utils import detect_language, translate_to_english

# UPDATE THIS PATH FOR WINDOWS
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def run_pipeline(input_pdf):
    """
    Main execution:
    PDF -> Image -> OCR -> Language Detection -> Translation -> Cleaned English Text
    """
    print(f" Starting Pipeline for: {input_pdf}")

    try:
        # Step 1: PDF to Image conversion
        pages = convert_from_path(input_pdf)
    except Exception as e:
        return f" Error: Could not convert PDF. Check if 'poppler' is installed.\n{e}"

    full_raw_text = ""
    for i, page in enumerate(pages):
        print(f" Scanning page {i+1}...")

        # Step 2: OCR Stage
        page_text = pytesseract.image_to_string(
            page,
            lang="eng+fra+spa"
        )
        full_raw_text += page_text + "\n"


    # OPTIONAL: Debug OCR output (useful for regex tuning)
    print("\n--- RAW OCR TEXT PREVIEW ---")
    print(full_raw_text[:600])

    # Step 3: Language Detection
    print(" Detecting language...")
    lang = detect_language(full_raw_text)
    print(f" Detected language: {lang}")

    # Step 4: Translation (if required)
    print(" Translating to English (if needed)...")

    # Force translation if accented / non-ASCII characters exist
    needs_translation = (
        lang != "en" or
        any(ord(c) > 127 for c in full_raw_text)
    )

    print(f" Translation forced: {needs_translation}")

    english_text = (
        translate_to_english(full_raw_text, lang)
        if needs_translation
        else full_raw_text
    )


    # Step 5: Preprocessing (Cleaning the noise)
    print(" Filtering medical noise and headers...")
    final_data = clean_medical_report(english_text)

    return final_data


if __name__ == "__main__":
    INPUT_FILE = "input/fr1.pdf"
    OUTPUT_FILE = "output/output1_cleaned.txt"

    if not os.path.exists("output"):
        os.makedirs("output")

    if os.path.exists(INPUT_FILE):
        clean_text = run_pipeline(INPUT_FILE)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(clean_text)

        print("\n Processing Complete!")
        print(f" Result saved to: {OUTPUT_FILE}")
        print("\n--- CLEANED TEXT PREVIEW ---")
        print(clean_text[:600])
    else:
        print(f" Error: {INPUT_FILE} not found. Ensure it is in the 'input' folder.")
