from .base_manager import BaseManager

class SetupManager(BaseManager):
    """
    Manages the initial setup of the database, including table creation
    and seeding of initial data.
    """
    def initialize_database(self):
        """Runs all setup and seeding operations."""
        print("[DEBUG] Initializing database...")
        self.create_tables()
        self.seed_initial_data()
        print("[DEBUG] Database initialization complete.")

    def create_tables(self):
        """Creates all necessary tables for the POS system."""
        print("[DEBUG] Creating tables...")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, role TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT, image TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tables (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, capacity INTEGER)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, table_id INTEGER, user_id INTEGER, status TEXT, total_amount REAL, created_at TIMESTAMP, closed_at TIMESTAMP)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, quantity INTEGER, price_at_time REAL)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, product_id INTEGER UNIQUE, stock_quantity INTEGER, min_stock_level INTEGER)")
        self.conn.commit()
        print("[DEBUG] Table creation step finished and COMMITTED.")

    def seed_initial_data(self):
        """Seeds the database with initial data if tables are empty."""
        print("[DEBUG] Checking if data seeding is required...")
        
        # --- CRITICAL FIX: Seed and commit tables FIRST ---
        self.cursor.execute("SELECT COUNT(*) FROM tables")
        if self.cursor.fetchone()[0] == 0:
            print("[DEBUG] Seeding default tables...")
            tables_to_seed = [
                ('T1', 2), ('T2', 4), ('T3', 4), ('T4', 6), ('T5', 2), ('T6', 4),
                ('T7', 6), ('T8', 4), ('P1', 8), ('P2', 6), ('B1', 2), ('B2', 2)
            ]
            self.cursor.executemany("INSERT INTO tables (name, capacity) VALUES (?, ?)", tables_to_seed)
            self.conn.commit() # This immediate commit is the core of the fix.
            print(f"[DEBUG] Inserted {len(tables_to_seed)} tables and COMMITTED.")

        # Seed other data
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            users = [('Admin', 'Admin'), ('Jessica', 'Server'), ('David', 'Server')]
            self.cursor.executemany("INSERT INTO users (username, role) VALUES (?, ?)", users)
        
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            products = [
                ('Spring Rolls', 8.99, 'Appetizers'), ('Garlic Bread', 6.50, 'Appetizers'),
                ('Margherita Pizza', 15.99, 'Mains'), ('Beef Burger', 16.99, 'Mains'),
                ('Tiramisu', 9.50, 'Desserts'), ('Coca-Cola', 3.50, 'Drinks')
            ]
            self.cursor.executemany("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", products)
        
        self.conn.commit() # Commit all other data
        print("[DEBUG] All remaining data seeding is complete and COMMITTED.")

