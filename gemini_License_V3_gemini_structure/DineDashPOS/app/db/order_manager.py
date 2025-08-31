from .base_manager import BaseManager
import sqlite3

class OrderManager(BaseManager):
    """
    Manages all complex business logic related to orders, including creation,
    item management, inventory updates, and closing transactions.
    """

    def get_tables_with_status(self) -> list:
        """Gets all tables with their current status for the main floor view."""
        self.cursor.execute('''
            SELECT t.id, t.name, t.capacity, 
                   CASE WHEN o.id IS NOT NULL THEN 'occupied' ELSE 'available' END as status
            FROM tables t
            LEFT JOIN orders o ON t.id = o.table_id AND o.status = 'open'
            ORDER BY t.name
        ''')
        return self.cursor.fetchall()

    def get_open_order_for_table(self, table_id: int) -> sqlite3.Row | None:
        """Gets the currently open order for a specific table, if one exists."""
        self.cursor.execute("SELECT id FROM orders WHERE table_id=? AND status='open'", (table_id,))
        return self.cursor.fetchone()

    def create_order(self, table_id: int, user_id: int) -> int:
        """Creates a new, empty order for a table and returns the new order ID."""
        self.cursor.execute(
            "INSERT INTO orders (table_id, user_id, status) VALUES (?, ?, 'open')", 
            (table_id, user_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_order_items(self, order_id: int) -> list:
        """Gets all items associated with a specific order."""
        self.cursor.execute('''
            SELECT oi.id, oi.product_id, p.name as product_name, oi.quantity, oi.price_at_time
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
            ORDER BY oi.created_at
        ''', (order_id,))
        return self.cursor.fetchall()

    def add_item_to_order(self, order_id: int, product_id: int, quantity: int, price: float):
        """Adds an item to an order. If the item exists, updates its quantity."""
        self.cursor.execute(
            "SELECT id, quantity FROM order_items WHERE order_id=? AND product_id=?", 
            (order_id, product_id)
        )
        existing_item = self.cursor.fetchone()
        
        if existing_item:
            new_quantity = existing_item['quantity'] + quantity
            self.update_order_item_quantity(existing_item['id'], new_quantity)
        else:
            self.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)", 
                (order_id, product_id, quantity, price)
            )
            self._update_inventory(product_id, -quantity) # Decrease stock
            self.conn.commit()

    def remove_order_item(self, order_item_id: int):
        """Removes an item from an order and returns its quantity to inventory."""
        self.cursor.execute("SELECT product_id, quantity FROM order_items WHERE id=?", (order_item_id,))
        item = self.cursor.fetchone()
        if item:
            self._update_inventory(item['product_id'], item['quantity']) # Add stock back
            self.cursor.execute("DELETE FROM order_items WHERE id=?", (order_item_id,))
            self.conn.commit()

    def update_order_item_quantity(self, order_item_id: int, new_quantity: int):
        """Updates an item's quantity and adjusts inventory accordingly."""
        self.cursor.execute("SELECT product_id, quantity FROM order_items WHERE id=?", (order_item_id,))
        item = self.cursor.fetchone()
        if not item:
            return

        quantity_change = item['quantity'] - new_quantity
        self._update_inventory(item['product_id'], quantity_change) # Adjust stock

        if new_quantity > 0:
            self.cursor.execute("UPDATE order_items SET quantity=? WHERE id=?", (new_quantity, order_item_id))
        else:
            # If new quantity is 0 or less, remove the item
            self.cursor.execute("DELETE FROM order_items WHERE id=?", (order_item_id,))
        self.conn.commit()

    def close_order(self, order_id: int):
        """Closes an order, calculating and storing the final total amount."""
        self.cursor.execute('''
            SELECT SUM(quantity * price_at_time) as total 
            FROM order_items WHERE order_id = ?
        ''', (order_id,))
        result = self.cursor.fetchone()
        total_amount = result['total'] if result and result['total'] is not None else 0.0
        
        self.cursor.execute(
            "UPDATE orders SET status='closed', closed_at=CURRENT_TIMESTAMP, total_amount=? WHERE id=?", 
            (total_amount, order_id)
        )
        self.conn.commit()

    def get_last_closed_order_for_table(self, table_id: int) -> sqlite3.Row | None:
        """Gets the most recently closed order for a table, for reprinting receipts."""
        self.cursor.execute('''
            SELECT id, user_id, closed_at, total_amount FROM orders 
            WHERE table_id=? AND status='closed' 
            ORDER BY closed_at DESC LIMIT 1
        ''', (table_id,))
        return self.cursor.fetchone()

    def _update_inventory(self, product_id: int, quantity_change: int):
        """
        Internal helper to update inventory stock for a product.
        A negative change subtracts from stock, a positive change adds to it.
        """
        self.cursor.execute(
            "UPDATE inventory SET stock_quantity = stock_quantity - ?, last_updated = CURRENT_TIMESTAMP WHERE product_id = ?",
            (quantity_change, product_id)
        )
