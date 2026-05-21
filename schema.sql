CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    mood INTEGER CHECK(mood BETWEEN 1 AND 5),
    work_hours REAL NOT NULL,
    sleep_hours REAL NOT NULL,
    comment TEXT
);