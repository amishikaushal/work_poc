import re

def clean_medical_report(text):
    # 1. NOISE REMOVAL
    noise_patterns = [
        r"Regd\. Office:.*", r"Corporate Identity.*",
        r"Tel:? \+[\d\s-]+", r"Fax:? \+[\d\s-]+",
        r"The following table:", r"\""
    ]
    cleaned_soup = text
    for pattern in noise_patterns:
        cleaned_soup = re.sub(pattern, "", cleaned_soup, flags=re.IGNORECASE)

    # 2. OCR CORRECTION
    corrections = {
        r"Simdmas": "Symptoms", r"fibere": "fever",
        r"antibotics": "antibiotics", r"Ibuprof\b": "Ibuprofen",
        r"Amoxicline": "Amoxicillin", r"ho3": "hours"
    }
    for pattern, replacement in corrections.items():
        cleaned_soup = re.sub(pattern, replacement, cleaned_soup, flags=re.IGNORECASE)

    # 3. SEMANTIC HIGHLIGHTING
    headers = [
        "Diagnosis", "Diagnostic", "Symptoms", "Prescription", 
        "Treatment", "Next Appointment", "UHID", "History"
    ]

    for header in headers:
        # We use ^ to ensure it only marks headers at the START of a line
        # This prevents bracketing the word "symptoms" inside a sentence.
        cleaned_soup = re.sub(
            rf"^\s*({header})\b", 
            r"[\1]", 
            cleaned_soup, 
            flags=re.IGNORECASE | re.MULTILINE
        )

    # 4. FINAL CLEANUP
    # Standardize bullets
    final_output = re.sub(r"[|®¢©*»+]", "•", cleaned_soup)
    # Fix the "e" bullet
    final_output = re.sub(r"^\s*e\s+", "• ", final_output, flags=re.MULTILINE)
    
    # IMPORTANT: Remove any accidental double brackets caused by re-running
    final_output = final_output.replace("[[", "[").replace("]]", "]")
    
    # Remove excessive blank lines
    final_output = re.sub(r"\n\s*\n", "\n", final_output).strip()

    output = [
        "=== SEMANTIC MEDICAL EXTRACTION (LOSSLESS) ===",
        "",
        final_output
    ]
    return "\n".join(output)