import os
from pdf2image import convert_from_path
import pytesseract
from preprocess import clean_medical_report

# Use the exact path your terminal confirmed
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

def run_pipeline(input_pdf):
    """
    Main execution: PDF -> Image -> OCR -> Cleaned English Text.
    """
    print(f"🚀 Starting Pipeline for: {input_pdf}")
    
    try:
        # Step 1: PDF to Image conversion
        pages = convert_from_path(input_pdf)
    except Exception as e:
        return f"❌ Error: Could not convert PDF. Check if 'poppler' is installed. {e}"

    full_raw_text = ""
    for i, page in enumerate(pages):
        print(f"🔍 Scanning page {i+1}...")
        
        # Step 2: OCR Stage
        # This uses the tesseract engine to "read" the image
        page_text = pytesseract.image_to_string(page)
        full_raw_text += page_text + "\n"

    # Step 3: Preprocessing (Cleaning the noise)
    print("🧹 Filtering medical noise and headers...")
    final_data = clean_medical_report(full_raw_text)
    
    return final_data

if __name__ == "__main__":
    # Settings for your folder structure
    INPUT_FILE = "input/input5.pdf" 
    OUTPUT_FILE = "output/output5_cleaned.txt"
    
    if not os.path.exists("output"):
        os.makedirs("output")
    
    if os.path.exists(INPUT_FILE):
        clean_text = run_pipeline(INPUT_FILE)
        
        with open(OUTPUT_FILE, "w") as f:
            f.write(clean_text)
            
        print(f"\n✅ Processing Complete!")
        print(f"📄 Result saved to: {OUTPUT_FILE}")
        print("\n--- TEXT PREVIEW ---")
        print(clean_text[:600]) 
    else:
        print(f"❌ Error: {INPUT_FILE} not found. Ensure it is in the 'input' folder.")