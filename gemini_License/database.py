import sqlite3
from datetime import datetime, timedelta
import os

class Database:
    def __init__(self, db_name="restaurant_pos.db"):
        """Initializes the database connection and creates tables if they don't exist."""
        home_dir = os.path.expanduser("~")
        app_data_dir = os.path.join(home_dir, "DineDashPOS")
        os.makedirs(app_data_dir, exist_ok=True)
        db_path = os.path.join(app_data_dir, db_name)
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates all necessary tables for the POS system."""
        # --- NEW: Settings Table for License ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Server'))
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                capacity INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('open', 'closed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES tables(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_at_time REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        self.conn.commit()
        self.seed_initial_data()

    def seed_initial_data(self):
        """Seeds the database with some initial data if it's empty."""
        # --- NEW: Seed license status ---
        self.cursor.execute("SELECT COUNT(*) FROM settings WHERE key='license_status'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO settings (key, value) VALUES ('license_status', 'unlicensed')")

        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            users = [('Admin', 'Admin'), ('Jessica', 'Server'), ('David', 'Server')]
            self.cursor.executemany("INSERT INTO users (username, role) VALUES (?, ?)", users)

        self.cursor.execute("SELECT COUNT(*) FROM tables")
        if self.cursor.fetchone()[0] == 0:
            tables = [('T1', 2), ('T2', 4), ('T3', 4), ('T4', 6), ('P1', 8), ('T5', 2), 
                      ('T6', 4), ('B1', 2), ('B2', 2), ('T7', 6), ('T8', 4), ('P2', 4)]
            self.cursor.executemany("INSERT INTO tables (name, capacity) VALUES (?, ?)", tables)

        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            products = [
                ('Spring Rolls', 8.99, 'Appetizers'), ('Garlic Bread', 6.50, 'Appetizers'),
                ('Margherita Pizza', 15.99, 'Mains'), ('Spaghetti Carbonara', 18.50, 'Mains'),
                ('Tiramisu', 9.50, 'Desserts'), ('Coca-Cola', 3.50, 'Drinks')
            ]
            self.cursor.executemany("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", products)
        
        self.conn.commit()

    # --- NEW: Settings Methods ---
    def get_setting(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else None

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    # --- User Methods ---
    def get_users(self):
        self.cursor.execute("SELECT id, username, role FROM users")
        return self.cursor.fetchall()
        
    def get_user_by_name(self, username):
        self.cursor.execute("SELECT id, username, role FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    # --- Product (Menu Item) Methods ---
    def get_products(self):
        self.cursor.execute("SELECT id, name, price, category FROM products ORDER BY category, name")
        return self.cursor.fetchall()
        
    def get_product_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def add_product(self, name, price, category):
        self.cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", (name, price, category))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_product(self, product_id, name, price, category):
        self.cursor.execute("UPDATE products SET name=?, price=?, category=? WHERE id=?", (name, price, category, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    # --- Table Methods ---
    def get_tables(self):
        self.cursor.execute('''
            SELECT t.id, t.name, t.capacity, 
                   CASE WHEN o.id IS NOT NULL THEN 'occupied' ELSE 'available' END as status
            FROM tables t
            LEFT JOIN orders o ON t.id = o.table_id AND o.status = 'open'
            ORDER BY t.id
        ''')
        return self.cursor.fetchall()
        
    def get_all_tables_for_management(self):
        self.cursor.execute("SELECT id, name, capacity FROM tables ORDER BY name")
        return self.cursor.fetchall()

    def add_table(self, name, capacity):
        self.cursor.execute("INSERT INTO tables (name, capacity) VALUES (?, ?)", (name, capacity))
        self.conn.commit()

    def update_table(self, table_id, name, capacity):
        self.cursor.execute("UPDATE tables SET name=?, capacity=? WHERE id=?", (name, capacity, table_id))
        self.conn.commit()

    def delete_table(self, table_id):
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE table_id=? AND status='open'", (table_id,))
        if self.cursor.fetchone()[0] > 0:
            return False
        self.cursor.execute("DELETE FROM tables WHERE id=?", (table_id,))
        self.conn.commit()
        return True

    # --- Order Methods ---
    def get_open_order_for_table(self, table_id):
        self.cursor.execute("SELECT id FROM orders WHERE table_id=? AND status='open'", (table_id,))
        return self.cursor.fetchone()

    def create_order(self, table_id, user_id):
        self.cursor.execute("INSERT INTO orders (table_id, user_id, status) VALUES (?, ?, 'open')", (table_id, user_id))
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_order_items(self, order_id):
        self.cursor.execute('''
            SELECT oi.id, p.id, p.name, oi.quantity, oi.price_at_time
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        return self.cursor.fetchall()

    def add_item_to_order(self, order_id, product_id, quantity, price):
        self.cursor.execute("SELECT id, quantity FROM order_items WHERE order_id=? AND product_id=?", (order_id, product_id))
        existing_item = self.cursor.fetchone()
        
        if existing_item:
            new_quantity = existing_item['quantity'] + quantity
            self.cursor.execute("UPDATE order_items SET quantity=? WHERE id=?", (new_quantity, existing_item['id']))
        else:
            self.cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", 
                                (order_id, product_id, quantity, price))
        self.conn.commit()

    def update_order_item_quantity(self, order_item_id, new_quantity):
        if new_quantity > 0:
            self.cursor.execute("UPDATE order_items SET quantity=? WHERE id=?", (new_quantity, order_item_id))
        else:
            self.cursor.execute("DELETE FROM order_items WHERE id=?", (order_item_id,))
        self.conn.commit()

    def close_order(self, order_id):
        self.cursor.execute("UPDATE orders SET status='closed', closed_at=? WHERE id=?", (datetime.now(), order_id))
        self.conn.commit()

    def get_last_closed_order_for_table(self, table_id):
        self.cursor.execute('''
            SELECT id, user_id, closed_at FROM orders 
            WHERE table_id=? AND status='closed' 
            ORDER BY closed_at DESC LIMIT 1
        ''', (table_id,))
        return self.cursor.fetchone()

    # --- Reporting Methods ---
    def get_all_sales_data_for_export(self):
        """Fetches all closed order data for analysis."""
        self.cursor.execute('''
            SELECT
                o.closed_at,
                t.name as table_name,
                u.username as server,
                p.name as product_name,
                p.category,
                oi.quantity,
                oi.price_at_time
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            JOIN users u ON o.user_id = u.id
            JOIN tables t ON o.table_id = t.id
            WHERE o.status = 'closed'
            ORDER BY o.closed_at
        ''')
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()
