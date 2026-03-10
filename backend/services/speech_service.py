"""
Speech service - mock Whisper transcription for demo.
Real version would call openai.Audio.transcribe() or faster-whisper.
"""
import random
from utils.helpers import parse_income_from_text, parse_occupation_from_text, parse_age_from_text, parse_state_from_text

# Demo transcripts that simulate what users would say
DEMO_TRANSCRIPTS = [
    "I am a construction worker earning 10000 rupees per month. I live in Tamil Nadu.",
    "My name is Lakshmi. I work as a domestic help. My income is 9000 rupees. I am from Karnataka.",
    "I am a farmer from Andhra Pradesh. I earn about 12000 rupees a month and I have 2 acres of land.",
    "Main ek majdoor hoon. Meri income 8000 rupees hai. Main Rajasthan se hoon.",
]


def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """
    Mock transcription - returns a demo transcript.
    Real implementation: openai.Audio.transcribe(model="whisper-1", file=audio_bytes)
    """
    # In a real system: call Whisper API or local model
    # For demo, return a random demo transcript
    return random.choice(DEMO_TRANSCRIPTS)


def extract_info_from_text(text: str) -> dict:
    """
    Parse natural language text to extract citizen profile fields.
    """
    profile = {
        "source": "voice",
        "raw_text": text,
        "name": None,
        "age": parse_age_from_text(text),
        "occupation": parse_occupation_from_text(text),
        "income": parse_income_from_text(text),
        "state": parse_state_from_text(text),
        "gender": None,
        "bpl_card": ("bpl" in text.lower() or "ration" in text.lower()),
        "has_land": ("land" in text.lower() or "acres" in text.lower() or "bigha" in text.lower()),
    }

    # Try to extract name
    import re
    name_match = re.search(r'(?:my name is|i am|main hoon)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)', text, re.IGNORECASE)
    if name_match:
        profile["name"] = name_match.group(1).strip().title()

    # Gender hints
    text_lower = text.lower()
    if any(w in text_lower for w in ["i am a woman", "i am female", "wife", "she", "mahila"]):
        profile["gender"] = "female"
    elif any(w in text_lower for w in ["i am a man", "i am male", "husband", "he", "purush"]):
        profile["gender"] = "male"

    return profile
