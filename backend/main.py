"""
AI Welfare Assistant - FastAPI Backend
Main entry point. Sets up CORS, mounts routes, initializes DB.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from utils.database import init_db
from routes import voice, documents, schemes, citizens

app = FastAPI(
    title="AI Citizen Welfare Assistant API",
    description="Backend API for the AI Welfare Assistant hackathon demo",
    version="1.0.0"
)

# CORS - allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads folder as static
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(voice.router, prefix="/voice-input", tags=["Voice"])
app.include_router(documents.router, prefix="/upload-document", tags=["Documents"])
app.include_router(schemes.router, prefix="/schemes", tags=["Schemes"])
app.include_router(citizens.router, prefix="/citizens", tags=["Citizens"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    init_db()
    sys.stdout.write("[OK] Database initialized\n")
    sys.stdout.write("[OK] AI Welfare Assistant API running at http://localhost:8000\n")
    sys.stdout.flush()


@app.get("/")
async def root():
    return {
        "message": "AI Citizen Welfare Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "voice": "/voice-input",
            "documents": "/upload-document",
            "schemes": "/schemes",
            "citizens": "/citizens",
            "ngo_dashboard": "/citizens/ngo-dashboard",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
