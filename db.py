import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'tracker.db'

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open('schema.sql', 'r') as f:
        conn = get_conn()
        conn.executescript(f.read())
        conn.commit()
        conn.close()

def add_record(user_id, date_str, mood_val, work_hours, sleep_hours, comment):
    conn = get_conn()
    conn.execute('INSERT INTO records (user_id, date, mood, work_hours, sleep_hours, comment) VALUES (?, ?, ?, ?, ?, ?)',
                 (user_id, date_str, mood_val, work_hours, sleep_hours, comment))
    conn.commit()
    conn.close()

def get_records(user_id, days):
    conn = get_conn()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    res = conn.execute('SELECT * FROM records WHERE user_id = ? AND date >= ? ORDER BY date', (user_id, cutoff)).fetchall()
    conn.close()
    return [dict(row) for row in res]

def clear_user_data(user_id):
    conn = get_conn()
    conn.execute('DELETE FROM records WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()