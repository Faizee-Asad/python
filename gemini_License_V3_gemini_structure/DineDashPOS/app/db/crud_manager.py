from .base_manager import BaseManager
import sqlite3

class CrudManager(BaseManager):
    """
    Manages all basic Create, Read, Update, and Delete (CRUD) operations
    for the database entities like users, products, and tables.
    """

    # --- Settings Methods ---
    def get_setting(self, key: str) -> str | None:
        """Gets a setting value by its key."""
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else None

    def set_setting(self, key: str, value: str):
        """Sets or updates a setting value."""
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    # --- User Methods ---
    def get_users(self) -> list:
        """Gets all users from the database."""
        self.cursor.execute("SELECT id, username, role FROM users ORDER BY role DESC, username")
        return self.cursor.fetchall()

    def get_user_by_name(self, username: str) -> sqlite3.Row | None:
        """Gets a single user by their username."""
        self.cursor.execute("SELECT id, username, role FROM users WHERE username=?", (username,))
        return self.cursor.fetchone()

    def add_user(self, username: str, role: str) -> bool:
        """Adds a new user to the database."""
        try:
            self.cursor.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError: # Handles case where username is not unique
            return False

    def delete_user(self, user_id: int):
        """Deletes a user by their ID."""
        self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()

    # --- Product Methods ---
    def get_products(self) -> list:
        """Gets all products from the database."""
        self.cursor.execute("SELECT id, name, price, category, image FROM products ORDER BY category, name")
        return self.cursor.fetchall()

    def get_product_categories(self) -> list[str]:
        """Gets all unique product categories."""
        self.cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def add_product(self, name: str, price: float, category: str, image: str = None) -> int:
        """Adds a new product and initializes its inventory."""
        self.cursor.execute(
            "INSERT INTO products (name, price, category, image) VALUES (?, ?, ?, ?)",
            (name, price, category, image)
        )
        product_id = self.cursor.lastrowid
        self.cursor.execute(
            "INSERT INTO inventory (product_id, stock_quantity, min_stock_level) VALUES (?, ?, ?)",
            (product_id, 100, 20)
        )
        self.conn.commit()
        return product_id

    def update_product(self, product_id: int, name: str, price: float, category: str):
        """Updates an existing product's details."""
        self.cursor.execute(
            "UPDATE products SET name=?, price=?, category=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (name, price, category, product_id)
        )
        self.conn.commit()

    def update_product_image(self, product_id: int, image_filename: str):
        """Updates only the image filename for a product."""
        self.cursor.execute(
            "UPDATE products SET image=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (image_filename, product_id)
        )
        self.conn.commit()

    def delete_product(self, product_id: int):
        """Deletes a product and its associated inventory record."""
        self.cursor.execute("DELETE FROM inventory WHERE product_id=?", (product_id,))
        self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    # --- Table Methods ---
    def get_all_tables_for_management(self) -> list:
        """Gets all tables with their status, intended for the settings screen."""
        self.cursor.execute('''
            SELECT t.id, t.name, t.capacity,
                   CASE WHEN o.id IS NOT NULL THEN 'occupied' ELSE 'available' END as status
            FROM tables t
            LEFT JOIN orders o ON t.id = o.table_id AND o.status = 'open'
            ORDER BY t.name
        ''')
        return self.cursor.fetchall()

    def add_table(self, name: str, capacity: int) -> bool:
        """Adds a new table to the restaurant floor plan."""
        try:
            self.cursor.execute("INSERT INTO tables (name, capacity) VALUES (?, ?)", (name, capacity))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError: # Handles case where table name is not unique
            return False

    def delete_table(self, table_id: int) -> bool:
        """Deletes a table, but only if it is not currently occupied."""
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE table_id=? AND status='open'", (table_id,))
        if self.cursor.fetchone()[0] > 0:
            return False  # Cannot delete an occupied table
        self.cursor.execute("DELETE FROM tables WHERE id=?", (table_id,))
        self.conn.commit()
        return True

    # --- Feedback Methods ---
    def add_feedback(self, order_id: int, rating: int, comment: str = None):
        """Adds customer feedback for a given order."""
        self.cursor.execute(
            "INSERT INTO feedback (order_id, rating, comment) VALUES (?, ?, ?)",
            (order_id, rating, comment)
        )
        self.conn.commit()

    def get_recent_feedback(self, limit: int = 10) -> list:
        """Gets the most recent customer feedback entries."""
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
