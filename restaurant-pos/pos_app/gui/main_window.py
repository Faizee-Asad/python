import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from pos_app.utils.constants import APP_TITLE, WINDOW_SIZE, CURRENCY
from pos_app.logic.products import ProductService
from pos_app.logic.billing import CartItem, calculate_totals, process_order
from pos_app.database.db_manager import DBManager
from pos_app.gui.admin_panel import AdminPanel


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)

        # CustomTkinter setup
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Backend
        self.products_service = ProductService()
        self.db = DBManager()
        self.cart: list[CartItem] = []

        # Build layout
        self._build_menu()
        self._build_layout()
        self._load_products()

    # ---------------- MENU ----------------
    def _build_menu(self):
        menubar = ctk.CTkMenu(self.root) if hasattr(ctk, "CTkMenu") else None
        # Fallback to Tkinter menu (CustomTkinter has no native Menu)
        import tkinter as tk
        menubar = tk.Menu(self.root)
        admin_menu = tk.Menu(menubar, tearoff=0)
        admin_menu.add_command(label="Open Admin Panel", command=self._open_admin)
        menubar.add_cascade(label="Admin", menu=admin_menu)
        self.root.config(menu=menubar)

    def _open_admin(self):
        AdminPanel(self.root)

    # ---------------- LAYOUT ----------------
    def _build_layout(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="white")
        main_frame.pack(fill="both", expand=True)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=3)  # Products area
        main_frame.grid_columnconfigure(1, weight=2)  # Cart area

        # Left: Products grid
        self.products_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.products_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Right: Cart
        self.cart_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self._build_cart_ui()

    # ---------------- PRODUCTS GRID ----------------
    def _load_products(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        products = self.products_service.list_products()

        cols = 3
        for i, row in enumerate(products):
            r, c = divmod(i, cols)
            frame = ctk.CTkFrame(self.products_frame, corner_radius=8)
            frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            # Try product image (fallback: text)
            try:
                img = Image.open(row["image_path"]).resize((80, 80))
                img = ImageTk.PhotoImage(img)
                lbl_img = ctk.CTkLabel(frame, image=img, text="")
                lbl_img.image = img
                lbl_img.pack(pady=5)
            except:
                ctk.CTkLabel(frame, text=row["name"], font=("Arial", 12, "bold")).pack()

            ctk.CTkButton(
                frame,
                text=f"{row['name']} - {CURRENCY}{row['price']:.2f}",
                command=lambda r=row: self._add_to_cart(r)
            ).pack(pady=5)

    # ---------------- CART UI ----------------
    def _build_cart_ui(self):
        ctk.CTkLabel(self.cart_frame, text="Cart", font=("Arial", 18, "bold")).pack(pady=10)

        self.cart_list = ctk.CTkTextbox(self.cart_frame, width=300, height=300)
        self.cart_list.pack(pady=10, padx=10)

        self.subtotal_var = ctk.StringVar(value=f"Subtotal: {CURRENCY} 0.00")
        self.tax_var = ctk.StringVar(value=f"Tax: {CURRENCY} 0.00")
        self.total_var = ctk.StringVar(value=f"Total: {CURRENCY} 0.00")

        ctk.CTkLabel(self.cart_frame, textvariable=self.subtotal_var).pack()
        ctk.CTkLabel(self.cart_frame, textvariable=self.tax_var).pack()
        ctk.CTkLabel(self.cart_frame, textvariable=self.total_var, font=("Arial", 14, "bold")).pack(pady=5)

        ctk.CTkButton(self.cart_frame, text="Checkout", fg_color="green", command=self._checkout).pack(pady=10)
        ctk.CTkButton(self.cart_frame, text="Clear Cart", fg_color="red", command=self._clear_cart).pack(pady=5)

    # ---------------- CART LOGIC ----------------
    def _add_to_cart(self, product):
        for item in self.cart:
            if item.product_id == product["id"]:
                item.qty += 1
                break
        else:
            self.cart.append(CartItem(product_id=product["id"], name=product["name"], price=product["price"], qty=1))
        self._refresh_cart_view()

    def _refresh_cart_view(self):
        self.cart_list.delete("0.0", "end")
        totals = calculate_totals(self.cart)

        for item in self.cart:
            self.cart_list.insert("end", f"{item.name} x{item.qty} - {CURRENCY}{item.line_total:.2f}\n")

        self.subtotal_var.set(f"Subtotal: {CURRENCY} {totals['subtotal']:.2f}")
        self.tax_var.set(f"Tax: {CURRENCY} {totals['tax']:.2f}")
        self.total_var.set(f"Total: {CURRENCY} {totals['total']:.2f}")

    def _clear_cart(self):
        self.cart.clear()
        self._refresh_cart_view()

    def _checkout(self):
        if not self.cart:
            messagebox.showinfo("Empty", "Cart is empty!")
            return

        try:
            result = process_order(self.cart, use_thermal=False)

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

        self._clear_cart()
        messagebox.showinfo("Success", f"Order #{order_id} placed!\nTotal: {CURRENCY}{result['total']:.2f}\nPDF saved at: {result['pdf']}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainWindow(root)
    root.mainloop()
