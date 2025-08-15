import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from pos_app.logic.products import ProductService
from pos_app.database.db_manager import DBManager
from pos_app.utils.constants import CURRENCY

class AdminPanel(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Admin Panel")
        self.geometry("780x520")
        self.products = ProductService()
        self.db = DBManager()

        self._build_ui()

    def _build_ui(self):
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Products Tab ---
        self.products_tab = ttk.Frame(tabs)
        tabs.add(self.products_tab, text="Products")
        self._build_products_tab()

        # --- Sales Tab ---
        self.sales_tab = ttk.Frame(tabs)
        tabs.add(self.sales_tab, text="Sales")
        self._build_sales_tab()

    # ===================== PRODUCTS TAB =====================
    def _build_products_tab(self):
        frame = self.products_tab
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Top controls
        top = ttk.Frame(frame)
        top.grid(row=0, column=0, sticky="ew", pady=(6, 6))
        ttk.Label(top, text="Name").pack(side="left")
        self.p_name = ttk.Entry(top, width=24)
        self.p_name.pack(side="left", padx=(6, 12))
        ttk.Label(top, text=f"Price ({CURRENCY})").pack(side="left")
        self.p_price = ttk.Entry(top, width=12)
        self.p_price.pack(side="left", padx=(6, 12))

        ttk.Button(top, text="Add", command=self._add_product).pack(side="left")
        ttk.Button(top, text="Update", command=self._update_product).pack(side="left", padx=6)
        ttk.Button(top, text="Delete", command=self._delete_product).pack(side="left")

        # Table
        self.products_tv = ttk.Treeview(
            frame, columns=("id", "name", "price"), show="headings", height=16
        )
        for col, txt, w, anchor in [
            ("id", "ID", 60, "center"),
            ("name", "Product", 320, "w"),
            ("price", f"Price ({CURRENCY})", 120, "e"),
        ]:
            self.products_tv.heading(col, text=txt)
            self.products_tv.column(col, width=w, anchor=anchor)
        self.products_tv.grid(row=1, column=0, sticky="nsew")

        self.products_tv.bind("<<TreeviewSelect>>", self._on_product_select)

        # Load
        self._load_products()

    def _load_products(self):
        for r in self.products_tv.get_children():
            self.products_tv.delete(r)
        rows = self.products.list_products()
        for row in rows:
            self.products_tv.insert("", "end", values=(row["id"], row["name"], f"{row['price']:.2f}"))

    def _on_product_select(self, _evt=None):
        sel = self.products_tv.selection()
        if not sel:
            return
        pid, name, price = self.products_tv.item(sel[0])["values"]
        self.p_name.delete(0, tk.END)
        self.p_name.insert(0, name)
        self.p_price.delete(0, tk.END)
        self.p_price.insert(0, str(price))

    def _add_product(self):
        name = self.p_name.get().strip()
        price_str = self.p_price.get().strip()
        if not name or not price_str:
            messagebox.showinfo("Required", "Enter product name and price.")
            return
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Invalid", "Price must be a number.")
            return
        self.products.add(name, price)
        self._load_products()
        self.p_name.delete(0, tk.END)
        self.p_price.delete(0, tk.END)

    def _update_product(self):
        sel = self.products_tv.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a product to update.")
            return
        pid, _old_name, _old_price = self.products_tv.item(sel[0])["values"]
        name = self.p_name.get().strip()
        price_str = self.p_price.get().strip()
        if not name or not price_str:
            messagebox.showinfo("Required", "Enter product name and price.")
            return
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Invalid", "Price must be a number.")
            return
        self.products.update(int(pid), name, price)
        self._load_products()

    def _delete_product(self):
        sel = self.products_tv.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a product to delete.")
            return
        pid, name, _ = self.products_tv.item(sel[0])["values"]
        if not messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            return
        self.products.delete(int(pid))
        self._load_products()

    # ===================== SALES TAB =====================
    def _build_sales_tab(self):
        frame = self.sales_tab
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Top: Date inputs
        top = ttk.Frame(frame)
        top.grid(row=0, column=0, sticky="ew", pady=(6, 6))

        today = datetime.now().date()
        start_default = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end_default = today.strftime("%Y-%m-%d")

        ttk.Label(top, text="From (YYYY-MM-DD)").pack(side="left")
        self.start_var = tk.StringVar(value=start_default)
        ttk.Entry(top, textvariable=self.start_var, width=14).pack(side="left", padx=(6, 12))

        ttk.Label(top, text="To (YYYY-MM-DD)").pack(side="left")
        self.end_var = tk.StringVar(value=end_default)
        ttk.Entry(top, textvariable=self.end_var, width=14).pack(side="left", padx=(6, 12))

        ttk.Button(top, text="Load", command=self._load_sales).pack(side="left")

        # Table
        self.sales_tv = ttk.Treeview(
            frame, columns=("date", "orders", "revenue"), show="headings", height=16
        )
        for col, txt, w, anchor in [
            ("date", "Date", 160, "center"),
            ("orders", "Orders", 100, "center"),
            ("revenue", f"Revenue ({CURRENCY})", 160, "e"),
        ]:
            self.sales_tv.heading(col, text=txt)
            self.sales_tv.column(col, width=w, anchor=anchor)
        self.sales_tv.grid(row=1, column=0, sticky="nsew")

        # Footer totals
        footer = ttk.Frame(frame)
        footer.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(footer, text="Total Orders:").pack(side="left")
        self.total_orders_var = tk.StringVar(value="0")
        ttk.Label(footer, textvariable=self.total_orders_var).pack(side="left", padx=(4, 20))

        ttk.Label(footer, text=f"Total Revenue ({CURRENCY}):").pack(side="left")
        self.total_revenue_var = tk.StringVar(value="0.00")
        ttk.Label(footer, textvariable=self.total_revenue_var).pack(side="left", padx=(4, 0))

        # Initial
        self._load_sales()

    def _load_sales(self):
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()
        # Basic validation
        for label, val in [("From", start), ("To", end)]:
            try:
                datetime.strptime(val, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid date", f"{label} date must be YYYY-MM-DD")
                return

        rows = self.db.daily_sales_between(start, end)
        for r in self.sales_tv.get_children():
            self.sales_tv.delete(r)
        total_orders, total_revenue = 0, 0.0
        for row in rows:
            self.sales_tv.insert("", "end", values=(row["d"], row["orders"], f"{row['revenue']:.2f}"))
            total_orders += row["orders"]
            total_revenue += row["revenue"]
        self.total_orders_var.set(str(total_orders))
        self.total_revenue_var.set(f"{total_revenue:.2f}")
