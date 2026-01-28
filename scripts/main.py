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

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def enhance_image_for_ocr(pil_page):
        img = np.array(pil_page)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]
        return Image.fromarray(processed)

    print(f"--- Starting: {input_pdf} ---")

    pages = convert_from_path(input_pdf)
    full_text = ""

    for i, page in enumerate(pages):
        print(f"Processing page {i+1}...")
        enhanced = enhance_image_for_ocr(page)
        text = pytesseract.image_to_string(enhanced, lang="eng+fra+spa")
        full_text += text + "\n"

    detected_lang = detect_language(full_text)

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

    else:
        print("❌ Unsupported file type.")


if __name__ == "__main__":
    main()
