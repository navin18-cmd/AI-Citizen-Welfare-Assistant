-- AI Welfare Assistant - SQLite Schema

CREATE TABLE IF NOT EXISTS citizens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    occupation TEXT,
    income REAL,
    annual_income REAL,
    state TEXT,
    district TEXT,
    aadhaar_number TEXT UNIQUE,
    phone TEXT,
    bank_account TEXT,
    bpl_card BOOLEAN DEFAULT FALSE,
    ration_card TEXT,
    has_land BOOLEAN DEFAULT FALSE,
    land_area TEXT,
    family_size INTEGER DEFAULT 1,
    eligibility_score REAL DEFAULT 0,
    total_benefits REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    registered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    short_name TEXT,
    category TEXT,
    benefit_value REAL,
    benefit_description TEXT,
    eligibility_json TEXT,
    required_documents TEXT,
    apply_link TEXT,
    hindi_name TEXT,
    tamil_name TEXT,
    description TEXT,
    icon TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citizen_id INTEGER,
    scheme_id INTEGER,
    status TEXT DEFAULT 'pending',
    applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    eligibility_score REAL,
    notes TEXT,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id),
    FOREIGN KEY (scheme_id) REFERENCES schemes(id)
);

CREATE TABLE IF NOT EXISTS voice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citizen_id INTEGER,
    transcript TEXT,
    extracted_data TEXT,
    language TEXT DEFAULT 'en',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    citizen_id INTEGER,
    document_type TEXT,
    file_path TEXT,
    extracted_text TEXT,
    parsed_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
