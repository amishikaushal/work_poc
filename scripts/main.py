"""
scripts/main.py
───────────────
Orchestrates the PDF and Audio processing pipelines.
Both functions return (patient_summary, doctor_summary) as strings.
"""
import os
import sys
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Ensure project root is importable from this module
_BASE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_BASE, ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.final_summarize import run_summarization
from scripts.translate_utils import translate_text


# ── Internal helper ────────────────────────────────────────────────────────────

def _generate_summaries(text: str, output_dir: str, target_lang: str):
    """
    Call the AI for Patient and Doctor summaries **in parallel**, optionally
    translate both, persist to disk, and return (patient, doctor) as a tuple.
    """
    # Both API calls are network-bound and independent — run them concurrently
    logger.info("Generating Patient + Doctor summaries in parallel…")
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_patient = pool.submit(run_summarization, text, "Patient")
        fut_doctor  = pool.submit(run_summarization, text, "Doctor")
        patient_en  = fut_patient.result()
        doctor_en   = fut_doctor.result()

    if target_lang != "en":
        logger.info("Translating summaries to '%s'…", target_lang)
        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_p = pool.submit(translate_text, patient_en, "en", target_lang)
            fut_d = pool.submit(translate_text, doctor_en,  "en", target_lang)
            patient_final = fut_p.result()
            doctor_final  = fut_d.result()
    else:
        patient_final, doctor_final = patient_en, doctor_en

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "patient_summary.txt"), "w", encoding="utf-8") as f:
        f.write(patient_final)
    with open(os.path.join(output_dir, "doctor_summary.txt"), "w", encoding="utf-8") as f:
        f.write(doctor_final)

    return patient_final, doctor_final


# ── PDF pipeline ───────────────────────────────────────────────────────────────

def process_pdf(input_pdf: str, target_lang: str):
    """
    PDF → OCR → language normalisation → clean → AI summarise.
    Returns (patient_summary, doctor_summary).
    """
    import pytesseract
    from pdf2image import convert_from_path
    from scripts.preprocess import clean_medical_report
    from scripts.translate_utils import detect_language

    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    pages = convert_from_path(input_pdf)
    full_text = "".join(
        pytesseract.image_to_string(page, lang="eng+fra+spa") + "\n"
        for page in pages
    )

    if not full_text.strip():
        raise ValueError("No text could be extracted from the PDF.")

    detected = detect_language(full_text)
    if detected != "en":
        full_text = translate_text(full_text, source_lang=detected, target_lang="en")

    cleaned    = clean_medical_report(full_text)
    output_dir = os.path.join(_ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(cleaned)

    return _generate_summaries(cleaned, output_dir, target_lang)


# ── Audio pipeline ─────────────────────────────────────────────────────────────

def process_audio(input_file: str, target_lang: str):
    """
    Audio → convert to WAV → diarise → transcribe → infer roles → AI summarise.
    Returns (patient_summary, doctor_summary).
    """
    from scripts.audio.audio_preprocess import convert_to_wav
    from scripts.audio.diarization    import diarize_audio
    from scripts.audio.transcription  import transcribe_segments
    from scripts.audio.role_inference import infer_roles
    from scripts.translate_utils      import save_audio_output

    wav_file   = convert_to_wav(input_file)
    diarized   = diarize_audio(wav_file)
    transcript = transcribe_segments(wav_file, diarized)
    role_map   = infer_roles(transcript)
    save_audio_output(transcript, role_map, input_file)

    output_dir = os.path.join(_ROOT, "output")
    with open(os.path.join(output_dir, "transcript.txt"), "r", encoding="utf-8") as f:
        final_text = f.read()

    return _generate_summaries(final_text, output_dir, target_lang)