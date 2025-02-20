import sqlite3
from pathlib import Path
from logger import get_logger

logger = get_logger()
DB_PATH = Path(__file__).parent / " .db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile TEXT,
            mode TEXT,
            lang TEXT,
            timestamp TEXT,
            answers TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_record(record: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO entries (profile, mode, lang, timestamp, answers)
        VALUES (?, ?, ?, ?, ?)
    """, (record["profile"], record["mode"], record["lang"], record["timestamp"], record["answers"]))
    conn.commit()
    conn.close()


def fetch_records(profile: str, lang: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT profile, mode, lang, timestamp, answers FROM entries
        WHERE profile = ? AND lang = ?
        ORDER BY timestamp DESC
    """, (profile, lang))
    rows = c.fetchall()
    conn.close()
    return [{"profile": row[0], "mode": row[1], "lang": row[2], "timestamp": row[3], "answers": row[4]} for row in rows]
