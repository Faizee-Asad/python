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
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # --- Table Definitions ---
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY, value TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff'))
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL NOT NULL,
                category TEXT NOT NULL, image TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
                capacity INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT, table_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('open', 'closed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, closed_at TIMESTAMP,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_id INTEGER,
                quantity INTEGER NOT NULL, price_at_time REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        ''')
        self.conn.commit()
        self.seed_initial_data()

    def seed_initial_data(self):
        """Seeds the database with initial data if it's empty."""
        self.cursor.execute("SELECT COUNT(*) FROM settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO settings (key, value) VALUES ('license_status', 'unlicensed')")

        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            users = [('Admin', 'Admin'), ('Jessica', 'Staff'), ('David', 'Staff'), ('Maria', 'Staff')]
            self.cursor.executemany("INSERT INTO users (username, role) VALUES (?, ?)", users)
        
        self.cursor.execute("SELECT COUNT(*) FROM tables")
        if self.cursor.fetchone()[0] == 0:
            tables = [('T1', 2), ('T2', 4), ('T3', 4), ('T4', 6), ('T5', 2), ('T6', 4),
                      ('T7', 6), ('T8', 4), ('P1', 8), ('P2', 6), ('B1', 2), ('B2', 2)]
            self.cursor.executemany("INSERT INTO tables (name, capacity) VALUES (?, ?)", tables)

        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            products = [
                ('Spring Rolls', 8.99, 'Appetizers'), ('Garlic Bread', 6.50, 'Appetizers'),
                ('Buffalo Wings', 12.99, 'Appetizers'),
                ('Margherita Pizza', 15.99, 'Mains'), ('Beef Burger', 16.99, 'Mains'),
                ('Chicken Alfredo', 19.99, 'Mains'),
                ('Tiramisu', 9.50, 'Desserts'), ('Chocolate Cake', 8.99, 'Desserts'),
                ('Coca-Cola', 3.50, 'Drinks'), ('Orange Juice', 4.50, 'Drinks')
            ]
            self.cursor.executemany("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", products)
        
        self.conn.commit()

    # --- Settings ---
    def get_setting(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else None

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()
    
    # --- Users ---
    # def get_users(self):
    #     self.cursor.execute("SELECT * FROM users ORDER BY role DESC, username")
    #     return [dict(row) for row in self.cursor.fetchall()]
    
    # def get_user_by_name(self, name):
    #     self.cursor.execute("SELECT * FROM users WHERE username=?", (name,))
    #     result = self.cursor.fetchone()
    #     return dict(result) if result else None

    # def add_user(self, username, role):
    #     try:
    #         self.cursor.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    #         self.conn.commit()
    #         return True
    #     except sqlite3.IntegrityError: return False

    # def delete_user(self, user_id):
    #     self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    #     self.conn.commit()

    def get_users(self):
        self.cursor.execute("SELECT * FROM users ORDER BY role DESC, username")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_user_by_name(self, name):
        # Case-insensitive search
        self.cursor.execute("SELECT * FROM users WHERE LOWER(username)=LOWER(?)", (name.strip(),))
        result = self.cursor.fetchone()
        return dict(result) if result else None

    def add_user(self, username, role):
        try:
            # Check if user already exists (case-insensitive)
            existing = self.get_user_by_name(username)
            if existing:
                return False, f"Username '{username}' already exists!"
            
            # Insert the new user
            self.cursor.execute("INSERT INTO users (username, role) VALUES (?, ?)", 
                            (username.strip(), role))
            self.conn.commit()
            return True, "User added successfully"
        except sqlite3.IntegrityError as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()

    # --- Tables ---
    def get_tables(self):
        self.cursor.execute('''
            SELECT t.id, t.name, t.capacity, 
                   CASE WHEN o.id IS NOT NULL THEN 'occupied' ELSE 'available' END as status
            FROM tables t LEFT JOIN orders o ON t.id = o.table_id AND o.status = 'open'
            ORDER BY t.name
        ''')
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_tables_for_management(self):
        return self.get_tables()
        
    def add_table(self, name, capacity):
        try:
            self.cursor.execute("INSERT INTO tables (name, capacity) VALUES (?, ?)", (name, capacity))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False
            
    def delete_table(self, table_id):
        self.cursor.execute("DELETE FROM tables WHERE id=?", (table_id,))
        self.conn.commit()

    # --- Products ---
    def get_products(self):
        self.cursor.execute("SELECT * FROM products ORDER BY category, name")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_product_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        return [row['category'] for row in self.cursor.fetchall()]

    def add_product(self, name, price, category):
        self.cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", (name, price, category))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_product(self, product_id, name, price, category):
        self.cursor.execute("UPDATE products SET name=?, price=?, category=? WHERE id=?", (name, price, category, product_id))
        self.conn.commit()

    def update_product_image(self, product_id, image_filename):
        self.cursor.execute("UPDATE products SET image=? WHERE id=?", (image_filename, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    # --- Orders ---
    def get_open_order_for_table(self, table_id):
        self.cursor.execute("SELECT id FROM orders WHERE table_id=? AND status='open'", (table_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None

    def create_order(self, table_id, user_id):
        self.cursor.execute("INSERT INTO orders (table_id, user_id, status) VALUES (?, ?, 'open')", (table_id, user_id))
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_order_items(self, order_id):
        self.cursor.execute('''
            SELECT oi.id, p.name as product_name, oi.quantity, oi.price_at_time
            FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?
        ''', (order_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def add_order_item(self, order_id, product_id, quantity, price):
        self.cursor.execute("SELECT id, quantity FROM order_items WHERE order_id=? AND product_id=?", (order_id, product_id))
        item = self.cursor.fetchone()
        if item:
            self.cursor.execute("UPDATE order_items SET quantity = quantity + ? WHERE id = ?", (quantity, item['id']))
        else:
            self.cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", 
                                (order_id, product_id, quantity, price))
        self.conn.commit()
    
    def remove_order_item(self, item_id):
        self.cursor.execute("DELETE FROM order_items WHERE id = ?", (item_id,))
        self.conn.commit()

    def update_order_item_quantity(self, item_id, new_quantity):
        self.cursor.execute("UPDATE order_items SET quantity=? WHERE id=?", (new_quantity, item_id))
        self.conn.commit()

    def close_order(self, order_id):
        self.cursor.execute("UPDATE orders SET status='closed', closed_at=? WHERE id=?", (datetime.now(), order_id))
        self.conn.commit()

    def get_last_closed_order_for_table(self, table_id):
        self.cursor.execute("SELECT * FROM orders WHERE table_id=? AND status='closed' ORDER BY closed_at DESC LIMIT 1", (table_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    # --- Reporting & Analytics ---
    def get_daily_sales_summary(self):
        today = datetime.now().date()
        query = '''
            SELECT 
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(oi.price_at_time * oi.quantity), 0) as total_sales
            FROM orders o JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'closed' AND DATE(o.closed_at) = ?
        '''
        summary = self.cursor.execute(query, (today,)).fetchone()
        
        category_query = '''
            SELECT p.category, SUM(oi.price_at_time * oi.quantity) as amount
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status = 'closed' AND DATE(o.closed_at) = ?
            GROUP BY p.category
        '''
        categories = self.cursor.execute(category_query, (today,)).fetchall()
        
        return {
            'total_orders': summary['total_orders'],
            'total_sales': summary['total_sales'],
            'average_order': (summary['total_sales'] / summary['total_orders']) if summary['total_orders'] > 0 else 0,
            'sales_by_category': {row['category']: row['amount'] for row in categories}
        }

    def get_sales_by_period(self, period):
        end_date = datetime.now()
        if period == "Last 7 Days": start_date = end_date - timedelta(days=6)
        elif period == "Last 30 Days": start_date = end_date - timedelta(days=29)
        elif period == "This Month": start_date = end_date.replace(day=1)
        elif period == "Last Month":
            last_month_end = end_date.replace(day=1) - timedelta(days=1)
            start_date = last_month_end.replace(day=1)
            end_date = last_month_end
        else: return {}

        query = '''
            SELECT DATE(closed_at) as date, SUM(oi.price_at_time * oi.quantity) as amount
            FROM orders o JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'closed' AND DATE(o.closed_at) BETWEEN ? AND ?
            GROUP BY DATE(closed_at) ORDER BY DATE(closed_at)
        '''
        results = self.cursor.execute(query, (start_date.date(), end_date.date())).fetchall()
        return {row['date']: row['amount'] for row in results}

    def get_top_products(self, limit=10):
        query = '''
            SELECT p.name, SUM(oi.quantity) as quantity_sold, SUM(oi.quantity * oi.price_at_time) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'closed'
            GROUP BY p.id, p.name ORDER BY revenue DESC LIMIT ?
        '''
        return [dict(row) for row in self.cursor.execute(query, (limit,)).fetchall()]

    def get_staff_performance(self):
        query = '''
            SELECT u.username, u.role,
                   COUNT(DISTINCT o.id) as total_orders,
                   COALESCE(SUM(oi.price_at_time * oi.quantity), 0) as total_sales
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'closed'
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY u.id, u.username, u.role ORDER BY total_sales DESC
        '''
        data = self.cursor.execute(query).fetchall()
        return [{
            'username': row['username'], 'role': row['role'],
            'total_orders': row['total_orders'], 'total_sales': row['total_sales'],
            'average_order': (row['total_sales'] / row['total_orders']) if row['total_orders'] > 0 else 0
        } for row in data]

    def get_order_history(self, date_filter="All Time"):
        query = '''
            SELECT o.id, o.closed_at, t.name as table_name, u.username as user_name,
                   (SELECT SUM(oi.price_at_time * oi.quantity) FROM order_items oi WHERE oi.order_id = o.id) as total
            FROM orders o
            JOIN tables t ON o.table_id = t.id
            JOIN users u ON o.user_id = u.id
            WHERE o.status = 'closed'
        '''
        params = []
        if date_filter == "Today": query += " AND DATE(o.closed_at) = DATE('now')"
        elif date_filter == "Last 7 Days": query += " AND o.closed_at >= DATE('now', '-7 days')"
        elif date_filter == "Last 30 Days": query += " AND o.closed_at >= DATE('now', '-30 days')"
        query += " ORDER BY o.closed_at DESC"
        return [dict(row) for row in self.cursor.execute(query, params).fetchall()]

    def get_live_stats(self):
        today = datetime.now().date()
        # Revenue
        self.cursor.execute("SELECT COALESCE(SUM(oi.price_at_time * oi.quantity), 0) FROM order_items oi JOIN orders o ON oi.order_id = o.id WHERE DATE(o.closed_at) = ? AND o.status = 'closed'", (today,))
        revenue = self.cursor.fetchone()[0]
        # Orders
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
        active_orders = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status='closed' AND DATE(closed_at) = ?", (today,))
        closed_orders_today = self.cursor.fetchone()[0]
        # Tables
        self.cursor.execute("SELECT COUNT(*) FROM tables")
        total_tables = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(DISTINCT table_id) FROM orders WHERE status='open'")
        occupied_tables = self.cursor.fetchone()[0]
        # Top Product
        self.cursor.execute("SELECT p.name FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN orders o ON oi.order_id = o.id WHERE DATE(o.closed_at) = ? AND o.status = 'closed' GROUP BY p.name ORDER BY SUM(oi.quantity) DESC LIMIT 1", (today,))
        top_product = self.cursor.fetchone()
        # Hourly Sales & Category Distribution
        hourly_q = "SELECT strftime('%H', closed_at) as hour, SUM(oi.price_at_time * oi.quantity) as total FROM orders o JOIN order_items oi ON o.id = oi.order_id WHERE DATE(o.closed_at) = ? AND o.status = 'closed' GROUP BY hour"
        cat_q = "SELECT p.category, SUM(oi.price_at_time * oi.quantity) as total FROM order_items oi JOIN products p ON oi.product_id = p.id JOIN orders o ON oi.order_id = o.id WHERE DATE(o.closed_at) = ? AND o.status = 'closed' GROUP BY p.category"
        
        return {
            'today_revenue': revenue, 'active_orders': active_orders,
            'total_tables': total_tables, 'occupied_tables': occupied_tables,
            'avg_order_value': (revenue / closed_orders_today) if closed_orders_today else 0,
            'top_product': top_product[0] if top_product else 'N/A',
            'active_staff': len(self.get_users()),
            'hourly_sales': {row['hour']: row['total'] for row in self.cursor.execute(hourly_q, (today,)).fetchall()},
            'category_distribution': {row['category']: row['total'] for row in self.cursor.execute(cat_q, (today,)).fetchall()}
        }

    def get_complete_order_history_for_export(self):
        query = '''
            SELECT o.id as order_id, o.closed_at, t.name as table_name, u.username as server,
                   p.name as product, p.category, oi.quantity, oi.price_at_time
            FROM orders o JOIN tables t ON o.table_id = t.id
            JOIN users u ON o.user_id = u.id JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status = 'closed' ORDER BY o.closed_at DESC
        '''
        return [dict(row) for row in self.cursor.execute(query).fetchall()]
        
    def __del__(self):
        """Ensures the database connection is closed when the object is destroyed."""
        if self.conn:
            self.conn.close()
