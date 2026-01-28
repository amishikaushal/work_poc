import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from translate_utils import detect_language, translate_to_english
from preprocess import clean_medical_report

# UPDATE THIS TO YOUR PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def enhance_image_for_ocr(pil_page):
    """
    Applies Grayscale, Thresholding, and Denoising to improve Tesseract accuracy.
    """
    # Convert PIL to OpenCV format (numpy array)
    img = np.array(pil_page)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # 1. Convert to Gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Apply Adaptive Thresholding (Binarization)
    # This makes the background pure white and text pure black
    processed_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # 3. Denoise (removes small "specks" that look like punctuation)
    kernel = np.ones((1, 1), np.uint8)
    processed_img = cv2.dilate(processed_img, kernel, iterations=1)
    processed_img = cv2.erode(processed_img, kernel, iterations=1)

    # Convert back to PIL for Tesseract
    return Image.fromarray(processed_img)

def run_pipeline(input_pdf):
    print(f"--- Starting: {input_pdf} ---")

    # 1. PDF to Images
    try:
        pages = convert_from_path(input_pdf)
    except Exception as e:
        return f"Error: {e}"

    # 2. Image Enhancement & OCR
    full_text = ""
    for i, page in enumerate(pages):
        print(f"Processing & Scanning page {i+1}...")
        
        # --- NEW ENHANCEMENT STEP ---
        enhanced_page = enhance_image_for_ocr(page)
        
        # Scan the ENHANCED version instead of the raw one
        page_text = pytesseract.image_to_string(enhanced_page, lang="eng+fra+spa")
        full_text += page_text + "\n"

    # 3. Detect & Translate
    detected_lang = detect_language(full_text)
    print(f"Detected: {detected_lang}")

    if detected_lang != "en":
        print(f"Converting {detected_lang} -> English...")
        english_text = translate_to_english(full_text, detected_lang)
    else:
        print("Already English. No translation needed.")
        english_text = full_text

    # 4. Clean and Format
    final_output = clean_medical_report(english_text)
    return final_output

if __name__ == "__main__":
    INPUT_FILE = "input/Data2.pdf" 
    OUTPUT_FILE = "output/Data2.txt"

    if not os.path.exists("output"): os.makedirs("output")

    if os.path.exists(INPUT_FILE):
        result = run_pipeline(INPUT_FILE)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Done! Saved to {OUTPUT_FILE}")
    else:
        print("Input file not found.")