"""
Simple SQLite storage for ingested content and extracted insights.
"""
import sqlite3
from datetime import datetime
from config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,          -- 'youtube' or 'rss'
            source_name TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            published_at TEXT,
            raw_text TEXT,
            ingested_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            category TEXT,                      -- 'model_release', 'benchmark', 'tool', 'capability', 'research'
            model_or_tool TEXT,
            summary TEXT NOT NULL,
            significance TEXT,                  -- 'major', 'minor', 'incremental'
            extracted_at TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(id)
        );

        CREATE INDEX IF NOT EXISTS idx_sources_url ON sources(url);
        CREATE INDEX IF NOT EXISTS idx_insights_category ON insights(category);
    """)
    conn.commit()
    conn.close()


def source_exists(url: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT 1 FROM sources WHERE url = ?", (url,)).fetchone()
    conn.close()
    return row is not None


def insert_source(source_type, source_name, title, url, published_at, raw_text) -> int:
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO sources (source_type, source_name, title, url, published_at, raw_text, ingested_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (source_type, source_name, title, url, published_at, raw_text, datetime.utcnow().isoformat())
    )
    conn.commit()
    source_id = cur.lastrowid
    conn.close()
    return source_id


def insert_insights(source_id: int, insights: list[dict]):
    conn = get_db()
    for ins in insights:
        conn.execute(
            """INSERT INTO insights (source_id, category, model_or_tool, summary, significance, extracted_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (source_id, ins.get("category"), ins.get("model_or_tool"),
             ins["summary"], ins.get("significance"), datetime.utcnow().isoformat())
        )
    conn.commit()
    conn.close()


def get_recent_insights(days: int = 7) -> list[dict]:
    conn = get_db()
    rows = conn.execute("""
        SELECT i.*, s.title as source_title, s.url as source_url, s.source_name
        FROM insights i
        JOIN sources s ON i.source_id = s.id
        WHERE i.extracted_at >= datetime('now', ?)
        ORDER BY i.extracted_at DESC
    """, (f"-{days} days",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
