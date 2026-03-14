"""
Document upload route - handles Aadhaar / income certificate OCR.
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os, shutil, uuid

from services.ocr_service import extract_text_from_image, is_valid_aadhaar_text, parse_aadhaar_data
from services.scheme_engine import get_eligible_schemes
from services.translation_service import translate, translate_scheme_fields
from utils.database import get_or_create_citizen, save_applications, save_document_upload

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
LOGGER = logging.getLogger(__name__)
_ALLOWED_DOC_TYPES = {"aadhaar", "income_certificate"}
_ALLOWED_CONTENT_TYPES = {
    "image/png", "image/jpeg", "image/jpg", "application/pdf"
}
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("aadhaar"),
    language: str = Form("en")
):
    """
    Accept an image upload, run mock OCR, extract citizen info.
    """
    if document_type not in _ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail=translate("validation_error", language))
    file_ext = os.path.splitext(file.filename or "")[-1].lower()
    if file_ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Aadhaar image or PDF.")
    if file.content_type and file.content_type.lower() not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Aadhaar image or PDF.")

    # Save file
    ext = file_ext or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

        extracted_text = extract_text_from_image(filepath, document_type)
        is_valid_aadhaar = is_valid_aadhaar_text(extracted_text)
        if not is_valid_aadhaar:
            return {
                "filename": filename,
                "document_type": document_type,
                "verification_status": "Invalid Document",
                "message": "Invalid document. Please upload a valid Aadhaar card.",
                "eligible_schemes": [],
                "total_schemes": 0,
                "total_benefit_value": 0,
            }

        parsed_data = parse_aadhaar_data(extracted_text)
        eligible = get_eligible_schemes(parsed_data)

        if document_type == "aadhaar":
            eligible = eligible[:1]

        translated_eligible = [translate_scheme_fields(s, language) for s in eligible]
        total_benefit = sum(s.get("benefit_value", 0) for s in translated_eligible)

        citizen_id = get_or_create_citizen(parsed_data)
        document_upload_id = save_document_upload(citizen_id, document_type, filepath, extracted_text, parsed_data)
        applications_saved = save_applications(citizen_id, eligible)

        return {
            "filename": filename,
            "document_type": document_type,
            "verification_status": "Aadhaar Verified",
            "name": parsed_data.get("name"),
            "dob": parsed_data.get("dob"),
            "state": parsed_data.get("state"),
            "address": parsed_data.get("address"),
            "extracted_text": extracted_text,
            "parsed_data": parsed_data,
            "eligible_schemes": translated_eligible,
            "total_schemes": len(translated_eligible),
            "total_benefit_value": total_benefit,
            "message": translate("document_processed", language, n=len(translated_eligible)),
            "document_upload_id": document_upload_id,
            "citizen_id": citizen_id,
            "applications_saved": applications_saved,
        }
    except ValueError as exc:
        LOGGER.warning("Document validation/OCR parsing failed: %s", exc)
        detail = str(exc)
        if "Unsupported file format" in detail:
            detail = "Unsupported file format. Please upload Aadhaar image or PDF."
        raise HTTPException(status_code=400, detail=detail) from exc
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception("Document upload processing failed")
        raise HTTPException(status_code=500, detail=translate("ocr_error", language)) from exc
