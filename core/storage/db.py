import sqlite3
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "leadgen.db"

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_url TEXT UNIQUE,
                title TEXT,
                account_name TEXT,
                publish_time TEXT,
                relevance_score INTEGER,
                heat_level TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                strategy TEXT,
                comment_content TEXT,
                posted INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0,
                likes_count INTEGER DEFAULT 0,
                posted_at TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                comments_sent INTEGER DEFAULT 0,
                featured_count INTEGER DEFAULT 0
            );
            """)
            conn.commit()

    def is_article_processed(self, url: str) -> bool:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT id FROM articles WHERE article_url = ?", (url,))
            return cur.fetchone() is not None

    def save_article(self, url: str, title: str, account_name: str, score: int, heat_level: str) -> int:
        with self._get_conn() as conn:
            cur = conn.execute(
                """INSERT OR REPLACE INTO articles 
                   (article_url, title, account_name, relevance_score, heat_level, status)
                   VALUES (?, ?, ?, ?, ?, 'evaluated')""",
                (url, title, account_name, score, heat_level)
            )
            conn.commit()
            return cur.lastrowid

    def save_comments(self, article_id: int, comments: List[Dict[str, str]]):
        with self._get_conn() as conn:
            for item in comments:
                conn.execute(
                    """INSERT INTO comments (article_id, strategy, comment_content)
                       VALUES (?, ?, ?)""",
                    (article_id, item.get("strategy", "unknown"), item.get("content", ""))
                )
            conn.commit()

    def get_daily_comment_count(self) -> int:
        today = datetime.date.today().isoformat()
        with self._get_conn() as conn:
            cur = conn.execute("SELECT comments_sent FROM daily_stats WHERE date = ?", (today,))
            row = cur.fetchone()
            return row["comments_sent"] if row else 0

    def increment_daily_comment(self):
        today = datetime.date.today().isoformat()
        with self._get_conn() as conn:
            conn.execute("""
            INSERT INTO daily_stats (date, comments_sent) VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET comments_sent = comments_sent + 1
            """, (today,))
            conn.commit()
