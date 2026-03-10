"""
Schemes routes - list all schemes, check eligibility for a profile.
"""
from fastapi import APIRouter
from typing import Optional
import json, os

from services.scheme_engine import get_eligible_schemes, get_all_schemes

router = APIRouter()


@router.get("")
async def list_schemes(category: Optional[str] = None, language: str = "en"):
    """Return all available schemes, optionally filtered by category."""
    schemes = get_all_schemes()
    if category:
        schemes = [s for s in schemes if s.get("category", "").lower() == category.lower()]
    return {"schemes": schemes, "total": len(schemes)}


@router.post("/check-eligibility")
async def check_eligibility(payload: dict):
    """
    Accept citizen profile dict, return eligible schemes.
    Payload: { age, occupation, income, state, gender, bpl_card, has_land }
    """
    eligible = get_eligible_schemes(payload)
    total_benefit = sum(s["benefit_value"] for s in eligible)
    score = _compute_score(eligible, payload)

    return {
        "eligible_schemes": eligible,
        "total_schemes": len(eligible),
        "total_benefit_value": total_benefit,
        "eligibility_score": score,
        "citizen_profile": payload,
        "message": f"You qualify for {len(eligible)} government welfare schemes worth ₹{total_benefit:,.0f}"
    }


@router.get("/categories")
async def get_categories():
    schemes = get_all_schemes()
    cats = list(set(s.get("category", "") for s in schemes))
    return {"categories": sorted(cats)}


def _compute_score(eligible_schemes: list, profile: dict) -> float:
    """Simple weighted eligibility score 0-100."""
    base = min(len(eligible_schemes) * 12, 60)
    income_bonus = 20 if profile.get("income", 999999) < 15000 else 10
    bpl_bonus = 15 if profile.get("bpl_card") else 0
    age_bonus = 5 if 18 <= (profile.get("age") or 30) <= 55 else 0
    return min(base + income_bonus + bpl_bonus + age_bonus, 100)
