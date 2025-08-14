import sqlite3
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.create_db()

    def create_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
        """)
        conn.commit()
        conn.close()

        if not self.get_products():
            self.add_product("Burger", 5.99)
            self.add_product("Pizza", 8.50)
            self.add_product("Pasta", 6.75)

    def add_product(self, name, price):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()

    def get_products(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        conn.close()
        return products

    def update_product(self, product_id, name, price):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE products SET name=?, price=? WHERE id=?", (name, price, product_id))
        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()
