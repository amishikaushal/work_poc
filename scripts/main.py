# import os
# import sys

# base_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(base_dir, ".."))
# if parent_dir not in sys.path:
#     sys.path.insert(0, parent_dir)

# # --- NEW IMPORT ---
# # This assumes your summarization script is named final_summarize.py
# from scripts.final_summarize import run_summarization

# # ---------------- PDF PIPELINE ---------------- #

# def process_pdf(input_pdf: str):
#     import pytesseract
#     import cv2
#     import numpy as np
#     from PIL import Image
#     from pdf2image import convert_from_path

#     from scripts.translate_utils import detect_language, translate_text 
#     from scripts.preprocess import clean_medical_report

#     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#     def enhance_image_for_ocr(pil_page):
#         img = np.array(pil_page)
#         img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#         kernel = np.ones((1, 1), np.uint8)
#         processed = cv2.dilate(processed, kernel, iterations=1)
#         processed = cv2.erode(processed, kernel, iterations=1)
#         return Image.fromarray(processed)

#     print(f"--- Starting: {input_pdf} ---")

#     try:
#         pages = convert_from_path(input_pdf)
#     except Exception as e:
#         print(f"Error during PDF conversion: {e}")
#         return

#     full_text = ""
#     for i, page in enumerate(pages):
#         print(f"Processing page {i+1}...")
#         enhanced = enhance_image_for_ocr(page)
#         text = pytesseract.image_to_string(enhanced, lang="eng+fra+spa")
#         full_text += text + "\n"

#     if not full_text.strip():
#         print("Error: No text extracted from PDF.")
#         return

#     detected_lang = detect_language(full_text)
#     if detected_lang != "en":
#         # Fixed: using 'translate_text' as imported above
#         full_text = translate_text(full_text, source_lang=detected_lang, target_lang="en")

#     final_text = clean_medical_report(full_text)

#     os.makedirs("output", exist_ok=True)
#     output_path = os.path.join("output", "transcript.txt")

#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(final_text)

#     print(f"Done! Saved to {os.path.abspath(output_path)}")

#     # --- TRIGGER SUMMARY ---
#     print("\n--- Starting Stage 3: AI Summarization ---")
#     run_summarization()


# # ---------------- AUDIO PIPELINE ---------------- #

# def process_audio(input_file: str):
#     from scripts.audio.audio_preprocess import convert_to_wav
#     from scripts.audio.diarization import diarize_audio
#     from scripts.audio.transcription import transcribe_segments
#     from scripts.audio.role_inference import infer_roles
#     from scripts.translate_utils import save_audio_output

#     print(f"--- Starting Audio Pipeline: {input_file} ---")
    
#     wav_file = convert_to_wav(input_file)
#     diarized = diarize_audio(wav_file)
#     transcript = transcribe_segments(wav_file, diarized)
#     role_map = infer_roles(transcript)

#     # This saves the final diarized text into output/transcript.txt
#     save_audio_output(transcript, role_map, input_file)

#     # --- TRIGGER SUMMARY ---
#     print("\n--- Starting Stage 3: AI Summarization ---")
#     run_summarization()


# # ---------------- MAIN ROUTER ---------------- #

# def main():
#     choice = input(
#         "Choose input type:\n"
#         "1. Upload audio/video/PDF file\n"
#         "2. Record audio from microphone\n"
#         "Enter 1 or 2: "
#     ).strip()

#     if choice == "2":
#         from scripts.audio.mic_recorder import record_audio
#         input_file = record_audio()
#     elif choice == "1":
#         input_file = input("Enter input file path: ").strip()
#     else:
#         print(" Invalid choice.")
#         return

#     if not os.path.exists(input_file):
#         print(" File not found.")
#         return

#     if input_file.lower().endswith(".pdf"):
#         process_pdf(input_file)
#     elif input_file.lower().endswith((".wav", ".mp3", ".mp4", ".m4a", ".mpeg")):
#         process_audio(input_file)
#     else:
#         print(" Unsupported file type.")


# if __name__ == "__main__":
#     main()


import os
import sys

