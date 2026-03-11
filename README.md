# AI Citizen Welfare Assistant

> Hackathon demo — FastAPI backend + Next.js 14 frontend + SQLite database.  
> Fully offline-capable: every frontend page has `DEMO_*` fallback constants.

---

## Quick Start

```bash
# Backend (port 8000)
cd backend
pip install -r requirements.txt
python main.py

# Frontend (port 3000)
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
ai-welfare-assistant/
├── backend/
│   ├── main.py                         # FastAPI app entry — CORS, static mounts, router wiring, DB init
│   ├── requirements.txt                # fastapi, uvicorn, python-multipart, pydantic, aiofiles, Pillow
│   ├── models/
│   │   └── citizen.py                  # Pydantic: CitizenBase, CitizenCreate, CitizenResponse, EligibilityRequest
│   ├── routes/
│   │   ├── citizens.py                 # GET/POST /citizens, GET /citizens/ngo-dashboard, GET /citizens/{id}
│   │   ├── schemes.py                  # GET/POST /schemes, POST /schemes/check-eligibility
│   │   ├── voice.py                    # POST /voice-input (audio or text), POST /voice-input/text
│   │   └── documents.py                # POST /upload-document (file → mock OCR → schemes)
│   ├── services/
│   │   ├── scheme_engine.py            # Core eligibility matching: income→age→occupation→state→gender scoring
│   │   ├── speech_service.py           # Mock Whisper transcription + NLP field extraction (regex-based)
│   │   ├── ocr_service.py              # Mock Tesseract OCR — fixed demo Aadhaar/income-cert outputs
│   │   └── translation_service.py      # Static EN/HI/TA string map
│   └── utils/
│       ├── database.py                 # SQLite init + scheme/citizen seeding
│       └── helpers.py                  # parse_income/occupation/age/state_from_text regex parsers
│
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx                # Landing — hero, language selector, action buttons, inline stats
│       │   ├── voice/page.tsx          # Wraps VoiceRecorder → saves result to sessionStorage → /results
│       │   ├── upload/page.tsx         # Document upload flow
│       │   ├── results/page.tsx        # Reads sessionStorage or ?demo=true → renders SchemeCard list
│       │   └── dashboard/page.tsx      # NGO stats + CitizenTable — falls back to DEMO_DASHBOARD
│       └── components/
│           ├── ChatAssistant.tsx        # Floating FAQ chatbot — offline-capable
│           ├── EligibilityScore.tsx     # AI Eligibility Score ring + confidence badge (mock values)
│           ├── VoiceRecorder.tsx        # Mic input + demo-text fallback
│           ├── SchemeCard.tsx           # Single scheme result card
│           ├── CitizenTable.tsx         # NGO dashboard table
│           ├── LanguageSelector.tsx     # EN / HI / TA switcher
│           └── UploadCard.tsx           # Document upload UI
│
├── datasets/
│   ├── schemes.json                    # 7 real schemes: Ayushman Bharat, e-Shram, PM-SYM, PMAY-G, PM Kisan, Ujjwala, MGNREGS
│   └── citizens_demo.json              # 3 seeded demo citizens
│
├── database/
│   └── schema.sql                      # 5 tables: citizens, schemes, applications, voice_sessions, document_uploads
│
└── ai_modules/                         # Empty — placeholder for real ML modules
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info + endpoint map |
| `GET` | `/health` | Health check |
| `POST` | `/voice-input` | Audio file or text → extracted profile + eligible schemes |
| `POST` | `/voice-input/text` | JSON text shortcut for voice |
| `POST` | `/upload-document` | File upload → mock OCR → matched schemes |
| `GET` | `/schemes` | List all schemes |
| `POST` | `/schemes` | Add scheme |
| `POST` | `/schemes/check-eligibility` | Check eligibility against criteria |
| `GET` | `/citizens` | List all citizens |
| `POST` | `/citizens` | Register citizen |
| `GET` | `/citizens/ngo-dashboard` | Aggregated NGO stats |
| `GET` | `/citizens/{id}` | Single citizen detail |

Interactive docs: **http://localhost:8000/docs**

---

## Data Flow

```
User speaks / uploads doc
        │
        ▼
  speech_service.py          ocr_service.py
  (mock Whisper +            (mock Tesseract —
   regex NLP extract)         fixed demo output)
        │                           │
        └──────────┬────────────────┘
                   ▼
          scheme_engine.py
          (income → age → occupation
           → state → gender scoring)
                   │
                   ▼
          Matched schemes JSON
                   │
                   ▼
          frontend /results page
          (SchemeCard list)
```

---

## Key Design Decisions

| Decision | Detail |
|----------|--------|
| **No real ML at runtime** | `speech_service` and `ocr_service` are mocks — no Whisper/pytesseract dependency. Safe to run offline. |
| **Frontend offline fallback** | Every page/component has a `DEMO_*` constant — frontend runs fully without the backend. |
| **SQLite** | Zero-config DB. Seeded on startup via `init_db()` in `utils/database.py`. |
| **Scoring** | `_compute_score` in `routes/schemes.py` and `eligibility_score` in `services/scheme_engine.py` are independent — results may diverge. |
| **Language** | `language` param accepted in voice routes but `extract_info_from_text` always parses as English (regex only). |

---

## Recent UI Updates

- Homepage CTA buttons clarified to: `🎤 Speak Your Details`, `📄 Upload Aadhaar`, `🔍 Find Eligible Schemes`.
- Added AI branding line under the homepage title: `Powered by AI: Speech Recognition • OCR • Eligibility Engine`.
- Added impact statement on homepage hero: `Helping 500M+ informal workers discover government welfare schemes instantly.`
- Added footer note on homepage: `Demo Mode — using simulated welfare scheme data.`
- No backend/API behavior changes and no new dependencies required.

---

## Known Gaps (for future LLMs / contributors)

| Area | Status |
|------|--------|
| `ai_modules/` | Empty — placeholder for real ML |
| `frontend/src/types/` | Empty — no shared TypeScript types |
| Pydantic models in routes | `citizen.py` models defined but routes accept raw `dict` |
| `applications` table | Schema exists, no route creates/reads applications |
| `voice_sessions` / `document_uploads` tables | Schema exists, but routes don't persist records to DB |
| Multi-language NLP | `language` param wired but regex parser is English-only |
| AI Eligibility Score | Uses hardcoded mock values (87%, High confidence) — wire to real scoring engine when available |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn, SQLite |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| OCR (mock) | Pillow (placeholder for Tesseract) |
| Speech (mock) | Placeholder for OpenAI Whisper |
| Translation | Static string map (placeholder for Google Translate API) |

## To start the web
Backend:cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\backend"
& "C:\Users\NAVIN GS\OneDrive\project\public welfare demo\.venv\Scripts\python.exe" -m uvicorn main:app --reload
Frontend:cd "c:\Users\NAVIN GS\OneDrive\project\public welfare demo\ai-welfare-assistant\frontend"
npm.cmd run dev
