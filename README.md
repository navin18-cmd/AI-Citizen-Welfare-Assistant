# AI Citizen Welfare Assistant

Production-ready hackathon backend with real OCR parsing, multilingual profile extraction, dynamic scheme matching, translation fallbacks, and persistent workflow logging.

## Project Overview

This project helps citizens discover government welfare schemes using either voice/text details or uploaded documents.

The frontend remains unchanged (Next.js 14), and the backend keeps the same API routes used by the UI:
- `POST /voice-input`
- `POST /voice-input/text`
- `POST /voice-input/audio`
- `POST /upload-document`
- `POST /schemes/check-eligibility`
- `GET /schemes`, `GET /citizens`, `GET /citizens/ngo-dashboard`, etc.

## Upgraded Architecture

### Backend Flow

1. Voice/Text input reaches `routes/voice.py`.
2. For audio, backend accepts browser formats (`webm`, `ogg`, etc.), converts audio to `WAV 16kHz mono` using FFmpeg, and transcribes via local Whisper (`base`) in `services/speech_to_text.py`.
3. `services/speech_service.py` extracts structured profile fields in English/Hindi/Tamil.
4. `services/scheme_engine.py` applies rule filtering and dynamic scoring.
5. `services/translation_service.py` translates user-visible response fields (`hi`, `ta`) with English fallback.
6. `utils/database.py` persists `voice_sessions`, recommended `applications`, and citizen records.

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
- `openai-whisper` + local FFmpeg
  - Local speech-to-text for uploaded/recorded audio via Whisper `base` model.
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
|  |  |- speech_to_text.py
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

Backup snapshot before Whisper integration:

```text
demo_backup_version/
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

# Whisper stack
pip install openai-whisper ffmpeg-python
```

Set runtime mode (`USE_DEMO_MODE`) in backend shell before starting:

```powershell
# Production-ready default (Whisper ON)
$env:USE_DEMO_MODE = "false"

# Demo fallback mode (placeholder transcription)
# $env:USE_DEMO_MODE = "true"
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

### 2b. FFmpeg Dependency for Audio Transcription (Windows)

Whisper audio preprocessing requires `ffmpeg.exe` available in PATH.

1. Install FFmpeg (Windows build).
2. Add FFmpeg `bin` folder to your PATH.
3. Verify:

```powershell
ffmpeg -version
ffprobe -version
```

### 3. Frontend Setup

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\frontend"
npm install
```

## How To Run

### Run with Windows CMD (Command Prompt)

Open two separate CMD windows.

CMD Window 1 (Backend):

```cmd
cd /d "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\backend"
set USE_DEMO_MODE=false
"c:\Users\NAVIN GS\OneDrive\project\public welfare demo\.venv\Scripts\python.exe" -m uvicorn main:app --reload
```

CMD Window 2 (Frontend):

```cmd
cd /d "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\frontend"
npm run dev
```

### Run Backend (port 8000)

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\backend"
$env:USE_DEMO_MODE = "false"
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

`POST /voice-input/audio` returns the exact same response structure as `POST /voice-input/text`.

## Demo Workflow

### Voice/Text Demo

1. Open `/voice` in frontend.
2. Speak (max 10 seconds) or type a sentence in English, Hindi, or Tamil.
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
- invalid/unsupported audio format handling (`wav/mp3/m4a/webm/ogg/...`)
- FFmpeg conversion failure handling
- transcription failure and empty transcription handling
- max audio duration enforcement (10 seconds)
- temporary file cleanup for original and converted audio (even on failures)
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
- `openai-whisper`
- `ffmpeg-python`

## Voice API (Whisper)

### Endpoint

- `POST /voice-input/audio`
  - multipart form fields:
   - `audio`: required file (`wav`, `mp3`, `m4a`, `webm`, `ogg`, etc.)
   - `language`: optional, default `en`

### Processing Steps

1. Validate file presence and supported extension.
2. Save temp original audio.
3. Convert to `WAV`, `16kHz`, `mono` using FFmpeg.
4. Validate max duration (`<= 10s`).
5. Transcribe:
  - `USE_DEMO_MODE=true`: demo placeholder flow
  - `USE_DEMO_MODE=false`: local Whisper (`base`) flow
6. Run existing text extraction + scheme matching pipeline.
7. Delete all temp files and temp directory in `finally` cleanup.

## Rollback / Restore

To restore the pre-Whisper baseline from backup:

```powershell
cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo"
Remove-Item -Recurse -Force "ai-welfare-assistant"
Copy-Item -Recurse -Force "demo_backup_version" "ai-welfare-assistant"
```

## Validation Checklist

1. Start backend with `USE_DEMO_MODE=false`.
2. Record audio from frontend (`/voice`) and confirm transcript is populated.
3. Confirm response includes unchanged keys:
  - `transcript`
  - `extracted_profile`
  - `eligible_schemes`
  - `total_schemes`
  - `total_benefit_value`
  - `message`
  - `language`
  - `voice_session_id`
  - `citizen_id`
  - `applications_saved`
4. Confirm schemes and total benefit values are returned.
5. Confirm temp files are not left behind after success/failure.

## Test Cases (Sample)

1. Happy path audio (`webm`, 6s)
  - Input: "I am a farmer earning 8000 rupees per month in Tamil Nadu"
  - Expected: non-empty `transcript`, valid `extracted_profile`, `eligible_schemes` array.

2. Unsupported format
  - Input: upload `.txt`
  - Expected: `400` with unsupported audio format message.

3. Empty file
  - Input: zero-byte audio
  - Expected: `400` with empty audio file message.

4. Audio too long
  - Input: 15s recording
  - Expected: `400` with duration limit message.

5. FFmpeg missing
  - Input: valid audio, FFmpeg not in PATH
  - Expected: `500` conversion failure.

6. Demo mode fallback
  - Set `USE_DEMO_MODE=true`
  - Expected: API still returns valid response structure with placeholder transcript.

## Common Errors + Fixes

1. `Audio conversion failed`
  - Cause: FFmpeg/ffprobe missing from PATH.
  - Fix: Install FFmpeg and verify `ffmpeg -version`.

2. `Unsupported audio format`
  - Cause: Extension not allowed.
  - Fix: Use `wav`, `mp3`, `m4a`, `webm`, or `ogg`.

3. `Audio too long. Max 10 seconds allowed`
  - Cause: Recording exceeds limit.
  - Fix: Record shorter clip (5-10s recommended).

4. `Transcription failed`
  - Cause: Whisper runtime/model issue.
  - Fix: Reinstall `openai-whisper`, confirm Python env and dependencies are intact.

## Notes

- The frontend still contains local demo fallback constants for offline UX safety.
- Local Whisper (`base`) transcription is integrated for audio routes when `USE_DEMO_MODE=false`.
- Text-based multilingual extraction and scheme matching are fully functional.
