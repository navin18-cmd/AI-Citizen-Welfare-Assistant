"""Translation service with deep-translator and English fallbacks."""

import logging
from typing import Dict

try:
    from deep_translator import GoogleTranslator
except ImportError:  # pragma: no cover - dependency/runtime specific
    GoogleTranslator = None

LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"en": "en", "hi": "hi", "ta": "ta"}
_STATIC_STRINGS = {
    "you_qualify": "You qualify for {n} government welfare schemes",
    "document_processed": "Document processed. You qualify for {n} scheme(s)",
    "validation_error": "Invalid input. Please check the request and try again",
    "ocr_error": "Could not read the uploaded document. Please upload a clearer image",
    "voice_error": "Could not process voice input. Please retry with clearer details",
}


def translate_text(text: str, language: str = "en") -> str:
    """Translate plain text to target language with English fallback."""
    if not text:
        return text

    target = SUPPORTED_LANGUAGES.get(language, "en")
    if target == "en":
        return text

    if GoogleTranslator is None:
        LOGGER.warning("deep-translator not installed; fallback to English text")
        return text

    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception as exc:  # pragma: no cover - network/runtime specific
        LOGGER.warning("Translation failed (%s). Falling back to English", exc)
        return text


def translate(key: str, language: str = "en", **kwargs) -> str:
    """Translate a known UI/system key with fallback to dynamic translation."""
    template = _STATIC_STRINGS.get(key, key)
    try:
        formatted = template.format(**kwargs)
    except KeyError:
        formatted = template
    return translate_text(formatted, language)


def get_scheme_name(scheme: Dict[str, object], language: str) -> str:
    """Return translated scheme name with cached manual names where available."""
    if language == "hi" and scheme.get("hindi_name"):
        return str(scheme["hindi_name"])
    if language == "ta" and scheme.get("tamil_name"):
        return str(scheme["tamil_name"])
    return translate_text(str(scheme.get("name", "")), language)


def translate_scheme_fields(scheme: Dict[str, object], language: str) -> Dict[str, object]:
    """Translate user-visible fields of a scheme payload."""
    if language == "en":
        return scheme

    translated = dict(scheme)
    translated["name"] = get_scheme_name(scheme, language)
    translated["scheme_name"] = translated["name"]
    translated["description"] = translate_text(str(scheme.get("description", "")), language)
    translated["benefit_description"] = translate_text(str(scheme.get("benefit_description", "")), language)
    translated["benefit_summary"] = translate_text(str(scheme.get("benefit_summary", "")), language)
    translated["reason"] = translate_text(str(scheme.get("reason", "")), language)

    required_documents = scheme.get("required_documents") or []
    if isinstance(required_documents, list):
        translated["required_documents"] = [translate_text(str(doc), language) for doc in required_documents]

    return translated


def get_all_translations(language: str = "en") -> dict:
    """Return translated static system strings for the target language."""
    return {key: translate(key, language) for key in _STATIC_STRINGS}
