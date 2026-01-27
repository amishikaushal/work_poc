import re
from googletrans import Translator

def clean_medical_report(raw_text):
    # 1. TRANSLATION PIVOT
    try:
        translator = Translator()
        text = translator.translate(raw_text, dest='en').text
    except:
        text = raw_text

 
    noise = [r"The following table:", r"Details", r"Patient Identifier", r"Hospital No", r"Episode No", r"\""]
    for n in noise:
        text = re.sub(n, "", text, flags=re.I)

  
    pt_match = re.search(r"(?:Mr\.|Ms\.|Mrs\.|Ms)\s+([A-Z][A-Z\s]+|[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
    
    # Provider: Look for Dr. or DR followed by the name
    dr_match = re.search(r"(?:Dr\.|DR|Doctor)\s+([A-Z][A-Z\s]+|[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
    
    # Age/Sex: Looking for the specific combo patterns found in Apollo and Human Care
    age_sex = re.search(r"(\d+\s*(?:yrs|yr|Yr|year)\s*(?:/|Mth)?\s*\d*\s*(?:Male|Female|M|F)?)", text, re.I)
    
    # Weight: Capture the weight specifically
    weight = re.search(r"(\d+\s*Kg)", text, re.I)

    # 4. SECTION SPLITTING (Unchanged Logic, but adds Weight as a header)
    headers = ["Diagnosis", "Symptoms", "Consultant Notes", "Treatment advised", "Prescription", "Surgery", "Procedure", "Medications"]
    header_regex = r"(" + "|".join(headers) + r")"
    segments = re.split(header_regex, text, flags=re.I)

    # 5. ASSEMBLY
    output = ["=== UNIVERSAL MEDICAL SUMMARY ==="]
    
    output.append(f"[PROVIDER] : {dr_match.group(0).strip() if dr_match else 'Not Detected'}")
    output.append(f"[PATIENT]  : {pt_match.group(0).strip() if pt_match else 'Not Detected'}")
    output.append(f"[AGE/SEX]  : {age_sex.group(0).strip() if age_sex else 'Not Detected'}")
    if weight: output.append(f"[WEIGHT]   : {weight.group(0).strip()}")

    output.append("\n" + "="*40 + "\nCLEANED CLINICAL DATA\n" + "="*40)

    if len(segments) > 1:
        for i in range(1, len(segments), 2):
            label = segments[i].upper().strip()
            content = segments[i+1].strip()
            # Remove administrative footers from segments
            content = re.split(r"Regd\. Office|Corporate Identity|Tel \+|Fax:", content, flags=re.I)[0].strip()
            content = re.sub(r"[|®¢©*]", "•", content)
            
            if len(content) > 3:
                output.append(f"\n[{label}]\n{content}")
    else:
        output.append("\n[RAW CONTENT]\n" + text.strip())

    return "\n".join(output)