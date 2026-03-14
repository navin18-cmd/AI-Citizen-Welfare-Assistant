"""Scheme eligibility engine with rule filtering and dynamic scoring."""

import json
import os
from typing import Any, Dict, List

SCHEMES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "schemes.json")

_schemes_cache = None


def get_all_schemes() -> List[Dict]:
    global _schemes_cache
    if _schemes_cache is None:
        with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
            _schemes_cache = json.load(f)
    return _schemes_cache


def get_eligible_schemes(profile: Dict[str, Any]) -> List[Dict]:
    """Match citizen profile with 2-step rule filtering and scoring."""
    schemes = get_all_schemes()
    eligible = []

    age = profile.get("age")
    income = profile.get("income") or 0
    annual_income = profile.get("annual_income") or (income * 12)
    occupation = (profile.get("occupation") or "").lower().strip()
    state = (profile.get("state") or "all").lower()
    gender = (profile.get("gender") or "").lower()
    has_land = profile.get("has_land", False)
    bpl_card = profile.get("bpl_card", False)

    for scheme in schemes:
        elig = scheme.get("eligibility", {})

        # Step 1 - Rule Filtering.
        max_income = elig.get("max_income", 999999)
        if annual_income and annual_income > max_income:
            continue

        min_age = elig.get("min_age", 0)
        max_age = elig.get("max_age", 100)
        if age is not None and not (min_age <= age <= max_age):
            continue

        allowed_occupations = [o.lower() for o in elig.get("occupations", [])]
        occupation_match = (
            not allowed_occupations
            or "all" in allowed_occupations
            or not occupation
            or any(occ in occupation or occupation in occ for occ in allowed_occupations)
        )
        if not occupation_match:
            continue

        allowed_states = [s.lower() for s in elig.get("states", ["all"])]
        state_match = "all" in allowed_states or state in allowed_states or state == "all"
        if not state_match:
            continue

        required_gender = elig.get("gender", None)
        if required_gender and gender and required_gender.lower() != gender:
            continue

        # Step 2 - Dynamic scoring in 60-95.
        score = 60
        reasons = []

        if annual_income:
            income_ratio = min(annual_income / max(max_income, 1), 1)
            score += int((1 - income_ratio) * 12)
            reasons.append(f"Income is within scheme threshold (<= Rs {max_income:,}/year)")
        else:
            score += 5
            reasons.append("Income not provided; matched on other profile rules")

        if age is None:
            score += 3
            reasons.append("Age not provided; age-limited criteria could not be strictly validated")
        else:
            age_span = max(max_age - min_age, 1)
            age_center = (min_age + max_age) / 2
            age_distance = abs(age - age_center) / (age_span / 2)
            score += max(0, 8 - int(age_distance * 6))
            reasons.append(f"Age fits scheme range ({min_age}-{max_age})")

        if allowed_occupations and "all" not in allowed_occupations:
            score += 7 if occupation else 3
            if occupation:
                reasons.append(f"Occupation '{occupation}' aligns with scheme target group")
        else:
            score += 4
            reasons.append("Scheme is open across multiple occupations")

        if state_match:
            score += 4
            reasons.append("Scheme is available in your state")

        if required_gender and gender == required_gender.lower():
            score += 2
            reasons.append(f"Gender-specific requirement met ({required_gender})")

        if bpl_card:
            score += 2
            reasons.append("BPL/ration indicator improves priority")
        if has_land and scheme.get("category") == "Agriculture":
            score += 3
            reasons.append("Land ownership supports agriculture scheme eligibility")

        score = max(60, min(score, 95))
        reason_text = "; ".join(reasons[:3])

        scheme_copy = dict(scheme)
        scheme_copy["scheme_name"] = scheme.get("name", "")
        scheme_copy["eligibility_score"] = score
        scheme_copy["reason"] = reason_text
        scheme_copy["benefit_summary"] = scheme.get("benefit_description", "")
        scheme_copy["eligibility_reasons"] = reasons
        eligible.append(scheme_copy)

    # Sort by eligibility score descending
    eligible.sort(key=lambda x: x["eligibility_score"], reverse=True)

    # Safety fallback.
    if not eligible:
        fallback_ids = {1, 2, 3}
        for scheme in schemes:
            if scheme["id"] in fallback_ids:
                s = dict(scheme)
                s["scheme_name"] = s.get("name", "")
                s["eligibility_score"] = 60
                s["reason"] = "No exact profile match found; added as baseline high-impact welfare scheme"
                s["benefit_summary"] = s.get("benefit_description", "")
                s["eligibility_reasons"] = [s["reason"]]
                eligible.append(s)

    return eligible
