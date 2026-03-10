"""
OCR service - mock Tesseract OCR for demo.
Real version would use pytesseract.image_to_string(Image.open(path)).
"""
import os
from utils.helpers import extract_aadhaar_info

# Mock OCR output for different document types
MOCK_AADHAAR_TEXTS = {
    "default": """
Government of India
Unique Identification Authority of India

Name: Ravi Kumar
DOB: 15/08/1990
Gender: Male
Address: 12, Main Street, Chennai, Tamil Nadu - 600001

Aadhaar No: XXXX XXXX 1234
""",
    "female": """
Government of India
Unique Identification Authority of India

Name: Lakshmi Devi
DOB: 22/03/1995
Gender: Female
Address: 45, Garden Road, Bengaluru, Karnataka - 560001

Aadhaar No: XXXX XXXX 5678
""",
    "farmer": """
Government of India
Unique Identification Authority of India

Name: Ramesh Patel
DOB: 10/07/1979
Gender: Male
Address: Village Sundarpur, Guntur, Andhra Pradesh - 522001

Aadhaar No: XXXX XXXX 9012
"""
}

MOCK_INCOME_CERT = """
INCOME CERTIFICATE
Government of Tamil Nadu

This is to certify that Ravi Kumar
Son/Daughter of: Mohan Kumar
Residing at: 12 Main Street, Chennai

Annual Income: Rs. 1,20,000/-
(Rupees One Lakh Twenty Thousand Only)

Occupation: Construction Worker
Issued by: Taluk Office, Chennai
"""


def extract_text_from_image(filepath: str, document_type: str = "aadhaar") -> str:
    """
    Mock OCR extraction.
    Real implementation:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(filepath))
    """
    filename = os.path.basename(filepath).lower()

    if document_type == "income_certificate":
        return MOCK_INCOME_CERT

    # Return appropriate mock based on filename hints
    if "female" in filename or "lakshmi" in filename:
        return MOCK_AADHAAR_TEXTS["female"]
    if "farmer" in filename or "ramesh" in filename:
        return MOCK_AADHAAR_TEXTS["farmer"]

    return MOCK_AADHAAR_TEXTS["default"]


def parse_aadhaar_data(text: str) -> dict:
    """Parse extracted OCR text into structured citizen profile."""
    import re

    info = extract_aadhaar_info(text)

    # Extract age from DOB
    dob_match = re.search(r'(\d{2})[/\-](\d{2})[/\-](\d{4})', text)
    if dob_match:
        birth_year = int(dob_match.group(3))
        info["dob"] = dob_match.group(0)
        info["age"] = 2025 - birth_year

    # Extract income if income cert
    income_match = re.search(r'(?:Rs\.?|₹)\s*([0-9,]+)', text)
    if income_match:
        info["annual_income"] = int(income_match.group(1).replace(",", ""))
        info["income"] = info["annual_income"] // 12

    info["source"] = "document"
    return info
