"""
Pydantic models for Citizen data.
"""
from pydantic import BaseModel
from typing import Optional, List


class CitizenBase(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None


class CitizenCreate(CitizenBase):
    aadhaar_number: Optional[str] = None
    phone: Optional[str] = None
    bpl_card: Optional[bool] = False
    family_size: Optional[int] = 1


class CitizenResponse(CitizenBase):
    id: int
    eligibility_score: Optional[float] = 0
    total_benefits: Optional[float] = 0
    status: Optional[str] = "active"

    class Config:
        from_attributes = True


class EligibilityRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[float] = None
    state: Optional[str] = None
    bpl_card: Optional[bool] = False
    has_land: Optional[bool] = False
    family_size: Optional[int] = 1
