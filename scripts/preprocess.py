import re
from googletrans import Translator

def clean_medical_report(raw_text):
    # 1. TRANSLATION (Translates the entire "soup" to keep it all in English)
    try:
        translator = Translator()
        text = translator.translate(raw_text, dest='en').text
    except:
        text = raw_text

    # 2. SURGICAL NOISE REMOVAL (ONLY remove the specific corporate junk)
    # We leave UHIDs, Dates, and all medical words untouched.
    noise_patterns = [
        r"Regd\. Office:.*", 
        r"Corporate Identity.*",
        r"Tel \+[\d\s-]+", 
        r"Fax:[\d\s-]+",
        r"The following table:",
        r"\"" # Remove stray OCR quotes
    ]
    
    # We execute the cleaning on the whole text
    cleaned_soup = text
    for pattern in noise_patterns:
        cleaned_soup = re.sub(pattern, "", cleaned_soup, flags=re.I)

    # 3. SEMANTIC HIGHLIGHTING
    # Instead of 'extracting', we just find headers and wrap them in [brackets]
    # This ensures that even if a header is in the middle of a sentence, NO DATA IS LOST.
    headers = [
        "Diagnosis", "Symptoms", "Consultant Notes", "Treatment advised", 
        "Prescription", "Surgery", "Procedure", "Medications", "UHID", 
        "Hospital No", "Patient Identifier", "Admission", "Discharge"
    ]
    
    for header in headers:
        # This adds a newline and brackets around any header found in the text
        cleaned_soup = re.sub(f"({header})", r"\n[\1]\n", cleaned_soup, flags=re.I)

    # 4. FINAL CLEANUP
    # Standardize bullet points from OCR artifacts and tighten spacing
    final_output = re.sub(r"[|®¢©*]", "•", cleaned_soup)
    final_output = re.sub(r"\n\s*\n", "\n", final_output).strip()

    # 5. ASSEMBLY
    output = [
        "=== SEMANTIC MEDICAL EXTRACTION (LOSSLESS) ===",
        "\n" + final_output
    ]

    return "\n".join(output)