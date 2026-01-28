import os

# ---------------- PDF PIPELINE ---------------- #

def process_pdf(input_pdf: str):
    import pytesseract
    import cv2
    import numpy as np
    from PIL import Image
    from pdf2image import convert_from_path

    from scripts.translate_utils import detect_language, translate_to_english
    from scripts.preprocess import clean_medical_report
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from translate_utils import detect_language, translate_text 
from preprocess import clean_medical_report

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def enhance_image_for_ocr(pil_page):
        img = np.array(pil_page)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]
        return Image.fromarray(processed)
def enhance_image_for_ocr(pil_page):
    """
    Applies Grayscale, Thresholding, and Denoising to improve Tesseract accuracy.
    """
    img = np.array(pil_page)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    kernel = np.ones((1, 1), np.uint8)
    processed_img = cv2.dilate(processed_img, kernel, iterations=1)
    processed_img = cv2.erode(processed_img, kernel, iterations=1)

    return Image.fromarray(processed_img)

def run_pipeline(input_pdf, user_target_lang):
    """
    Processes OCR to English. Stage 2 is prepared but disabled for current usage.
    """
    print(f"--- Starting: {input_pdf} ---")

    pages = convert_from_path(input_pdf)
    # 1. PDF to Images
    try:
        pages = convert_from_path(input_pdf)
    except Exception as e:
        return f"Error during PDF conversion: {e}"

    # 2. Image Enhancement & OCR
    full_text = ""

    for i, page in enumerate(pages):
        print(f"Processing page {i+1}...")
        enhanced = enhance_image_for_ocr(page)
        text = pytesseract.image_to_string(enhanced, lang="eng+fra+spa")
        full_text += text + "\n"
        print(f"Processing & Scanning page {i+1}...")
        enhanced_page = enhance_image_for_ocr(page)
        page_text = pytesseract.image_to_string(enhanced_page, lang="eng+fra+spa")
        full_text += page_text + "\n"

    if not full_text.strip():
        return "Error: No text extracted from PDF."

    # 3. STAGE 1: Detect & Translate to English for processing
    detected_lang = detect_language(full_text)
    print(f"Detected Language: {detected_lang}")

    if detected_lang != "en":
        full_text = translate_to_english(full_text, detected_lang)

    final_text = clean_medical_report(full_text)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join(
        "output",
        os.path.splitext(os.path.basename(input_pdf))[0] + ".txt"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"Done! Saved to {output_path}")


# ---------------- AUDIO PIPELINE ---------------- #

# ---------------- AUDIO PIPELINE ---------------- #

def process_audio(input_file: str):
    # Import audio-related modules ONLY when audio processing is required
    # (lazy imports to avoid loading audio dependencies during PDF processing)
    from scripts.audio.audio_preprocess import convert_to_wav
    from scripts.audio.diarization import diarize_audio
    from scripts.audio.transcription import transcribe_segments
    from scripts.audio.role_inference import infer_roles
    from scripts.translate_utils import save_audio_output

    # Step 1: Convert input audio/video file to 16kHz mono WAV format
    # This ensures compatibility with diarization and transcription models
    wav_file = convert_to_wav(input_file)

    # Step 2: Perform speaker diarization
    # This identifies "who spoke when" and returns speaker segments with timestamps
    diarized = diarize_audio(wav_file)

    # Step 3: Transcribe each diarized speaker segment
    # Whisper is used to convert speech (any language) into English text
    transcript = transcribe_segments(wav_file, diarized)

    # Step 4: Infer speaker roles (Doctor / Patient)
    # This is done using semantic analysis of the spoken text
    role_map = infer_roles(transcript)

    # Step 5: Save the final output to a text file
    # Speaker labels are replaced with Doctor / Patient
    # Timestamps are removed in the final output
    save_audio_output(transcript, role_map, input_file)



# ---------------- MAIN ROUTER ---------------- #

def main():
    input_file = input("Enter input file path (PDF / audio / video): ").strip()

    if not os.path.exists(input_file):
        print("❌ File not found.")
        return

    if input_file.lower().endswith(".pdf"):
        process_pdf(input_file)

    elif input_file.lower().endswith((".wav", ".mp3", ".mp4", ".m4a",".mpeg")):
        process_audio(input_file)

        print(f"Stage 1: Converting {detected_lang} -> English for analysis...")
        english_text = translate_text(full_text, source_lang=detected_lang, target_lang="en")
    else:
        print("❌ Unsupported file type.")
        english_text = full_text

    # 4. Clean and Format (English-based preprocessing)
    processed_english_text = clean_medical_report(english_text)

    # --- STAGE 2 BYPASS ---
    # We stop here so the other team gets the English text for summarizing.
    # The following line is what will be used LATER:
    # final_output = translate_text(processed_english_text, source_lang="en", target_lang=user_target_lang)
    
    return processed_english_text

if __name__ == "__main__":
    main()

    # Keeping this for later usage by the other team
    USER_PREF_LANG = "hi" 

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    INPUT_FILE = os.path.join(base_dir, "..", "input", "fr1.pdf")
    # Output file is now marked as 'en' since we aren't doing the final translation yet
    OUTPUT_FILE = os.path.join(base_dir, "..", "output", "processed_en_report.txt")

    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)

    if os.path.exists(INPUT_FILE):
        result = run_pipeline(INPUT_FILE, USER_PREF_LANG)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Done! English processed report saved at {OUTPUT_FILE}")
    else:
        print(f"Input file not found at: {os.path.abspath(INPUT_FILE)}")