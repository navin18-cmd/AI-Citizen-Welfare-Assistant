"""
Translation service - mock multilingual support (English, Hindi, Tamil).
Real version would call Google Translate API or OpenAI.
"""

TRANSLATIONS = {
    "en": {
        "you_qualify": "You qualify for {n} government welfare schemes",
        "total_benefits": "Total benefits worth ₹{amount}",
        "speak_now": "Speak Now",
        "upload_doc": "Upload Document",
        "find_schemes": "Find Schemes",
        "eligible_schemes": "Eligible Schemes",
        "benefit_value": "Benefit Value",
        "apply_now": "Apply Now",
        "required_docs": "Documents Required",
    },
    "hi": {
        "you_qualify": "आप {n} सरकारी कल्याण योजनाओं के पात्र हैं",
        "total_benefits": "कुल लाभ ₹{amount} के योग्य",
        "speak_now": "अभी बोलें",
        "upload_doc": "दस्तावेज़ अपलोड करें",
        "find_schemes": "योजनाएं खोजें",
        "eligible_schemes": "पात्र योजनाएं",
        "benefit_value": "लाभ राशि",
        "apply_now": "अभी आवेदन करें",
        "required_docs": "आवश्यक दस्तावेज़",
    },
    "ta": {
        "you_qualify": "நீங்கள் {n} அரசு நலத் திட்டங்களுக்கு தகுதிபெற்றுள்ளீர்கள்",
        "total_benefits": "மொத்த நலன்கள் ₹{amount} மதிப்புள்ளவை",
        "speak_now": "இப்போது பேசுங்கள்",
        "upload_doc": "ஆவணம் பதிவேற்றவும்",
        "find_schemes": "திட்டங்களை கண்டறியவும்",
        "eligible_schemes": "தகுதி திட்டங்கள்",
        "benefit_value": "நலன் மதிப்பு",
        "apply_now": "இப்போது விண்ணப்பிக்கவும்",
        "required_docs": "தேவையான ஆவணங்கள்",
    }
}


def translate(key: str, language: str = "en", **kwargs) -> str:
    """Get translated string for a given key."""
    lang_map = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    template = lang_map.get(key, TRANSLATIONS["en"].get(key, key))
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def get_scheme_name(scheme: dict, language: str) -> str:
    """Return scheme name in requested language."""
    if language == "hi" and scheme.get("hindi_name"):
        return scheme["hindi_name"]
    if language == "ta" and scheme.get("tamil_name"):
        return scheme["tamil_name"]
    return scheme.get("name", "")


def get_all_translations(language: str = "en") -> dict:
    return TRANSLATIONS.get(language, TRANSLATIONS["en"])
