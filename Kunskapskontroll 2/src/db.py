import os, sqlite3
from pathlib import Path

DB_PATH = os.path.join("data", "jobs.db")

def _ensure_dirs():
    Path("data").mkdir(parents=True, exist_ok=True)

def get_conn():
    _ensure_dirs()
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_ads (
                id TEXT PRIMARY KEY,
                fetched_at TEXT DEFAULT (datetime('now')),
                payload TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agg_daily (
                date TEXT NOT NULL,
                county TEXT,
                occupation_group TEXT,
                ad_count INTEGER NOT NULL,
                PRIMARY KEY (date, county, occupation_group)
            );
        """)
        conn.commit()