# Standardize pathing so scripts find each other
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(base_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the summarization function
from scripts.final_summarize import run_summarization

# ---------------- PDF PIPELINE ---------------- #

def process_pdf(input_pdf: str):
    import pytesseract
    import cv2
    import numpy as np
    from PIL import Image
    from pdf2image import convert_from_path
    from scripts.translate_utils import detect_language, translate_text 
    from scripts.preprocess import clean_medical_report

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def enhance_image_for_ocr(pil_page):
        img = np.array(pil_page)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.dilate(processed, kernel, iterations=1)
        processed = cv2.erode(processed, kernel, iterations=1)
        return Image.fromarray(processed)

    print(f"--- Starting: {input_pdf} ---")

    try:
        pages = convert_from_path(input_pdf)
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        return

    full_text = ""
    for i, page in enumerate(pages):
        print(f"Processing page {i+1}...")
        enhanced = enhance_image_for_ocr(page)
        text = pytesseract.image_to_string(enhanced, lang="eng+fra+spa")
        full_text += text + "\n"

    if not full_text.strip():
        print("Error: No text extracted from PDF.")
        return

    detected_lang = detect_language(full_text)
    if detected_lang != "en":
        full_text = translate_text(full_text, source_lang=detected_lang, target_lang="en")

    final_text = clean_medical_report(full_text)

    # Save transcript
    output_dir = os.path.join(parent_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    transcript_path = os.path.join(output_dir, "transcript.txt")

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"Done! Transcript saved to {transcript_path}")

    # --- TRIGGER SUMMARY ---
    trigger_summaries(final_text, output_dir)


# ---------------- AUDIO PIPELINE ---------------- #

def process_audio(input_file: str):
    from scripts.audio.audio_preprocess import convert_to_wav
    from scripts.audio.diarization import diarize_audio
    from scripts.audio.transcription import transcribe_segments
    from scripts.audio.role_inference import infer_roles
    from scripts.translate_utils import save_audio_output

    print(f"--- Starting Audio Pipeline: {input_file} ---")
    
    wav_file = convert_to_wav(input_file)
    diarized = diarize_audio(wav_file)
    transcript = transcribe_segments(wav_file, diarized)
    role_map = infer_roles(transcript)

    # save_audio_output writes to output/transcript.txt
    save_audio_output(transcript, role_map, input_file)

    # Read the text back for summarization
    output_dir = os.path.join(parent_dir, "output")
    transcript_path = os.path.join(output_dir, "transcript.txt")
    with open(transcript_path, "r", encoding="utf-8") as f:
        final_text = f.read()

    # --- TRIGGER SUMMARY ---
    trigger_summaries(final_text, output_dir)


# ---------------- HELPER FUNCTION ---------------- #

def trigger_summaries(text_to_summarize, output_folder):
    """Handles calling the AI twice and saving the results."""
    print("\n--- Starting Stage 3: AI Summarization ---")
    
    # Generate Patient Summary
    print("Generating Patient Perspective...")
    pat_summary = run_summarization(text_to_summarize, "Patient")
    
    # Generate Doctor Summary
    print("Generating Doctor Perspective...")
    doc_summary = run_summarization(text_to_summarize, "Doctor")

    # Save to files
    with open(os.path.join(output_folder, "patient_summary.txt"), "w", encoding="utf-8") as f:
        f.write(pat_summary)
    
    with open(os.path.join(output_folder, "doctor_summary.txt"), "w", encoding="utf-8") as f:
        f.write(doc_summary)

    print(f"✅ Summaries saved to {output_folder}")


# ---------------- MAIN ROUTER ---------------- #

def main():
    choice = input(
        "Choose input type:\n"
        "1. Upload audio/video/PDF file\n"
        "2. Record audio from microphone\n"
        "Enter 1 or 2: "
    ).strip()

    if choice == "2":
        from scripts.audio.mic_recorder import record_audio
        input_file = record_audio()
    elif choice == "1":
        input_file = input("Enter input file path: ").strip()
    else:
        print(" Invalid choice.")
        return

    if not os.path.exists(input_file):
        print(" File not found.")
        return

    if input_file.lower().endswith(".pdf"):
        process_pdf(input_file)
    elif input_file.lower().endswith((".wav", ".mp3", ".mp4", ".m4a", ".mpeg")):
        process_audio(input_file)
    else:
        print(" Unsupported file type.")


if __name__ == "__main__":
    main()