"""
Database utility - initializes SQLite and provides connection helper.
"""
import sqlite3
import json
import os
from typing import Dict, Iterable, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database", "welfare.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "database", "schema.sql")
SCHEMES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "schemes.json")
CITIZENS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "citizens_demo.json")


def get_db():
    """Return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed demo data if DB is fresh."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur = conn.cursor()

    # Create tables
    with open(SCHEMA_PATH, "r") as f:
        cur.executescript(f.read())

    # Seed schemes if empty
    cur.execute("SELECT COUNT(*) FROM schemes")
    if cur.fetchone()[0] == 0:
        with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
            schemes = json.load(f)
        for s in schemes:
            cur.execute("""
                INSERT INTO schemes (id, name, short_name, category, benefit_value,
                    benefit_description, eligibility_json, required_documents,
                    apply_link, hindi_name, tamil_name, description, icon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["id"], s["name"], s["short_name"], s["category"],
                s["benefit_value"], s["benefit_description"],
                json.dumps(s["eligibility"]),
                json.dumps(s["required_documents"]),
                s["apply_link"], s["hindi_name"], s["tamil_name"],
                s["description"], s["icon"]
            ))

    # Seed demo citizens if empty
    cur.execute("SELECT COUNT(*) FROM citizens")
    if cur.fetchone()[0] == 0:
        with open(CITIZENS_PATH, "r", encoding="utf-8") as f:
            citizens = json.load(f)
        for c in citizens:
            cur.execute("""
                INSERT INTO citizens (id, name, age, gender, occupation, income,
                    annual_income, state, district, aadhaar_number, phone,
                    bpl_card, has_land, family_size, eligibility_score, total_benefits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], c["name"], c["age"], c["gender"], c["occupation"],
                c["income"], c["annual_income"], c["state"], c["district"],
                c["aadhaar_number"], c["phone"], c["bpl_card"],
                c.get("has_land", False), c["family_size"],
                c["eligibility_score"], c["total_benefits"]
            ))

            # Seed applications for registered schemes
            for scheme_name in c.get("registered_schemes", []):
                cur.execute("SELECT id FROM schemes WHERE short_name = ? OR name LIKE ?",
                            (scheme_name, f"%{scheme_name}%"))
                row = cur.fetchone()
                if row:
                    cur.execute("""
                        INSERT INTO applications (citizen_id, scheme_id, status, eligibility_score)
                        VALUES (?, ?, 'approved', ?)
                    """, (c["id"], row["id"], c["eligibility_score"]))

    conn.commit()
    conn.close()


def _json_dumps_safe(value) -> str:
    return json.dumps(value or {}, ensure_ascii=False)


def get_or_create_citizen(profile: Dict) -> int:
    """Resolve citizen id from profile or create a minimal record."""
    conn = get_db()
    cur = conn.cursor()

    name = (profile.get("name") or "").strip()
    age = profile.get("age")
    state = profile.get("state")
    occupation = profile.get("occupation")
    income = profile.get("income")

    if name:
        row = cur.execute(
            "SELECT id FROM citizens WHERE name = ? AND COALESCE(state, '') = COALESCE(?, '') ORDER BY id DESC LIMIT 1",
            (name, state),
        ).fetchone()
        if row:
            conn.close()
            return int(row["id"])

    cur.execute(
        """
        INSERT INTO citizens (name, age, occupation, income, annual_income, state, bpl_card, has_land, family_size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name or "Unknown",
            age,
            occupation,
            income,
            (income or 0) * 12,
            state,
            bool(profile.get("bpl_card", False)),
            bool(profile.get("has_land", False)),
            1,
        ),
    )
    conn.commit()
    citizen_id = int(cur.execute("SELECT last_insert_rowid()").fetchone()[0])
    conn.close()
    return citizen_id


def save_voice_session(citizen_id: int, transcript: str, extracted_data: Dict, language: str = "en") -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO voice_sessions (citizen_id, transcript, extracted_data, language)
        VALUES (?, ?, ?, ?)
        """,
        (citizen_id, transcript, _json_dumps_safe(extracted_data), language),
    )
    conn.commit()
    row_id = int(cur.execute("SELECT last_insert_rowid()").fetchone()[0])
    conn.close()
    return row_id


def save_document_upload(
    citizen_id: Optional[int],
    document_type: str,
    file_path: str,
    extracted_text: str,
    parsed_data: Dict,
) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO document_uploads (citizen_id, document_type, file_path, extracted_text, parsed_data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (citizen_id, document_type, file_path, extracted_text, _json_dumps_safe(parsed_data)),
    )
    conn.commit()
    row_id = int(cur.execute("SELECT last_insert_rowid()").fetchone()[0])
    conn.close()
    return row_id


def save_applications(citizen_id: int, schemes: Iterable[Dict]) -> int:
    """Store scheme recommendations as pending applications."""
    conn = get_db()
    cur = conn.cursor()
    inserted = 0
    for scheme in schemes:
        scheme_id = scheme.get("id")
        if not scheme_id:
            continue
        cur.execute(
            """
            INSERT INTO applications (citizen_id, scheme_id, status, eligibility_score, notes)
            VALUES (?, ?, 'pending', ?, ?)
            """,
            (
                citizen_id,
                scheme_id,
                scheme.get("eligibility_score", 0),
                scheme.get("reason", "Auto-generated recommendation"),
            ),
        )
        inserted += 1
    conn.commit()
    conn.close()
    return inserted
