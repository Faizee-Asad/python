import sqlite3
from datetime import datetime
import os

class Database:
    def _init_(self, db_name="dinedash.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.seed_data()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tables table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category_id INTEGER,
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                user_id INTEGER,
                status TEXT DEFAULT 'active',
                total REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES tables (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Order items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def seed_data(self):
        # Check if data already exists
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] > 0:
            return
        
        # Seed users
        users = [
            ('admin', 'admin123', 'Administrator'),
            ('jessica', 'pass123', 'Server'),
            ('david', 'pass123', 'Server'),
            ('maria', 'pass123', 'Server')
        ]
        self.cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)
        
        # Seed tables
        tables = [
            ('T1', 2), ('T2', 4), ('T3', 4), ('T4', 4),
            ('T5', 6), ('T6', 6), ('T7', 4), ('T8', 4),
            ('P1', 8), ('P2', 8), ('P3', 10), ('P4', 10),
            ('VIP1', 8), ('VIP2', 12), ('B1', 2), ('B2', 2)
        ]
        self.cursor.executemany("INSERT INTO tables (name, capacity) VALUES (?, ?)", tables)
        
        # Seed categories
        categories = [
            ('Appetizers', '🥗'),
            ('Mains', '🍽'),
            ('Desserts', '🍰'),
            ('Drinks', '🥤')
        ]
        self.cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", categories)
        
        # Seed products
        products = [
            # Appetizers
            ('Spring Rolls', 8.99, 1, '🥖'),
            ('Garlic Bread', 6.50, 1, '🧄'),
            ('Buffalo Wings', 12.99, 1, '🍗'),
            ('Mozzarella Sticks', 9.99, 1, '🧀'),
            ('Nachos', 10.99, 1, '🌮'),
            ('Calamari', 13.99, 1, '🦑'),
            
            # Mains
            ('Margherita Pizza', 15.99, 2, '🍕'),
            ('Grilled Salmon', 24.99, 2, '🐟'),
            ('Beef Steak', 28.99, 2, '🥩'),
            ('Chicken Pasta', 18.99, 2, '🍝'),
            ('Vegetarian Burger', 14.99, 2, '🍔'),
            ('Caesar Salad', 12.99, 2, '🥗'),
            
            # Desserts
            ('Chocolate Cake', 7.99, 3, '🍫'),
            ('Ice Cream', 5.99, 3, '🍨'),
            ('Tiramisu', 8.99, 3, '🍰'),
            ('Fruit Salad', 6.99, 3, '🍓'),
            
            # Drinks
            ('Coca Cola', 3.99, 4, '🥤'),
            ('Orange Juice', 4.99, 4, '🍊'),
            ('Coffee', 3.50, 4, '☕'),
            ('Tea', 2.99, 4, '🍵'),
            ('Beer', 5.99, 4, '🍺'),
            ('Wine', 8.99, 4, '🍷')
        ]
        self.cursor.executemany("INSERT INTO products (name, price, category_id, icon) VALUES (?, ?, ?, ?)", products)
        
        # Seed settings
        settings = [
            ('restaurant_name', 'DineDash Restaurant'),
            ('tax_rate', '10'),
            ('currency', '$'),
            ('license_key', 'DEMO-1234-5678-9012')
        ]
        self.cursor.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", settings)
        
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()