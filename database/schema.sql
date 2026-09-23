DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS journal_entries;
DROP TABLE IF EXISTS daily_stats;
DROP TABLE IF EXISTS escalation_alerts;


CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE journal_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    encrypted_content TEXT NOT NULL,

    mood TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id)
);


CREATE TABLE daily_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    log_date DATE NOT NULL,

    mood TEXT,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id)
);


CREATE TABLE escalation_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    risk_level TEXT NOT NULL,

    signal_summary TEXT NOT NULL,

    status TEXT DEFAULT 'PENDING',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
        REFERENCES students(student_id)
);