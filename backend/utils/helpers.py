"""
Shared helper utilities used across the backend.
"""
import re
import json
from typing import Optional


def parse_income_from_text(text: str) -> Optional[int]:
    """Extract income figure from natural language text."""
    text = text.lower()
    # Match patterns like "10000 rupees", "₹10,000", "ten thousand"
    patterns = [
        r'(?:rs\.?|rupees?|₹)\s*([0-9,]+)',
        r'([0-9,]+)\s*(?:rs\.?|rupees?|₹)',
        r'earning\s+([0-9,]+)',
        r'earn\s+([0-9,]+)',
        r'salary\s+(?:of\s+)?([0-9,]+)',
        r'income\s+(?:of\s+)?([0-9,]+)',
    ]
    number_words = {
        "thousand": 1000, "lakh": 100000, "lac": 100000,
        "hundred": 100, "crore": 10000000
    }
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).replace(",", "")
            try:
                return int(amount_str)
            except ValueError:
                pass
    # Try word-based numbers
    for word, multiplier in number_words.items():
        match = re.search(rf'(\d+(?:\.\d+)?)\s*{word}', text)
        if match:
            return int(float(match.group(1)) * multiplier)
    return None


def parse_occupation_from_text(text: str) -> Optional[str]:
    """Extract occupation from natural language text."""
    text = text.lower()
    occupation_map = {
        "construction worker": ["construction", "building", "masonry", "mason", "carpenter", "cement"],
        "farmer": ["farmer", "farming", "agriculture", "kisan", "cultivat"],
        "domestic worker": ["domestic", "maid", "house help", "housework", "babysitter", "cook"],
        "daily wage worker": ["daily wage", "daily worker", "labour", "labor", "kooli"],
        "street vendor": ["vendor", "selling", "hawker", "street sell", "vegetable sell"],
        "auto driver": ["auto", "driver", "taxi", "cab", "rickshaw"],
        "sanitation worker": ["sanitation", "sweeper", "cleaning", "garbage", "toilet"],
        "migrant worker": ["migrant", "migration", "moved from"],
    }
    for occupation, keywords in occupation_map.items():
        for keyword in keywords:
            if keyword in text:
                return occupation
    return None


def parse_age_from_text(text: str) -> Optional[int]:
    """Extract age from text."""
    patterns = [
        r'(\d+)\s*years?\s*old',
        r'age\s*(?:is\s*)?(\d+)',
        r'i\s*am\s*(\d+)',
        r'(\d+)\s*saal',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            age = int(match.group(1))
            if 10 <= age <= 100:
                return age
    return None


def parse_state_from_text(text: str) -> Optional[str]:
    """Extract Indian state from text."""
    text = text.lower()
    states = [
        "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
        "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
        "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya",
        "mizoram", "nagaland", "odisha", "punjab", "rajasthan", "sikkim",
        "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand",
        "west bengal", "delhi", "jammu and kashmir", "ladakh"
    ]
    for state in states:
        if state in text:
            return state.title()
    return None


def format_currency(amount: float) -> str:
    """Format number as Indian currency string."""
    if amount >= 100000:
        return f"₹{amount/100000:.1f} Lakh"
    elif amount >= 1000:
        return f"₹{amount:,.0f}"
    return f"₹{amount:.0f}"


def extract_aadhaar_info(text: str) -> dict:
    """Parse mock OCR text to extract Aadhaar details."""
    info = {}
    # Name pattern
    name_match = re.search(r'(?:Name|नाम|பெயர்)[:\s]+([A-Za-z\s]+)', text)
    if name_match:
        info["name"] = name_match.group(1).strip()
    # DOB pattern
    dob_match = re.search(r'(?:DOB|Date of Birth|जन्म तिथि)[:\s]+(\d{2}[/\-]\d{2}[/\-]\d{4})', text)
    if dob_match:
        info["dob"] = dob_match.group(1)
    # State pattern
    state_text = parse_state_from_text(text)
    if state_text:
        info["state"] = state_text
    # Gender
    if "male" in text.lower() or "पुरुष" in text:
        info["gender"] = "male"
    elif "female" in text.lower() or "महिला" in text:
        info["gender"] = "female"
    return info
