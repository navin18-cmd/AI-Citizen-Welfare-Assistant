"""
Scheme eligibility engine - core matching logic.
Loads schemes from JSON and matches against citizen profile.
"""
import json
import os
from typing import List, Dict, Any

SCHEMES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "schemes.json")

_schemes_cache = None


def get_all_schemes() -> List[Dict]:
    global _schemes_cache
    if _schemes_cache is None:
        with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
            _schemes_cache = json.load(f)
    return _schemes_cache


def get_eligible_schemes(profile: Dict[str, Any]) -> List[Dict]:
    """
    Match citizen profile against all schemes.
    Returns list of eligible schemes with individual eligibility scores.
    """
    schemes = get_all_schemes()
    eligible = []

    age = profile.get("age") or 30
    income = profile.get("income") or 0
    annual_income = profile.get("annual_income") or (income * 12)
    occupation = (profile.get("occupation") or "").lower().strip()
    state = (profile.get("state") or "all").lower()
    gender = (profile.get("gender") or "").lower()
    has_land = profile.get("has_land", False)
    bpl_card = profile.get("bpl_card", False)

    for scheme in schemes:
        elig = scheme.get("eligibility", {})
        score = 0
        reasons = []

        # Income check
        max_income = elig.get("max_income", 999999)
        if annual_income <= max_income:
            score += 30
            reasons.append("Income qualifies")
        else:
            continue  # Hard fail if income too high

        # Age check
        min_age = elig.get("min_age", 0)
        max_age = elig.get("max_age", 100)
        if min_age <= age <= max_age:
            score += 25
            reasons.append("Age qualifies")
        else:
            continue  # Hard fail on age

        # Occupation check
        allowed_occupations = [o.lower() for o in elig.get("occupations", [])]
        if "all" in allowed_occupations or not allowed_occupations:
            score += 20
            reasons.append("Occupation qualifies")
        elif occupation and any(
            occ in occupation or occupation in occ
            for occ in allowed_occupations
        ):
            score += 20
            reasons.append(f"Occupation '{occupation}' qualifies")
        elif not occupation:
            score += 10  # partial
        else:
            continue  # Hard fail on occupation

        # State check
        allowed_states = [s.lower() for s in elig.get("states", ["all"])]
        if "all" in allowed_states or state in allowed_states:
            score += 15
            reasons.append("State qualifies")
        else:
            score += 5

        # Gender check (only if scheme restricts)
        required_gender = elig.get("gender", None)
        if required_gender and gender and required_gender.lower() != gender:
            continue  # Fail on gender mismatch
        elif required_gender and gender == required_gender:
            score += 10

        # Bonus points
        if bpl_card:
            score += 5
        if has_land and scheme.get("category") == "Agriculture":
            score += 10

        scheme_copy = dict(scheme)
        scheme_copy["eligibility_score"] = min(score, 100)
        scheme_copy["eligibility_reasons"] = reasons
        eligible.append(scheme_copy)

    # Sort by eligibility score descending
    eligible.sort(key=lambda x: x["eligibility_score"], reverse=True)

    # Safety: never return zero schemes (demo requirement)
    if not eligible:
        fallback_ids = {1, 2, 3}  # Ayushman Bharat, e-Shram, PM-SYM
        for scheme in schemes:
            if scheme["id"] in fallback_ids:
                s = dict(scheme)
                s["eligibility_score"] = 60
                s["eligibility_reasons"] = ["Default welfare eligibility"]
                eligible.append(s)

    return eligible
