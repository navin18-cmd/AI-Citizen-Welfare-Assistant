"""
Pydantic models for Scheme data.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SchemeEligibility(BaseModel):
    max_income: Optional[float] = None
    occupations: Optional[List[str]] = []
    min_age: Optional[int] = 0
    max_age: Optional[int] = 100
    states: Optional[List[str]] = ["all"]
    gender: Optional[str] = None


class SchemeResponse(BaseModel):
    id: int
    name: str
    short_name: Optional[str] = None
    category: Optional[str] = None
    benefit_value: Optional[float] = None
    benefit_description: Optional[str] = None
    required_documents: Optional[List[str]] = []
    apply_link: Optional[str] = None
    hindi_name: Optional[str] = None
    tamil_name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    eligibility_score: Optional[float] = None

    class Config:
        from_attributes = True


class EligibilityResult(BaseModel):
    eligible_schemes: List[SchemeResponse]
    total_schemes: int
    total_benefit_value: float
    eligibility_score: float
    citizen_profile: Dict[str, Any]
    message: str
    language: str = "en"
