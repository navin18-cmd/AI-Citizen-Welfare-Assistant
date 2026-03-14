"""
Voice input route - accepts audio or text, returns extracted citizen info + eligible schemes.
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from services.speech_service import transcribe_audio, extract_info_from_text
from services.scheme_engine import get_eligible_schemes
from services.translation_service import translate, translate_scheme_fields
from utils.database import get_or_create_citizen, save_applications, save_voice_session

router = APIRouter()
LOGGER = logging.getLogger(__name__)


def _translate_schemes(schemes: list, language: str) -> list:
    return [translate_scheme_fields(s, language) for s in schemes]


@router.post("")
async def voice_input(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: str = Form("en")
):
    """
    Accept voice audio OR plain text.
    Returns transcript + extracted profile + eligible schemes.
    """
    transcript = (text or "").strip()

    if not audio and not transcript:
        raise HTTPException(status_code=400, detail=translate("validation_error", language))

    try:
        if audio and not transcript:
            audio_bytes = await audio.read()
            transcript = transcribe_audio(audio_bytes, language)

        profile = extract_info_from_text(transcript, language_hint=language)
        eligible = get_eligible_schemes(profile)
        translated_eligible = _translate_schemes(eligible, language)
        total_benefit = sum(s.get("benefit_value", 0) for s in translated_eligible)

        citizen_id = get_or_create_citizen(profile)
        voice_session_id = save_voice_session(citizen_id, transcript, profile, language)
        applications_saved = save_applications(citizen_id, eligible)

        message = translate(
            "you_qualify",
            language,
            n=len(translated_eligible),
        )
        message = f"{message} worth ₹{total_benefit:,.0f}"

        return {
            "transcript": transcript,
            "extracted_profile": profile,
            "eligible_schemes": translated_eligible,
            "total_schemes": len(translated_eligible),
            "total_benefit_value": total_benefit,
            "message": message,
            "language": language,
            "voice_session_id": voice_session_id,
            "citizen_id": citizen_id,
            "applications_saved": applications_saved,
        }
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Voice input processing failed")
        raise HTTPException(status_code=500, detail=translate("voice_error", language)) from exc


@router.post("/text")
async def text_input(payload: dict):
    """Direct text input endpoint."""
    text = (payload.get("text") or "").strip()
    language = payload.get("language", "en")

    if not text:
        raise HTTPException(status_code=400, detail=translate("validation_error", language))

    try:
        profile = extract_info_from_text(text, language_hint=language)
        eligible = get_eligible_schemes(profile)
        translated_eligible = _translate_schemes(eligible, language)
        total_benefit = sum(s.get("benefit_value", 0) for s in translated_eligible)

        citizen_id = get_or_create_citizen(profile)
        voice_session_id = save_voice_session(citizen_id, text, profile, language)
        applications_saved = save_applications(citizen_id, eligible)

        message = translate("you_qualify", language, n=len(translated_eligible))
        message = f"{message} worth ₹{total_benefit:,.0f}"

        return {
            "transcript": text,
            "extracted_profile": profile,
            "eligible_schemes": translated_eligible,
            "total_schemes": len(translated_eligible),
            "total_benefit_value": total_benefit,
            "message": message,
            "language": language,
            "voice_session_id": voice_session_id,
            "citizen_id": citizen_id,
            "applications_saved": applications_saved,
        }
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Text voice endpoint processing failed")
        raise HTTPException(status_code=500, detail=translate("voice_error", language)) from exc
