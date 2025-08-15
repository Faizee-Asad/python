import tkinter as tk
from tkinter import ttk, messagebox
from pos_app.utils.constants import APP_TITLE, WINDOW_SIZE, CURRENCY
from pos_app.logic.products import ProductService
from pos_app.logic.billing import CartItem, calculate_totals
from pos_app.database.db_manager import DBManager
from pos_app.gui.admin_panel import AdminPanel
from pos_app.logic.billing import CartItem, process_order



class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self._build_menu()


        self.products_service = ProductService()
        self.db = DBManager()
        self.cart: list[CartItem] = []

        self._build_layout()
        self._load_products()
    
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        admin_menu = tk.Menu(menubar, tearoff=0)
        admin_menu.add_command(label="Open Admin Panel", command=self._open_admin)
        menubar.add_cascade(label="Admin", menu=admin_menu)
        self.root.config(menu=menubar)

    def _open_admin(self):
        AdminPanel(self.root)


    # ---------------- UI ----------------
    def _build_layout(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        # Left: Products
        left = ttk.Frame(self.root, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        search_frame = ttk.Frame(left)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
        ttk.Button(search_frame, text="Go", command=self._search_products).pack(side="left")
        ttk.Button(search_frame, text="Clear", command=self._clear_search).pack(side="left", padx=(6,0))

        self.products_list = ttk.Treeview(
            left,
            columns=("id", "name", "price"),
            show="headings",
            height=18
        )
        self.products_list.heading("id", text="ID")
        self.products_list.heading("name", text="Product")
        self.products_list.heading("price", text=f"Price ({CURRENCY})")
        self.products_list.column("id", width=50, anchor="center")
        self.products_list.column("name", width=180)
        self.products_list.column("price", width=90, anchor="e")
        self.products_list.grid(row=1, column=0, sticky="nsew")

        products_btns = ttk.Frame(left)
        products_btns.grid(row=2, column=0, sticky="ew", pady=(8,0))
        ttk.Button(products_btns, text="Add to Cart", command=self._add_selected_to_cart).pack(side="left")
        ttk.Button(products_btns, text="Add Qty +1", command=lambda: self._add_selected_to_cart(qty=1)).pack(side="left", padx=6)

        # Right: Cart
        right = ttk.Frame(self.root, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.cart_view = ttk.Treeview(
            right,
            columns=("name", "qty", "price", "total"),
            show="headings",
            height=18
        )
        for col, txt, width, anchor in [
            ("name", "Item", 220, "w"),
            ("qty", "Qty", 60, "center"),
            ("price", f"Price ({CURRENCY})", 110, "e"),
            ("total", f"Total ({CURRENCY})", 110, "e"),
        ]:
            self.cart_view.heading(col, text=txt)
            self.cart_view.column(col, width=width, anchor=anchor)
        self.cart_view.grid(row=0, column=0, sticky="nsew")

        cart_btns = ttk.Frame(right)
        cart_btns.grid(row=1, column=0, sticky="ew", pady=(8,0))
        ttk.Button(cart_btns, text="Qty +", command=self._inc_qty).pack(side="left")
        ttk.Button(cart_btns, text="Qty -", command=self._dec_qty).pack(side="left", padx=6)
        ttk.Button(cart_btns, text="Remove", command=self._remove_item).pack(side="left")
        ttk.Button(cart_btns, text="Clear Cart", command=self._clear_cart).pack(side="left", padx=6)

        # Bottom: Totals + Checkout
        bottom = ttk.Frame(self.root, padding=10)
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=0)

        self.subtotal_var = tk.StringVar(value=f"{CURRENCY} 0.00")
        self.tax_var = tk.StringVar(value=f"{CURRENCY} 0.00")
        self.total_var = tk.StringVar(value=f"{CURRENCY} 0.00")

        totals = ttk.Frame(bottom)
        totals.grid(row=0, column=0, sticky="w")
        ttk.Label(totals, text="Subtotal: ").grid(row=0, column=0, sticky="w")
        ttk.Label(totals, textvariable=self.subtotal_var).grid(row=0, column=1, sticky="w", padx=(4, 12))
        ttk.Label(totals, text="Tax: ").grid(row=0, column=2, sticky="w")
        ttk.Label(totals, textvariable=self.tax_var).grid(row=0, column=3, sticky="w", padx=(4, 12))
        ttk.Label(totals, text="Total: ").grid(row=0, column=4, sticky="w")
        ttk.Label(totals, textvariable=self.total_var, font=("Arial", 11, "bold")).grid(row=0, column=5, sticky="w", padx=(4, 0))

        ttk.Button(bottom, text="Checkout", command=self._checkout).grid(row=0, column=1, sticky="e")

    # ---------------- Data ----------------
    def _load_products(self, search: str | None = None):
        for r in self.products_list.get_children():
            self.products_list.delete(r)
        rows = self.products_service.list_products(search)
        for row in rows:
            self.products_list.insert("", "end", values=(row["id"], row["name"], f"{row['price']:.2f}"))

    def _search_products(self):
        self._load_products(self.search_var.get().strip())

    def _clear_search(self):
        self.search_var.set("")
        self._load_products()

    # ---------------- Cart ops ----------------
    def _add_selected_to_cart(self, qty: int = 1):
        sel = self.products_list.selection()
        if not sel:
            messagebox.showinfo("Select Product", "Please select a product to add.")
            return
        pid, name, price_str = self.products_list.item(sel[0])["values"]
        price = float(price_str)
        # If already in cart, increase qty
        for item in self.cart:
            if item.product_id == int(pid):
                item.qty += qty
                self._refresh_cart_view()
                self._update_totals()
                return
        # Else new item
        self.cart.append(CartItem(product_id=int(pid), name=name, price=price, qty=qty))
        self._refresh_cart_view()
        self._update_totals()

    def _inc_qty(self):
        sel = self.cart_view.selection()
        if not sel:
            return
        idx = int(self.cart_view.index(sel[0]))
        self.cart[idx].qty += 1
        self._refresh_cart_view()
        self._update_totals()

    def _dec_qty(self):
        sel = self.cart_view.selection()
        if not sel:
            return
        idx = int(self.cart_view.index(sel[0]))
        self.cart[idx].qty -= 1
        if self.cart[idx].qty <= 0:
            del self.cart[idx]
        self._refresh_cart_view()
        self._update_totals()

    def _remove_item(self):
        sel = self.cart_view.selection()
        if not sel:
            return
        idx = int(self.cart_view.index(sel[0]))
        del self.cart[idx]
        self._refresh_cart_view()
        self._update_totals()

    def _clear_cart(self):
        self.cart.clear()
        self._refresh_cart_view()
        self._update_totals()

    def _refresh_cart_view(self):
        for r in self.cart_view.get_children():
            self.cart_view.delete(r)
        for item in self.cart:
            self.cart_view.insert(
                "", "end",
                values=(item.name, item.qty, f"{item.price:.2f}", f"{item.line_total:.2f}")
            )

    def _update_totals(self):
        totals = calculate_totals(self.cart)
        self.subtotal_var.set(f"{CURRENCY} {totals['subtotal']:.2f}")
        self.tax_var.set(f"{CURRENCY} {totals['tax']:.2f}")
        self.total_var.set(f"{CURRENCY} {totals['total']:.2f}")

    # ---------------- Checkout ----------------
    def _checkout(self):
        if not self.cart:
            messagebox.showinfo("Empty Cart", "No items in cart.")
            return

        try:
            # This now calculates totals, generates PDF, and optionally prints
            result = process_order(self.cart, use_thermal=False)  # set True if using thermal

            # Save order in DB
            items_payload = [
                {
                    "product_id": ci.product_id,
                    "qty": ci.qty,
                    "price": ci.price,
                    "line_total": ci.line_total,
                }
                for ci in self.cart
            ]
            order_id = self.db.create_order(total=result["total"], items=items_payload)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process order: {e}")
            return

        # Clear the cart after success
        self._clear_cart()

        # Notify user
        messagebox.showinfo(
            "Success",
            f"Order #{order_id} placed!\n"
            f"Total: {CURRENCY} {result['total']:.2f}\n"
            f"PDF saved at: {result['pdf']}"
        )
        