"""OCR service for Aadhaar validation from images and PDFs."""

import datetime as dt
import logging
import os
import re
from typing import Dict, Optional

from PIL import Image, UnidentifiedImageError
from utils.helpers import parse_state_from_text

try:
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
except ImportError:  # pragma: no cover - dependency/runtime specific
    convert_from_path = None
    PDFInfoNotInstalledError = PDFPageCountError = PDFSyntaxError = Exception

try:
    import pytesseract
except ImportError:  # pragma: no cover - dependency/runtime specific
    pytesseract = None

LOGGER = logging.getLogger(__name__)
_SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".pdf"}
_AADHAAR_REGEX_PATTERNS = [
    r"\baadhaar\b",
    r"\buidai\b",
    r"government\s*of\s*india",
    r"unique\s*identification\s*authority(?:\s*of\s*india)?",
]


def _configure_tesseract_path() -> None:
    """Set pytesseract binary path from common install locations if needed."""
    if pytesseract is None:
        return

    candidate_paths = [
        os.environ.get("TESSERACT_CMD"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Tesseract-OCR", "tesseract.exe"),
    ]

    for path in candidate_paths:
        if path and os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return


_configure_tesseract_path()


def _get_poppler_path() -> Optional[str]:
    """Resolve Poppler bin path for pdf2image if PATH is not configured."""
    env_path = os.environ.get("POPPLER_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    candidates = [
        r"C:\poppler\Library\bin",
        r"C:\Program Files\poppler\Library\bin",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "poppler", "Library", "bin"),
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Microsoft",
            "WinGet",
            "Packages",
            "oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe",
            "poppler-25.07.0",
            "Library",
            "bin",
        ),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def _normalize_ocr_text(text: str) -> str:
    cleaned = text.replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n+", "\n", cleaned)
    return cleaned.strip()


def _extract_name(text: str) -> Optional[str]:
    patterns = [
        r"(?:Name|नाम|பெயர்)\s*[:\-]?\s*([A-Za-z ]{3,60})",
        r"(?:To\s+)?([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\n(?:DOB|Year of Birth|जन्म)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip().title()
    return None


def _extract_dob(text: str) -> Optional[str]:
    patterns = [
        r"(?:DOB|Date of Birth|जन्म तिथि|பிறந்த தேதி)\s*[:\-]?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_address(text: str) -> Optional[str]:
    patterns = [
        r"(?:Address|पता|முகவரி)\s*[:\-]?\s*(.{10,250})",
        r"\b(?:S/O|D/O|W/O).{0,120}\n(.{10,250})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).split("\n")[0].strip(" ,")
            if value:
                return value
    return None


def _extract_age_from_dob(dob: Optional[str]) -> Optional[int]:
    if not dob:
        return None
    try:
        birth = dt.datetime.strptime(dob.replace("-", "/"), "%d/%m/%Y").date()
    except ValueError:
        return None
    today = dt.date.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def _ocr_from_pil_image(image: Image.Image, filepath: str) -> str:
    gray = image.convert("L")
    try:
        raw_text = pytesseract.image_to_string(gray, lang="eng")
    except Exception as exc:  # pragma: no cover - runtime specific
        LOGGER.exception("Unexpected OCR failure for %s", filepath)
        raise RuntimeError("Failed to process image with OCR") from exc
    return _normalize_ocr_text(raw_text)


def extract_text_from_image(filepath: str, document_type: str = "aadhaar") -> str:
    """Extract text from image/PDF using pytesseract and pdf2image."""
    if not os.path.exists(filepath):
        raise ValueError("Uploaded file does not exist")

    ext = os.path.splitext(filepath)[1].lower()
    if ext and ext not in _SUPPORTED_EXTS:
        raise ValueError("Unsupported file format. Please upload Aadhaar image or PDF.")

    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed in this environment")

    if ext == ".pdf":
        if convert_from_path is None:
            raise RuntimeError("pdf2image is not installed in this environment")
        try:
            pages = convert_from_path(filepath, first_page=1, last_page=1, poppler_path=_get_poppler_path())
        except PDFInfoNotInstalledError as exc:
            LOGGER.exception("Poppler is missing for PDF OCR")
            raise ValueError("PDF processing dependency missing. Install Poppler and retry") from exc
        except (PDFPageCountError, PDFSyntaxError, ValueError) as exc:
            LOGGER.warning("Unreadable PDF: %s", filepath)
            raise ValueError("Unreadable PDF. Please upload a valid Aadhaar PDF") from exc
        except Exception as exc:  # pragma: no cover - runtime specific
            LOGGER.exception("Unexpected PDF conversion failure for %s", filepath)
            raise RuntimeError("Failed to process PDF document") from exc

        if not pages:
            raise ValueError("Unreadable PDF. Please upload a valid Aadhaar PDF")
        text = _ocr_from_pil_image(pages[0], filepath)
    else:
        try:
            with Image.open(filepath) as image:
                text = _ocr_from_pil_image(image, filepath)
        except UnidentifiedImageError as exc:
            LOGGER.warning("OCR failed due to unreadable image: %s", filepath)
            raise ValueError("Unreadable image. Please upload a clear Aadhaar image") from exc

    if len(text) < 10:
        raise ValueError("Empty OCR result. Please upload a clearer Aadhaar image or PDF")

    LOGGER.info("OCR extracted %s chars for %s", len(text), document_type)
    return text


def is_valid_aadhaar_text(text: str) -> bool:
    """Check OCR text for Aadhaar identity keywords."""
    lowered = (text or "").lower()
    compact = re.sub(r"\s+", "", lowered)
    for pattern in _AADHAAR_REGEX_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return True

    # OCR frequently drops spaces, e.g. "governmentofindia".
    if "governmentofindia" in compact or "uniqueidentificationauthority" in compact:
        return True

    return False


def parse_aadhaar_data(text: str) -> Dict[str, object]:
    """Parse OCR text into a structured citizen profile."""
    if not text or len(text.strip()) < 10:
        raise ValueError("No OCR text available for parsing")

    info: Dict[str, object] = {
        "source": "document",
        "name": _extract_name(text),
        "dob": _extract_dob(text),
        "address": _extract_address(text),
        "state": parse_state_from_text(text),
        "gender": None,
    }

    text_lower = text.lower()
    if "female" in text_lower or "महिला" in text or "பெண்" in text:
        info["gender"] = "female"
    elif "male" in text_lower or "पुरुष" in text or "ஆண்" in text:
        info["gender"] = "male"

    age = _extract_age_from_dob(info.get("dob") if isinstance(info.get("dob"), str) else None)
    if age is not None:
        info["age"] = age

    # Support income certificate parsing as a secondary doc type.
    income_match = re.search(r"(?:Annual Income|Income)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([0-9,]+)", text, re.IGNORECASE)
    if income_match:
        annual_income = int(income_match.group(1).replace(",", ""))
        info["annual_income"] = annual_income
        info["income"] = int(annual_income / 12)

    missing_core = [field for field in ["name", "dob", "state"] if not info.get(field)]
    if len(missing_core) >= 2:
        LOGGER.warning("Low-confidence Aadhaar parsing. Missing fields: %s", ", ".join(missing_core))

    return info
