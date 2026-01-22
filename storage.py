import sqlite3
import json
from datetime import datetime

class ChatStorage:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_message(self, role, content):
        """Saves a single message to the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        conn.commit()
        conn.close()

    def load_history(self, limit=50):
        """Loads the last N messages from history."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Get last N messages ordered by timestamp ascending (oldest to newest)
        # We select sorted by id DESC first to get the *latest* N, then re-sort ASC for display
        c.execute('''
            SELECT role, content FROM (
                SELECT id, role, content, timestamp 
                FROM messages 
                ORDER BY id DESC 
                LIMIT ?
            ) ORDER BY id ASC
        ''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        return [{"role": row[0], "content": row[1]} for row in rows]

    def clear_history(self):
        """Clears all messages."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM messages')
        conn.commit()
        conn.close()
