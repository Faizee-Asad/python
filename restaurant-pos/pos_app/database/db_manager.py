import sqlite3
from pathlib import Path
from datetime import datetime

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

    # ---------- Admin ----------
    def validate_admin(self, username, password):
        query = "SELECT 1 FROM admin WHERE username=? AND password=?"
        result = self.conn.execute(query, (username, password)).fetchone()
        return result is not None

    # ---------- Products ----------
    def get_products(self, search: str | None = None):
        if search:
            return self.conn.execute(
                "SELECT * FROM products WHERE name LIKE ? ORDER BY name ASC",
                (f"%{search}%",),
            ).fetchall()
        return self.conn.execute("SELECT * FROM products ORDER BY name ASC").fetchall()

    def add_product(self, name: str, price: float):
        self.conn.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        self.conn.commit()

    def update_product(self, product_id: int, name: str, price: float):
        self.conn.execute(
            "UPDATE products SET name=?, price=? WHERE id=?", (name, price, product_id)
        )
        self.conn.commit()

    def delete_product(self, product_id: int):
        self.conn.execute("DELETE FROM products WHERE id=?", (product_id,))
        self.conn.commit()

    # ---------- Orders ----------
    def create_order(self, total: float, items: list[dict]):
        """
        items: [{product_id:int, qty:int, price:float, line_total:float}]
        """
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO orders (total, date) VALUES (?, ?)",
            (float(total), datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        order_id = cur.lastrowid

        cur.executemany(
            """
            INSERT INTO order_items (order_id, product_id, qty, price, line_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (order_id, int(i["product_id"]), int(i["qty"]), float(i["price"]), float(i["line_total"]))
                for i in items
            ],
        )
        self.conn.commit()
        return order_id

    # ---------- Reports ----------
    def daily_sales_between(self, date_from: str, date_to: str):
        """
        Returns rows like: {'d': 'YYYY-MM-DD', 'orders': int, 'revenue': float}
        Inclusive between date_from and date_to.
        """
        sql = """
        SELECT date(date) AS d,
               COUNT(*) AS orders,
               COALESCE(SUM(total), 0) AS revenue
        FROM orders
        WHERE datetime(date) >= datetime(?) AND datetime(date) <= datetime(? || ' 23:59:59')
        GROUP BY date(date)
        ORDER BY d ASC
        """
        rows = self.conn.execute(sql, (date_from, date_to)).fetchall()
        # Convert sqlite3.Row -> dict for consistency
        return [ {"d": r["d"], "orders": r["orders"], "revenue": float(r["revenue"])} for r in rows ]

