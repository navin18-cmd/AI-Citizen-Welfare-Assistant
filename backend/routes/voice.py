"""
Voice input route - accepts audio or text, returns extracted citizen info + eligible schemes.
"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import json

from services.speech_service import transcribe_audio, extract_info_from_text
from services.scheme_engine import get_eligible_schemes

router = APIRouter()


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
    transcript = text or ""

    if audio and not text:
        audio_bytes = await audio.read()
        transcript = transcribe_audio(audio_bytes, language)

    # Extract citizen profile from text
    profile = extract_info_from_text(transcript)

    # Run eligibility engine
    eligible = get_eligible_schemes(profile)

    total_benefit = sum(s["benefit_value"] for s in eligible)

    return {
        "transcript": transcript,
        "extracted_profile": profile,
        "eligible_schemes": eligible,
        "total_schemes": len(eligible),
        "total_benefit_value": total_benefit,
        "message": f"You qualify for {len(eligible)} government welfare schemes worth ₹{total_benefit:,.0f}",
        "language": language
    }


@router.post("/text")
async def text_input(payload: dict):
    """Direct text input endpoint."""
    text = payload.get("text", "")
    language = payload.get("language", "en")

    profile = extract_info_from_text(text)
    eligible = get_eligible_schemes(profile)
    total_benefit = sum(s["benefit_value"] for s in eligible)

    return {
        "transcript": text,
        "extracted_profile": profile,
        "eligible_schemes": eligible,
        "total_schemes": len(eligible),
        "total_benefit_value": total_benefit,
        "message": f"You qualify for {len(eligible)} government welfare schemes worth ₹{total_benefit:,.0f}",
        "language": language
    }
