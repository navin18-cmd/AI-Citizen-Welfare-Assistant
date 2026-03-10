"""
Database utility - initializes SQLite and provides connection helper.
"""
import sqlite3
import json
import os

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
