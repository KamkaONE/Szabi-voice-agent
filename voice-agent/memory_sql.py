# /opt/agent/voice-agent/memory_sql.py
import sqlite3
from typing import List, Dict, Any

class SQLiteMemory:
    def __init__(self, db_path="/opt/Livekit/conversations.db"):
        self.db_path = db_path
        self._ensure()

    def _ensure(self):
        with sqlite3.connect(self.db_path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

    def add_message(self, role: str, content: str):
        with sqlite3.connect(self.db_path) as c:
            c.execute("INSERT INTO messages(role, content) VALUES(?, ?)", (role, content))

    def get_context_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as c:
            rows = c.execute(
                "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
