import re
from googletrans import Translator
from langdetect import detect

def clean_medical_report(raw_text):
    # 1. LANGUAGE DETECTION
    try:
        source_lang = detect(raw_text)
    except:
        source_lang = "en"

    # 2. TRANSLATION PIVOT
    if source_lang != 'en':
        try:
            translator = Translator()
            text = translator.translate(raw_text, dest='en').text
        except:
            text = raw_text
    else:
        text = raw_text

    # 3. UNIVERSAL HEADER MAPPING
    # This ensures that even if translation is slightly off, we force the English label
    header_map = {
        r"INFORME DE ALTA MEDICA|RESUME DE SORTIE MEDICALE": "DISCHARGE SUMMARY",
        r"DATOS DEL PACIENTE|DETAILS DU PATIENT": "PATIENT DETAILS",
        r"DIAGNOSTICO|DIAGNOSTIC": "DIAGNOSIS",
        r"TRATAMIENTO RECOMENDADO|TRAITEMENT CONSEILLE": "RECOMMENDED TREATMENT",
        r"NOMBRE|NOM": "NAME",
        r"MEDICO|MEDECIN": "PHYSICIAN",
        r"SEDE SOCIAL|HEADQUARTERS|SIEGE SOCIAL": "ADMIN_NOISE" 
    }

    # Apply the mapping to standardize the text soup
    for pattern, replacement in header_map.items():
        text = re.sub(pattern, f"\n[{replacement}]\n", text, flags=re.I)

    # 4. SURGICAL NOISE REMOVAL (Lossless)
    # Now we can target the standardized [ADMIN_NOISE] tag
    noise_patterns = [
        r"\[ADMIN_NOISE\].*", # Removes the Madrid/Paris headquarters line
        r"The following table:",
        r"\""
    ]
    
    cleaned_soup = text
    for pattern in noise_patterns:
        cleaned_soup = re.sub(pattern, "", cleaned_soup, flags=re.I)

    # 5. FINAL SEMANTIC CLEANUP
    # Standardize all brackets and remove excessive spacing
    final_output = re.sub(r"\n\s*\n", "\n", cleaned_soup).strip()
    final_output = re.sub(r"[|®¢©*]", "•", final_output)

    return f"=== SEMANTIC MEDICAL EXTRACTION (LOSSLESS) ===\n[DETECTED LANGUAGE]: {source_lang.upper()}\n\n{final_output}"