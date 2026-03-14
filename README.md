# AI Citizen Welfare Assistant

Production-ready hackathon backend with real OCR parsing, multilingual profile extraction, dynamic scheme matching, translation fallbacks, and persistent workflow logging.

## Project Overview

This project helps citizens discover government welfare schemes using either voice/text details or uploaded documents.

The frontend remains unchanged (Next.js 14), and the backend keeps the same API routes used by the UI:
- `POST /voice-input`
- `POST /voice-input/text`
- `POST /upload-document`
- `POST /schemes/check-eligibility`
- `GET /schemes`, `GET /citizens`, `GET /citizens/ngo-dashboard`, etc.

## Upgraded Architecture

### Backend Flow

1. Voice/Text input reaches `routes/voice.py`.
2. `services/speech_service.py` extracts structured profile fields in English/Hindi/Tamil.
3. `services/scheme_engine.py` applies rule filtering and dynamic scoring.
4. `services/translation_service.py` translates user-visible response fields (`hi`, `ta`) with English fallback.
5. `utils/database.py` persists `voice_sessions`, recommended `applications`, and citizen records.

### Document Flow

1. Upload reaches `routes/documents.py`.
2. `services/ocr_service.py` reads OCR text from image or first PDF page.
3. Aadhaar keyword validation is applied before eligibility matching.
4. Aadhaar parser extracts `name`, `dob`, `address`, `state`.
5. Matched schemes are returned and persisted in `document_uploads` + `applications`.

### Supported Document Types

- `.jpg`
- `.jpeg`
- `.png`
- `.pdf`

Any other format is rejected with:
- `Unsupported file format. Please upload Aadhaar image or PDF.`

## AI / NLP Modules Used

- `pytesseract` + `Pillow` + `pdf2image`
  - OCR extraction from Aadhaar images and first page of Aadhaar PDFs.
- Regex + keyword dictionaries
  - Multilingual occupation/income/language extraction from natural text.
- `deep-translator` (`GoogleTranslator`)
  - Runtime translation for scheme names, descriptions, reasons, and response messages.
- Rule-based scheme engine
  - Step 1: strict rule filtering (`income`, `occupation`, `state`, `age`, `gender`).
  - Step 2: dynamic eligibility scoring in range `60-95`.
  - Step 3: human-readable eligibility reason + benefit summary.

## Project Structure

```text
ai-welfare-assistant/
|- backend/
|  |- main.py
|  |- requirements.txt
|  |- routes/
|  |  |- voice.py
|  |  |- documents.py
|  |  |- schemes.py
|  |  |- citizens.py
|  |- services/
|  |  |- speech_service.py
|  |  |- ocr_service.py
|  |  |- scheme_engine.py
|  |  |- translation_service.py
|  |- utils/
|  |  |- database.py
|  |  |- helpers.py
|- frontend/
|  |- src/
|     |- app/
|     |- components/
|     |- services/api.ts
|- datasets/
|  |- schemes.json
|  |- citizens_demo.json
|- database/
|  |- schema.sql
```

## Database Usage

All schema tables are now actively used:

- `citizens`
  - Stores citizen records from voice/document extraction.
- `voice_sessions`
  - Stores transcript, extracted profile JSON, language, and citizen link.
- `document_uploads`
  - Stores file metadata, OCR text, parsed data, and citizen link.
- `applications`
  - Stores generated scheme recommendations per citizen with score and notes.
- `schemes`
  - Seeded from `datasets/schemes.json`.

## Installation

### 1. Backend Setup

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\backend"

# if needed, activate your venv first
# .\\..\\.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

# direct install for OCR stack (equivalent)
pip install pytesseract pdf2image pillow
```

### 2. OCR Dependencies (Windows)

`pytesseract` requires the Tesseract executable installed on your system.

1. Install Tesseract OCR (Windows installer).
2. Ensure `tesseract.exe` is available in `PATH`.
3. Verify:

```powershell
tesseract --version
```

If it is not in PATH, set `pytesseract.pytesseract.tesseract_cmd` in `ocr_service.py` to the local executable path.

`pdf2image` requires Poppler for PDF conversion.

Install Poppler and set one of the following:
1. Add Poppler `bin` folder to `PATH`.
2. Or set environment variable `POPPLER_PATH` to Poppler `bin` directory.

Example (PowerShell):

```powershell
$env:POPPLER_PATH = "C:\poppler\Library\bin"
```

### 3. Frontend Setup

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\frontend"
npm install
```

## How To Run

### Run Backend (port 8000)

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\backend"
& "C:\Users\NAVIN GS\OneDrive\project\public welfare demo\.venv\Scripts\python.exe" -m uvicorn main:app --reload
```

Backend docs:
- `http://localhost:8000/docs`

### Run Frontend (port 3000)

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\frontend"
npm.cmd run dev
```

Frontend:
- `http://localhost:3000`

## API Compatibility Notes

The backend upgrade preserves all existing frontend-consumed route paths and response keys such as:
- `transcript`
- `extracted_profile`
- `eligible_schemes`
- `total_schemes`
- `total_benefit_value`
- `message`

New metadata fields were added in responses (for traceability) without breaking existing keys:
- `citizen_id`
- `voice_session_id`
- `document_upload_id`
- `applications_saved`

## Demo Workflow

### Voice/Text Demo

1. Open `/voice` in frontend.
2. Speak or type a sentence in English, Hindi, or Tamil.
3. Backend extracts:
   - `occupation`
   - `income` (monthly)
   - `language`
   - optional profile hints (`state`, `age`, etc.)
4. Eligible schemes appear with:
   - `scheme_name`
   - `eligibility_score` (`60-95`)
   - `reason`
   - `required_documents`
   - `benefit_summary`

Example Tamil input:
- `நான் விவசாயி மாதம் 8000 சம்பாதிக்கிறேன்`
- Parsed as: `occupation=farmer`, `income=8000`, `language=ta`

### Document Upload Demo

1. Open `/upload` in frontend.
2. Upload a clear Aadhaar image (`.jpg/.jpeg/.png`) or Aadhaar PDF (`.pdf`).
3. OCR extracts text using:
  - direct image OCR for image files
  - `pdf2image` first-page conversion + OCR for PDF files
4. Aadhaar verification checks text for keywords such as `aadhaar`, `government of india`, `uidai`.
5. On success:
  - `verification_status` is `Aadhaar Verified`
  - extracted `name`, `dob`, `state`, `address` are returned
6. On failure:
  - `verification_status` is `Invalid Document`
  - message: `Invalid document. Please upload a valid Aadhaar card.`

## Error Handling and Validation

Implemented in upgraded backend:
- strict file type validation (`.jpg/.jpeg/.png/.pdf` only)
- unreadable image handling (`400` responses with actionable message)
- unreadable/corrupted PDF handling (`400` responses)
- empty OCR result handling
- OCR failure handling with safe response
- empty text/audio validation in voice routes
- parser fallback behavior for partial profiles
- translation fallback to English on network/API errors
- structured logging for OCR, translation, and voice failures

## Required Libraries

Backend `requirements.txt` includes:
- `fastapi`
- `uvicorn[standard]`
- `python-multipart`
- `pydantic`
- `aiofiles`
- `Pillow`
- `pytesseract`
- `pdf2image`
- `deep-translator`

## Notes

- The frontend still contains local demo fallback constants for offline UX safety.
- Audio transcription remains a placeholder message unless a full ASR model (Whisper/local STT) is integrated.
- Text-based multilingual extraction and scheme matching are fully functional.
