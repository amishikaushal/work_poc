from collections import defaultdict

def infer_roles(segments: list[dict]) -> dict:
    """
    Infers Doctor / Patient roles based on spoken content.
    Returns a dictionary mapping speaker IDs to their roles.
    """

    # Dictionary to collect all spoken text for each speaker
    # Example: {"speaker_0": "text...", "speaker_1": "text..."}
    speaker_text = defaultdict(str)

    # Combine all text spoken by each speaker
    for seg in segments:
        speaker_text[seg["speaker"]] += " " + seg["text"]

    # Keywords that are commonly used by doctors during consultations
    doctor_keywords = [
        "since when", "how long", "do you have",
        "any history", "diagnosis", "treatment",
        "prescribe", "recommend", "you should"
    ]

    # Function to calculate a "doctor-likeness" score for a speaker
    # The more medical or questioning keywords found, the higher the score
    def score(text: str) -> int:
        text = text.lower()
        return sum(kw in text for kw in doctor_keywords)

    # Calculate scores for each speaker based on their spoken content
    scores = {spk: score(txt) for spk, txt in speaker_text.items()}

    # The speaker with the highest score is assumed to be the doctor
    doctor_speaker = max(scores, key=scores.get)

    # Assign roles to each speaker
    role_map = {}
    for spk in scores:
        role_map[spk] = "Doctor" if spk == doctor_speaker else "Patient"

    # Return the final mapping of speaker IDs to roles
    return role_map
