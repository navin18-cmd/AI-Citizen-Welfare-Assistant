"""
Citizens routes - CRUD for citizens + NGO dashboard.
"""
from fastapi import APIRouter, HTTPException
from utils.database import get_db
import json

router = APIRouter()


@router.get("")
async def list_citizens():
    """Return all citizens (for NGO dashboard)."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM citizens").fetchall()
    conn.close()
    return {"citizens": [dict(r) for r in rows], "total": len(rows)}


@router.get("/ngo-dashboard")
async def ngo_dashboard():
    """Aggregated stats for the NGO worker dashboard."""
    conn = get_db()
    citizens = [dict(r) for r in conn.execute("SELECT * FROM citizens").fetchall()]
    schemes = conn.execute("SELECT COUNT(*) as total FROM schemes").fetchone()["total"]
    apps = conn.execute(
        "SELECT citizen_id, scheme_id, status FROM applications"
    ).fetchall()
    conn.close()

    total_benefits = sum(c.get("total_benefits", 0) for c in citizens)
    approved = sum(1 for a in apps if a["status"] == "approved")

    return {
        "summary": {
            "total_citizens": len(citizens),
            "total_schemes_available": schemes,
            "total_applications": len(apps),
            "approved_applications": approved,
            "total_benefits_unlocked": total_benefits
        },
        "citizens": citizens
    }


@router.get("/{citizen_id}")
async def get_citizen(citizen_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM citizens WHERE id = ?", (citizen_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Citizen not found")
    citizen = dict(row)
    # Get their applications
    apps = conn.execute(
        """SELECT a.*, s.name as scheme_name, s.benefit_value, s.icon
           FROM applications a JOIN schemes s ON a.scheme_id = s.id
           WHERE a.citizen_id = ?""",
        (citizen_id,)
    ).fetchall()
    conn.close()
    citizen["applications"] = [dict(a) for a in apps]
    return citizen


@router.post("")
async def create_citizen(payload: dict):
    """Register a new citizen (from voice/form input)."""
    conn = get_db()
    conn.execute("""
        INSERT INTO citizens (name, age, gender, occupation, income, annual_income,
            state, district, phone, bpl_card, family_size, eligibility_score, total_benefits)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.get("name", "Unknown"),
        payload.get("age"),
        payload.get("gender"),
        payload.get("occupation"),
        payload.get("income"),
        (payload.get("income") or 0) * 12,
        payload.get("state"),
        payload.get("district"),
        payload.get("phone"),
        payload.get("bpl_card", False),
        payload.get("family_size", 1),
        payload.get("eligibility_score", 0),
        payload.get("total_benefits", 0),
    ))
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return {"id": new_id, "message": "Citizen registered successfully"}
