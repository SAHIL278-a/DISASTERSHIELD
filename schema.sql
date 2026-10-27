CREATE TABLE IF NOT EXISTS disaster_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_type TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT,
    severity TEXT DEFAULT 'Pending',
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_type TEXT NOT NULL,
    rainfall_mm REAL DEFAULT 0,
    wind_speed_kmh REAL DEFAULT 0,
    water_level_rising INTEGER DEFAULT 0,
    people_at_risk INTEGER DEFAULT 0,
    risk_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    message TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);