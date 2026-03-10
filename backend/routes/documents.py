"""
Document upload route - handles Aadhaar / income certificate OCR.
"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
import os, shutil, uuid

from services.ocr_service import extract_text_from_image, parse_aadhaar_data
from services.scheme_engine import get_eligible_schemes

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("aadhaar"),
    language: str = Form("en")
):
    """
    Accept an image upload, run mock OCR, extract citizen info.
    """
    # Save file
    ext = os.path.splitext(file.filename)[-1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run OCR (mock for demo)
    extracted_text = extract_text_from_image(filepath, document_type)
    parsed_data = parse_aadhaar_data(extracted_text)

    # Run eligibility with extracted data
    eligible = get_eligible_schemes(parsed_data)

    # Aadhaar only confirms identity — limit to top 1 best-match scheme
    if document_type == "aadhaar":
        eligible = eligible[:1]

    total_benefit = sum(s["benefit_value"] for s in eligible)

    return {
        "filename": filename,
        "document_type": document_type,
        "extracted_text": extracted_text,
        "parsed_data": parsed_data,
        "eligible_schemes": eligible,
        "total_schemes": len(eligible),
        "total_benefit_value": total_benefit,
        "message": f"Document processed. You qualify for {len(eligible)} scheme."
    }
