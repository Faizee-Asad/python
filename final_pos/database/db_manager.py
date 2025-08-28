import sqlite3

DB_NAME = "restaurant_pos.db"

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Menu Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
        """)

        # Orders Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def insert_menu_item(self, name, price):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
        self.conn.commit()

    def get_menu_items(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM menu")
        return cursor.fetchall()

    def insert_order(self, item_name, quantity, total_price):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO orders (item_name, quantity, total_price) VALUES (?, ?, ?)",
                       (item_name, quantity, total_price))
        self.conn.commit()
