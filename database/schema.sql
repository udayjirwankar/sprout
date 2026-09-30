CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS journal_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    encrypted_content TEXT NOT NULL,

    mood TEXT,

    day_factors TEXT,

    helpful_needs TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id)
);


CREATE TABLE IF NOT EXISTS daily_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    log_date DATE NOT NULL,

    mood TEXT,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id)
);


CREATE TABLE IF NOT EXISTS escalation_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    risk_level TEXT NOT NULL,

    signal_summary TEXT NOT NULL,

    status TEXT DEFAULT 'PENDING',

    reviewed_at TIMESTAMP,

    resolved_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id)
);
