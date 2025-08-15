PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total REAL NOT NULL,
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    price REAL NOT NULL, -- unit price at time of sale
    line_total REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES products(id)
);

-- Default admin
INSERT OR IGNORE INTO admin (username, password) VALUES ('admin', 'admin123');

-- Seed products (insert only if table is empty)
INSERT OR IGNORE INTO products (id, name, price) VALUES
(1, 'Masala Dosa', 90.00),
(2, 'Paneer Tikka', 160.00),
(3, 'Veg Biryani', 140.00),
(4, 'Chicken Biryani', 180.00),
(5, 'Cold Coffee', 80.00),
(6, 'Masala Tea', 25.00),
(7, 'Mineral Water', 20.00);
