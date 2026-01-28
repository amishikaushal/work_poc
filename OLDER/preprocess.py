import re

def clean_medical_report(text):
    """
    Assumes input text is ALREADY IN ENGLISH.
    Multilingual handling is done BEFORE this step.
    Performs lossless cleaning and semantic highlighting only.
    """

    # 1. SURGICAL NOISE REMOVAL (ONLY remove specific corporate junk)
    noise_patterns = [
        r"Regd\. Office:.*", 
        r"Corporate Identity.*",
        r"Tel \+[\d\s-]+", 
        r"Fax:[\d\s-]+",
        r"The following table:",
        r"\""
    ]

    cleaned_soup = text
    for pattern in noise_patterns:
        cleaned_soup = re.sub(pattern, "", cleaned_soup, flags=re.IGNORECASE)

    # 2. SEMANTIC HIGHLIGHTING (LOSSLESS)
    # We do NOT extract, we only mark headers
    headers = [
        "Diagnosis", "Symptoms", "Consultant Notes", "Treatment advised", 
        "Prescription", "Surgery", "Procedure", "Medications", "UHID", 
        "Hospital No", "Patient Identifier", "Admission", "Discharge"
    ]

    for header in headers:
        cleaned_soup = re.sub(
            rf"({header})",
            r"\n[\1]\n",
            cleaned_soup,
            flags=re.IGNORECASE
        )

    # 3. FINAL CLEANUP
    final_output = re.sub(r"[|®¢©*]", "•", cleaned_soup)
    final_output = re.sub(r"\n\s*\n", "\n", final_output).strip()

    # 4. ASSEMBLY
    output = [
        "=== SEMANTIC MEDICAL EXTRACTION (LOSSLESS) ===",
        "",
        final_output
    ]

    return "\n".join(output)
