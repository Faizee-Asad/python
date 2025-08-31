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
        # Settings table for license and configuration
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Server')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Products table with image support
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL,
                image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tables management
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                capacity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Orders table with enhanced tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('open', 'closed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                total_amount REAL DEFAULT 0,
                FOREIGN KEY (table_id) REFERENCES tables(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Order items with enhanced tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_at_time REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        # Customer feedback table (new feature)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        ''')

        # Inventory tracking (new feature)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL UNIQUE,
                stock_quantity INTEGER DEFAULT 0,
                min_stock_level INTEGER DEFAULT 10,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        # Add indexes for better performance
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_table_status ON orders(table_id, status)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)')
        
        self.conn.commit()
        self.seed_initial_data()

    def seed_initial_data(self):
        """Seeds the database with some initial data if it's empty."""
        # License status
        self.cursor.execute("SELECT COUNT(*) FROM settings WHERE key='license_status'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO settings (key, value) VALUES ('license_status', 'unlicensed')")

        # Default users
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            users = [
                ('Admin', 'Admin'),
                ('Jessica', 'Server'),
                ('David', 'Server'),
                ('Maria', 'Server')
            ]
            self.cursor.executemany("INSERT INTO users (username, role) VALUES (?, ?)", users)

        # Default tables
        self.cursor.execute("SELECT COUNT(*) FROM tables")
        if self.cursor.fetchone()[0] == 0:
            tables = [
                ('T1', 2), ('T2', 4), ('T3', 4), ('T4', 6), ('T5', 2), ('T6', 4),
                ('T7', 6), ('T8', 4), ('P1', 8), ('P2', 6), ('B1', 2), ('B2', 2),
                ('VIP1', 8), ('VIP2', 10), ('BAR1', 4), ('BAR2', 4)
            ]
            self.cursor.executemany("INSERT INTO tables (name, capacity) VALUES (?, ?)", tables)

        # Sample products with categories
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            products = [
                # Appetizers
                ('Spring Rolls', 8.99, 'Appetizers'),
                ('Garlic Bread', 6.50, 'Appetizers'),
                ('Buffalo Wings', 12.99, 'Appetizers'),
                ('Nachos Supreme', 10.99, 'Appetizers'),
                ('Mozzarella Sticks', 9.99, 'Appetizers'),
                
                # Mains
                ('Margherita Pizza', 15.99, 'Mains'),
                ('Pepperoni Pizza', 17.99, 'Mains'),
                ('Grilled Salmon', 24.99, 'Mains'),
                ('Beef Burger', 16.99, 'Mains'),
                ('Chicken Alfredo', 19.99, 'Mains'),
                ('Steak & Fries', 28.99, 'Mains'),
                ('Fish & Chips', 18.99, 'Mains'),
                
                # Desserts
                ('Tiramisu', 9.50, 'Desserts'),
                ('Chocolate Cake', 8.99, 'Desserts'),
                ('Ice Cream Sundae', 7.50, 'Desserts'),
                ('Cheesecake', 9.99, 'Desserts'),
                
                # Drinks
                ('Coca-Cola', 3.50, 'Drinks'),
                ('Fresh Orange Juice', 4.50, 'Drinks'),
                ('Coffee', 2.99, 'Drinks'),
                ('Tea', 2.50, 'Drinks'),
                ('Beer', 5.99, 'Drinks'),
                ('Wine Glass', 8.99, 'Drinks')
            ]
            self.cursor.executemany("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", products)
            
            # Initialize inventory for all products
            self.cursor.execute("SELECT id FROM products")
            product_ids = self.cursor.fetchall()
            inventory_data = [(pid[0], 100, 20) for pid in product_ids]  # 100 stock, 20 minimum
            self.cursor.executemany("INSERT INTO inventory (product_id, stock_quantity, min_stock_level) VALUES (?, ?, ?)", inventory_data)
        
        self.conn.commit()

    # Settings methods
    def get_setting(self, key):
        """Get a setting value by key."""
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else None

    def set_setting(self, key, value):
        """Set a setting value."""
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    # User methods
    def get_users(self):
        """Get all users."""
        self.cursor.execute("SELECT id, username, role FROM users ORDER BY role DESC, username")
        return self.cursor.fetchall()
        
    def get_user_by_name(self, username):
        """Get user by username."""
        self.cursor.execute("SELECT id, username, role FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    # Product methods with image support
    def get_products(self):
        """Get all products with their images."""
        self.cursor.execute("SELECT id, name, price, category, image FROM products ORDER BY category, name")
        return self.cursor.fetchall()
        
    def get_product_categories(self):
        """Get all unique product categories."""
        self.cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def add_product(self, name, price, category, image=None):
        """Add a new product."""
        self.cursor.execute(
            "INSERT INTO products (name, price, category, image) VALUES (?, ?, ?, ?)", 
            (name, price, category, image)
        )
        self.conn.commit()
        product_id = self.cursor.lastrowid
        
        # Initialize inventory for new product
        self.cursor.execute(
            "INSERT INTO inventory (product_id, stock_quantity, min_stock_level) VALUES (?, ?, ?)",
            (product_id, 100, 20)
        )
        self.conn.commit()
        return product_id

    def update_product(self, product_id, name, price, category, image=None):
        """Update an existing product."""
        self.cursor.execute(
            "UPDATE products SET name=?, price=?, category=?, image=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", 
            (name, price, category, image, product_id)
        )
        self.conn.commit()

    def update_product_image(self, product_id, image_filename):
        """Update only the product image."""
        self.cursor.execute(
            "UPDATE products SET image=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", 
            (image_filename, product_id)
        )
        self.conn.commit()

    def delete_product(self, product_id):
        """Delete a product and its inventory record."""
        self.cursor.execute("DELETE FROM inventory WHERE product_id=?", (product_id,))
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    # Table methods
    def get_tables(self):
        """Get all tables with their current status."""
        self.cursor.execute('''
            SELECT t.id, t.name, t.capacity, 
                   CASE WHEN o.id IS NOT NULL THEN 'occupied' ELSE 'available' END as status
            FROM tables t
            LEFT JOIN orders o ON t.id = o.table_id AND o.status = 'open'
            ORDER BY t.name
        ''')
        return self.cursor.fetchall()
        
def get_all_tables_for_management(self):
    """Get all tables for management purposes."""
    self.cursor.execute('''
        SELECT t.id, t.name, t.capacity,
               CASE WHEN o.id IS NOT NULL THEN 'occupied' ELSE 'available' END as status
        FROM tables t
        LEFT JOIN orders o ON t.id = o.table_id AND o.status = 'open'
        ORDER BY t.name
    ''')
    return self.cursor.fetchall()

    def add_table(self, name, capacity):
        """Add a new table."""
        self.cursor.execute("INSERT INTO tables (name, capacity) VALUES (?, ?)", (name, capacity))
        self.conn.commit()

    def update_table(self, table_id, name, capacity):
        """Update an existing table."""
        self.cursor.execute("UPDATE tables SET name=?, capacity=? WHERE id=?", (name, capacity, table_id))
        self.conn.commit()

    def delete_table(self, table_id):
        """Delete a table if it has no open orders."""
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE table_id=? AND status='open'", (table_id,))
        if self.cursor.fetchone()[0] > 0:
            return False
        self.cursor.execute("DELETE FROM tables WHERE id=?", (table_id,))
        self.conn.commit()
        return True

    # Order methods
    def get_open_order_for_table(self, table_id):
        """Get the open order for a specific table."""
        self.cursor.execute("SELECT id FROM orders WHERE table_id=? AND status='open'", (table_id,))
        return self.cursor.fetchone()

    def create_order(self, table_id, user_id):
        """Create a new order."""
        self.cursor.execute(
            "INSERT INTO orders (table_id, user_id, status) VALUES (?, ?, 'open')", 
            (table_id, user_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_order_items(self, order_id):
        """Get all items for a specific order."""
        self.cursor.execute('''
            SELECT oi.id, p.id as product_id, p.name, oi.quantity, oi.price_at_time
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
            ORDER BY oi.created_at
        ''', (order_id,))
        return self.cursor.fetchall()

    def add_item_to_order(self, order_id, product_id, quantity, price):
        """Add an item to an order or update quantity if it already exists."""
        self.cursor.execute(
            "SELECT id, quantity FROM order_items WHERE order_id=? AND product_id=?", 
            (order_id, product_id)
        )
        existing_item = self.cursor.fetchone()
        
        if existing_item:
            new_quantity = existing_item['quantity'] + quantity
            self.cursor.execute(
                "UPDATE order_items SET quantity=? WHERE id=?", 
                (new_quantity, existing_item['id'])
            )
        else:
            self.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", 
                (order_id, product_id, quantity, price)
            )
        
        # Update inventory
        self.update_inventory(product_id, -quantity)
        self.conn.commit()

    def update_order_item_quantity(self, order_item_id, new_quantity):
        """Update the quantity of an order item."""
        if new_quantity > 0:
            self.cursor.execute("UPDATE order_items SET quantity=? WHERE id=?", (new_quantity, order_item_id))
        else:
            self.cursor.execute("DELETE FROM order_items WHERE id=?", (order_item_id,))
        self.conn.commit()

    def close_order(self, order_id):
        """Close an order and calculate total."""
        # Calculate total
        self.cursor.execute('''
            SELECT SUM(quantity * price_at_time) as total 
            FROM order_items WHERE order_id = ?
        ''', (order_id,))
        result = self.cursor.fetchone()
        total_amount = result['total'] if result['total'] else 0.0
        
        # Update order with total and close it
        self.cursor.execute(
            "UPDATE orders SET status='closed', closed_at=CURRENT_TIMESTAMP, total_amount=? WHERE id=?", 
            (total_amount, order_id)
        )
        self.conn.commit()

    def get_last_closed_order_for_table(self, table_id):
        """Get the most recent closed order for a table."""
        self.cursor.execute('''
            SELECT id, user_id, closed_at, total_amount FROM orders 
            WHERE table_id=? AND status='closed' 
            ORDER BY closed_at DESC LIMIT 1
        ''', (table_id,))
        return self.cursor.fetchone()

    # Inventory methods
    def get_inventory(self):
        """Get current inventory status."""
        self.cursor.execute('''
            SELECT p.name, p.category, i.stock_quantity, i.min_stock_level,
                   CASE WHEN i.stock_quantity <= i.min_stock_level THEN 1 ELSE 0 END as low_stock
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY low_stock DESC, p.name
        ''')
        return self.cursor.fetchall()

    def update_inventory(self, product_id, quantity_change):
        """Update inventory quantity (positive to add, negative to subtract)."""
        self.cursor.execute(
            "UPDATE inventory SET stock_quantity = stock_quantity + ?, last_updated = CURRENT_TIMESTAMP WHERE product_id = ?",
            (quantity_change, product_id)
        )

    def get_low_stock_products(self):
        """Get products that are low on stock."""
        self.cursor.execute('''
            SELECT p.name, p.category, i.stock_quantity, i.min_stock_level
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.stock_quantity <= i.min_stock_level
            ORDER BY i.stock_quantity
        ''')
        return self.cursor.fetchall()

    # Analytics and reporting methods
    def get_today_sales(self):
        """Get total sales for today."""
        self.cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) as today_sales
            FROM orders 
            WHERE status = 'closed' 
            AND DATE(closed_at) = DATE('now')
        ''')
        result = self.cursor.fetchone()
        return float(result['today_sales']) if result else 0.0

    def get_orders_count_today(self):
        """Get number of orders completed today."""
        self.cursor.execute('''
            SELECT COUNT(*) as count
            FROM orders 
            WHERE status = 'closed' 
            AND DATE(closed_at) = DATE('now')
        ''')
        result = self.cursor.fetchone()
        return result['count'] if result else 0

    def get_weekly_sales(self):
        """Get sales for the current week."""
        self.cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) as weekly_sales
            FROM orders 
            WHERE status = 'closed' 
            AND closed_at >= DATE('now', '-7 days')
        ''')
        result = self.cursor.fetchone()
        return float(result['weekly_sales']) if result else 0.0

    def get_monthly_sales(self):
        """Get sales for the current month."""
        self.cursor.execute('''
            SELECT COALESCE(SUM(total_amount), 0) as monthly_sales
            FROM orders 
            WHERE status = 'closed' 
            AND strftime('%Y-%m', closed_at) = strftime('%Y-%m', 'now')
        ''')
        result = self.cursor.fetchone()
        return float(result['monthly_sales']) if result else 0.0

    def get_top_selling_products(self, limit=10):
        """Get top selling products by quantity."""
        self.cursor.execute('''
            SELECT p.name, p.category, SUM(oi.quantity) as total_sold,
                   SUM(oi.quantity * oi.price_at_time) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'closed'
            GROUP BY p.id, p.name, p.category
            ORDER BY total_sold DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def get_server_performance(self):
        """Get performance statistics for each server."""
        self.cursor.execute('''
            SELECT u.username, u.role,
                   COUNT(o.id) as orders_served,
                   COALESCE(SUM(o.total_amount), 0) as total_sales,
                   COALESCE(AVG(o.total_amount), 0) as avg_order_value
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'closed'
            GROUP BY u.id, u.username, u.role
            ORDER BY total_sales DESC
        ''')
        return self.cursor.fetchall()

    def get_all_sales_data_for_export(self):
        """Get comprehensive sales data for reporting and export."""
        self.cursor.execute('''
            SELECT
                o.closed_at as timestamp,
                t.name as table_name,
                u.username as server,
                p.name as product_name,
                p.category,
                oi.quantity,
                oi.price_at_time as price
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            JOIN users u ON o.user_id = u.id
            JOIN tables t ON o.table_id = t.id
            WHERE o.status = 'closed'
            ORDER BY o.closed_at DESC
        ''')
        return self.cursor.fetchall()

    def get_hourly_sales_pattern(self):
        """Get sales patterns by hour of day."""
        self.cursor.execute('''
            SELECT 
                strftime('%H', closed_at) as hour,
                COUNT(id) as order_count,
                COALESCE(SUM(total_amount), 0) as total_sales
            FROM orders 
            WHERE status = 'closed'
            GROUP BY strftime('%H', closed_at)
            ORDER BY hour
        ''')
        return self.cursor.fetchall()

    def get_category_performance(self):
        """Get sales performance by product category."""
        self.cursor.execute('''
            SELECT 
                p.category,
                COUNT(oi.id) as items_sold,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.quantity * oi.price_at_time) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'closed'
            GROUP BY p.category
            ORDER BY total_revenue DESC
        ''')
        return self.cursor.fetchall()

    # Customer feedback methods
    def add_feedback(self, order_id, rating, comment=None):
        """Add customer feedback for an order."""
        self.cursor.execute(
            "INSERT INTO feedback (order_id, rating, comment) VALUES (?, ?, ?)",
            (order_id, rating, comment)
        )
        self.conn.commit()

    def get_average_rating(self):
        """Get the average customer rating."""
        self.cursor.execute("SELECT COALESCE(AVG(rating), 0) as avg_rating FROM feedback")
        result = self.cursor.fetchone()
        return float(result['avg_rating']) if result else 0.0

    def get_recent_feedback(self, limit=10):
        """Get recent customer feedback."""
        self.cursor.execute('''
            SELECT f.rating, f.comment, f.created_at,
                   t.name as table_name, u.username as server
            FROM feedback f
            JOIN orders o ON f.order_id = o.id
            JOIN tables t ON o.table_id = t.id
            JOIN users u ON o.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    # Database maintenance methods
    def backup_database(self, backup_path):
        """Create a backup of the database."""
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            return True
        except Exception:
            return False

    def get_database_stats(self):
        """Get basic database statistics."""
        stats = {}
        
        # Count records in each table
        tables = ['users', 'products', 'tables', 'orders', 'order_items', 'feedback', 'inventory']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = self.cursor.fetchone()
            stats[f'{table}_count'] = result['count']
        
        # Get date range of orders
        self.cursor.execute('''
            SELECT 
                MIN(created_at) as first_order,
                MAX(closed_at) as last_order
            FROM orders WHERE status = 'closed'
        ''')
        result = self.cursor.fetchone()
        stats['first_order'] = result['first_order']
        stats['last_order'] = result['last_order']
        
        return stats

    def optimize_database(self):
        """Optimize database performance."""
        self.cursor.execute("VACUUM")
        self.cursor.execute("ANALYZE")
        self.conn.commit()

    def __del__(self):
        """Close database connection when object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()