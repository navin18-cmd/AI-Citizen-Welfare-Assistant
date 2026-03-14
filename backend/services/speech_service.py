"""Speech service with multilingual NLP parsing for EN/HI/TA text inputs."""

import logging
import re
from typing import Dict, Optional

from utils.helpers import parse_age_from_text, parse_state_from_text

LOGGER = logging.getLogger(__name__)

_OCCUPATION_KEYWORDS = {
    "farmer": [
        "farmer", "farming", "agriculture", "kisan", "kisaan", "krishi",
        "விவசாயி", "விவசாயம்",
    ],
    "construction worker": [
        "construction", "mason", "building worker", "majdoor", "mazdoor",
        "கட்டுமான", "கூலி",
    ],
    "domestic worker": [
        "domestic", "house maid", "house help", "ghar kaam", "ghar ka kaam",
        "வீட்டு வேலை", "வீட்டு வேலைக்காரி",
    ],
    "daily wage worker": [
        "daily wage", "daily worker", "labour", "labor", "rojgar",
        "தினக்கூலி",
    ],
    "auto driver": [
        "auto driver", "rickshaw", "taxi driver", "cab driver",
        "ஆட்டோ", "டிரைவர்",
    ],
}


def _detect_language(text: str) -> str:
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "ta"
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    lowered = text.lower()
    if any(k in lowered for k in ["mera", "meri", "main", "rupaye", "mazdoor", "kisan"]):
        return "hi"
    if any(k in lowered for k in ["naan", "varumanam", "rupai", "vivasayi"]):
        return "ta"
    return "en"


def _extract_income(text: str, detected_language: str) -> Optional[int]:
    # Numeric amounts with currency and monthly hints.
    patterns = [
        r"(?:rs\.?|rupees?|₹)\s*([0-9,]+)",
        r"([0-9,]+)\s*(?:rs\.?|rupees?|₹|rupaye|रुपये|ரூபாய்)",
        r"(?:income|salary|earning|earn)\s*(?:is|of)?\s*([0-9,]+)",
        r"(?:मासिक आय|आय|सैलरी)\s*(?:है|के करीब)?\s*([0-9,]+)",
        r"(?:மாதம்|மாத வருமானம்|வருமானம்)\s*([0-9,]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                amount = int(match.group(1).replace(",", ""))
                return amount
            except ValueError:
                continue

    # Language-aware fallback: plain numbers near monthly terms.
    monthly_tokens = {
        "en": ["month", "monthly"],
        "hi": ["माह", "महीना", "मासिक"],
        "ta": ["மாதம்", "மாத"],
    }
    near_words = monthly_tokens.get(detected_language, monthly_tokens["en"])
    for token in near_words:
        match = re.search(rf"{token}.{{0,10}}([0-9,]+)", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def _extract_occupation(text: str) -> Optional[str]:
    lowered = text.lower()
    for occupation, keywords in _OCCUPATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in lowered:
                return occupation

    # Regex fallback for simple English sentence forms.
    explicit_match = re.search(
        r"(?:i am|i work as|my occupation is)\s+(?:a\s+|an\s+)?([a-z ]{3,40})",
        lowered,
    )
    if explicit_match:
        value = explicit_match.group(1).strip()
        return value if value else None
    return None


def transcribe_audio(audio_bytes: bytes, language: str = "en") -> str:
    """
    Audio transcription placeholder.
    The API stays compatible while NLP extraction is now fully functional for text input.
    """
    if not audio_bytes:
        raise ValueError("Empty audio payload")

    LOGGER.warning(
        "Audio transcription model is not configured. Returning placeholder transcript for language=%s",
        language,
    )
    return "Audio received. Please use text input for accurate multilingual extraction in this demo."


def extract_info_from_text(text: str, language_hint: Optional[str] = None) -> Dict[str, object]:
    """Extract occupation, monthly income, language and profile hints from text."""
    text = (text or "").strip()
    detected_language = language_hint or _detect_language(text)

    if not text:
        LOGGER.warning("Voice parser received empty text")
        return {
            "source": "voice",
            "raw_text": "",
            "language": detected_language,
            "occupation": None,
            "income": None,
            "name": None,
            "age": None,
            "state": None,
            "gender": None,
            "bpl_card": False,
            "has_land": False,
        }

    profile: Dict[str, object] = {
        "source": "voice",
        "raw_text": text,
        "language": detected_language,
        "name": None,
        "age": parse_age_from_text(text),
        "occupation": _extract_occupation(text),
        "income": _extract_income(text, detected_language),
        "state": parse_state_from_text(text),
        "gender": None,
        "bpl_card": bool(re.search(r"\b(bpl|ration|गरीब|ரேஷன்)\b", text.lower())),
        "has_land": bool(re.search(r"\b(land|acre|bigha|जमीन|நிலம்|ஏக்கர்)\b", text.lower())),
    }

    name_match = re.search(
        r"(?:my name is|i am|मैं|मेरा नाम|நான்|என் பெயர்)\s+([A-Za-z\u0900-\u097F\u0B80-\u0BFF ]{2,50})",
        text,
        flags=re.IGNORECASE,
    )
    if name_match:
        profile["name"] = re.sub(r"\s+", " ", name_match.group(1)).strip().title()

    lowered = text.lower()
    if any(w in lowered for w in ["female", "woman", "mahila", "महिला", "பெண்"]):
        profile["gender"] = "female"
    elif any(w in lowered for w in ["male", "man", "purush", "पुरुष", "ஆண்"]):
        profile["gender"] = "male"

    if profile.get("income") is not None:
        profile["annual_income"] = int(profile["income"]) * 12

    missing = [key for key in ["occupation", "income", "state"] if not profile.get(key)]
    if missing:
        LOGGER.info("Partial voice extraction. Missing fields: %s", ", ".join(missing))

    return profile
