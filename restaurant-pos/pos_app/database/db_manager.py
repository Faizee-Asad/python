import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "pos.db"

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def create_tables(self):
        schema_file = Path(__file__).parent / "schema.sql"
        with open(schema_file, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def validate_admin(self, username, password):
        query = "SELECT * FROM admin WHERE username=? AND password=?"
        result = self.conn.execute(query, (username, password)).fetchone()
        return result is not None
