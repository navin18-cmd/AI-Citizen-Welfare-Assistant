"""Local Whisper speech-to-text service with global model reuse."""

import logging
import threading
from typing import Optional

import whisper

LOGGER = logging.getLogger(__name__)
_MODEL_NAME = "base"
_MODEL_LOCK = threading.Lock()
_WHISPER_MODEL: Optional[whisper.Whisper] = None


def _get_model() -> whisper.Whisper:
    """Load Whisper model once globally and reuse for all requests."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        with _MODEL_LOCK:
            if _WHISPER_MODEL is None:
                LOGGER.info("Loading Whisper model: %s", _MODEL_NAME)
                _WHISPER_MODEL = whisper.load_model(_MODEL_NAME)
                LOGGER.info("Whisper model loaded")
    return _WHISPER_MODEL


def transcribe_audio(file_path: str) -> str:
    """Transcribe a prepared WAV 16k mono audio file with local Whisper."""
    model = _get_model()
    try:
        LOGGER.info(f"Starting Whisper transcription on file: {file_path}")
        result = model.transcribe(
            file_path,
            task="transcribe",
            fp16=False,
            verbose=False,
        )
        LOGGER.info(f"Whisper transcription complete. Raw result keys: {result.keys()}")
    except Exception as exc:
        LOGGER.exception("Whisper transcription failed")
        raise RuntimeError("Transcription failed") from exc

    text = (result.get("text") or "").strip()
    LOGGER.info(f"Extracted text (length={len(text)}): {text[:100] if text else '[EMPTY]'}")
    if not text:
        LOGGER.warning("Whisper returned empty transcription - audio may be silent or contain only noise")
        raise ValueError("No speech detected. Please speak clearly and loudly, or check your microphone.")
    return text
