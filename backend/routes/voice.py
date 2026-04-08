"""
Voice input route - accepts audio or text, returns extracted citizen info + eligible schemes.
"""
import asyncio
import logging
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import ffmpeg
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from services.speech_service import transcribe_audio as demo_transcribe_audio, extract_info_from_text, USE_DEMO_MODE
from services.speech_to_text import transcribe_audio as whisper_transcribe_audio
from services.scheme_engine import get_eligible_schemes
from services.translation_service import translate, translate_scheme_fields
from utils.database import get_or_create_citizen, save_applications, save_voice_session

router = APIRouter()
LOGGER = logging.getLogger(__name__)
SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".webm", ".ogg", ".oga", ".mp4", ".mpeg", ".mpga"
}
MAX_AUDIO_DURATION_SECONDS = 10.0


def _translate_schemes(schemes: list, language: str) -> list:
    return [translate_scheme_fields(s, language) for s in schemes]


def _process_transcript(transcript: str, language: str) -> dict:
    profile = extract_info_from_text(transcript, language_hint=language)
    eligible = get_eligible_schemes(profile)
    translated_eligible = _translate_schemes(eligible, language)
    total_benefit = sum(s.get("benefit_value", 0) for s in translated_eligible)

    citizen_id = get_or_create_citizen(profile)
    voice_session_id = save_voice_session(citizen_id, transcript, profile, language)
    applications_saved = save_applications(citizen_id, eligible)

    message = translate("you_qualify", language, n=len(translated_eligible))
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


def _convert_to_wav_16k_mono(input_path: str, output_path: str) -> None:
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format="wav", ac=1, ar=16000)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as exc:
        error_text = exc.stderr.decode("utf-8", errors="ignore") if exc.stderr else str(exc)
        LOGGER.error("FFmpeg conversion failed: %s", error_text)
        raise RuntimeError("Audio conversion failed") from exc


def _probe_audio_duration_seconds(file_path: str) -> float:
    try:
        probe_data = ffmpeg.probe(file_path)
    except ffmpeg.Error as exc:
        LOGGER.error("FFmpeg probe failed for duration")
        raise RuntimeError("Unable to inspect audio duration") from exc

    duration_text = (probe_data.get("format") or {}).get("duration")
    if duration_text is None:
        raise RuntimeError("Unable to inspect audio duration")
    try:
        return float(duration_text)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Unable to inspect audio duration") from exc


async def _transcribe_upload(audio: UploadFile, language: str) -> str:
    if not audio:
        raise HTTPException(status_code=400, detail="Missing audio file")

    file_name = audio.filename or ""
    extension = Path(file_name).suffix.lower()
    if extension not in SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported audio format. Use wav, mp3, m4a, webm, or ogg")

    payload = await audio.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Empty audio file")

    LOGGER.info(f"Audio received: {file_name}, size={len(payload)} bytes, language={language}")

    tmp_dir = tempfile.mkdtemp(prefix="voice_audio_")
    original_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}{extension}")
    wav_path = os.path.join(tmp_dir, f"{uuid.uuid4().hex}.wav")

    try:
        with open(original_path, "wb") as f:
            f.write(payload)

        LOGGER.info(f"Converting audio from {extension} to WAV 16kHz mono...")
        await asyncio.to_thread(_convert_to_wav_16k_mono, original_path, wav_path)
        LOGGER.info(f"Audio conversion complete. WAV file: {os.path.getsize(wav_path)} bytes")
        
        duration = await asyncio.to_thread(_probe_audio_duration_seconds, wav_path)
        LOGGER.info(f"Audio duration: {duration:.2f} seconds")
        if duration > MAX_AUDIO_DURATION_SECONDS:
            raise HTTPException(
                status_code=400,
                detail=f"Audio too long. Max {int(MAX_AUDIO_DURATION_SECONDS)} seconds allowed",
            )

        if USE_DEMO_MODE:
            return demo_transcribe_audio(payload, language)
        return await asyncio.to_thread(whisper_transcribe_audio, wav_path)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Audio transcription flow failed")
        raise HTTPException(status_code=500, detail="Audio transcription failed") from exc
    finally:
        for path in [original_path, wav_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                LOGGER.warning("Failed to delete temporary file: %s", path)
        try:
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            LOGGER.warning("Failed to delete temporary directory: %s", tmp_dir)


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
            transcript = await _transcribe_upload(audio, language)

        return _process_transcript(transcript, language)
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Voice input processing failed")
        raise HTTPException(status_code=500, detail=translate("voice_error", language)) from exc


@router.post("/audio")
async def audio_input(
    audio: UploadFile = File(...),
    language: str = Form("en"),
):
    """Dedicated audio endpoint with format conversion and Whisper transcription."""
    try:
        transcript = await _transcribe_upload(audio, language)
        return _process_transcript(transcript, language)
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Audio endpoint processing failed")
        raise HTTPException(status_code=500, detail=translate("voice_error", language)) from exc


@router.post("/text")
async def text_input(payload: dict):
    """Direct text input endpoint."""
    text = (payload.get("text") or "").strip()
    language = payload.get("language", "en")

    if not text:
        raise HTTPException(status_code=400, detail=translate("validation_error", language))

    try:
        return _process_transcript(text, language)
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Text voice endpoint processing failed")
        raise HTTPException(status_code=500, detail=translate("voice_error", language)) from exc
