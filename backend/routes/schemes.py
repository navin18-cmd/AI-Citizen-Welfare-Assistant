"""
Schemes routes - list all schemes, check eligibility for a profile.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from services.scheme_engine import get_eligible_schemes, get_all_schemes
from services.translation_service import translate, translate_scheme_fields

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.get("")
async def list_schemes(category: Optional[str] = None, language: str = "en"):
    """Return all available schemes, optionally filtered by category."""
    schemes = get_all_schemes()
    if category:
        schemes = [s for s in schemes if s.get("category", "").lower() == category.lower()]
    translated = [translate_scheme_fields(s, language) for s in schemes]
    return {"schemes": translated, "total": len(translated)}


@router.post("/check-eligibility")
async def check_eligibility(payload: dict):
    """
    Accept citizen profile dict, return eligible schemes.
    Payload: { age, occupation, income, state, gender, bpl_card, has_land }
    """
    language = payload.get("language", "en")
    try:
        eligible = get_eligible_schemes(payload)
        translated = [translate_scheme_fields(s, language) for s in eligible]
        total_benefit = sum(s.get("benefit_value", 0) for s in translated)
        score = _compute_score(translated, payload)

        return {
            "eligible_schemes": translated,
            "total_schemes": len(translated),
            "total_benefit_value": total_benefit,
            "eligibility_score": score,
            "citizen_profile": payload,
            "message": f"{translate('you_qualify', language, n=len(translated))} worth ₹{total_benefit:,.0f}",
        }
    except Exception as exc:
        LOGGER.exception("Eligibility check failed")
        raise HTTPException(status_code=500, detail=translate("validation_error", language)) from exc


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
