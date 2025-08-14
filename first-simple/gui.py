import tkinter as tk
from tkinter import messagebox, simpledialog
from database import Database
from logic import calculate_total
from utils import format_currency

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

class POSApp:
    def __init__(self):
        self.db = Database("data/app.db")
        self.cart = []

        self.root = tk.Tk()
        self.root.title("Restaurant POS - Demo")
        self.root.geometry("450x500")

        # Title
        tk.Label(self.root, text="Restaurant POS", font=("Arial", 16, "bold")).pack(pady=10)

        # Product List
        self.products_listbox = tk.Listbox(self.root, height=15)
        self.products_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_products()

        # Buttons
        tk.Button(self.root, text="Add to Cart", command=self.add_to_cart).pack(pady=5)
        tk.Button(self.root, text="Show Total", command=self.show_total).pack(pady=5)
        tk.Button(self.root, text="Admin Login", command=self.admin_login).pack(pady=10)

    def load_products(self):
        self.products_listbox.delete(0, tk.END)
        products = self.db.get_products()
        for p in products:
            self.products_listbox.insert(tk.END, f"{p[1]} - {format_currency(p[2])}")

    def add_to_cart(self):
        selection = self.products_listbox.curselection()
        if selection:
            index = selection[0]
            products = self.db.get_products()
            self.cart.append(products[index])
            messagebox.showinfo("Added", f"Added {products[index][1]} to cart.")
        else:
            messagebox.showwarning("No Selection", "Please select a product.")

    def show_total(self):
        total = calculate_total(self.cart)
        messagebox.showinfo("Total", f"Total Amount: {format_currency(total)}")

    def admin_login(self):
        username = simpledialog.askstring("Admin Login", "Enter username:")
        password = simpledialog.askstring("Admin Login", "Enter password:", show="*")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.open_admin_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

    def open_admin_panel(self):
        admin_win = tk.Toplevel(self.root)
        admin_win.title("Admin Panel")
        admin_win.geometry("400x400")

        tk.Label(admin_win, text="Admin Panel", font=("Arial", 14, "bold")).pack(pady=10)

        # Product List in Admin Panel
        admin_listbox = tk.Listbox(admin_win, height=10)
        admin_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        def load_admin_products():
            admin_listbox.delete(0, tk.END)
            for p in self.db.get_products():
                admin_listbox.insert(tk.END, f"{p[0]} - {p[1]} - {format_currency(p[2])}")

        def add_product():
            name = simpledialog.askstring("Add Product", "Enter product name:")
            price = simpledialog.askfloat("Add Product", "Enter product price:")
            if name and price is not None:
                self.db.add_product(name, price)
                load_admin_products()
                self.load_products()
                messagebox.showinfo("Success", "Product added successfully!")

        def edit_product():
            selection = admin_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a product to edit.")
                return
            index = selection[0]
            products = self.db.get_products()
            product_id, name, price = products[index]

            new_name = simpledialog.askstring("Edit Product", "Enter new name:", initialvalue=name)
            new_price = simpledialog.askfloat("Edit Product", "Enter new price:", initialvalue=price)

            if new_name and new_price is not None:
                self.db.update_product(product_id, new_name, new_price)
                load_admin_products()
                self.load_products()
                messagebox.showinfo("Success", "Product updated successfully!")

        def delete_product():
            selection = admin_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a product to delete.")
                return
            index = selection[0]
            products = self.db.get_products()
            product_id, _, _ = products[index]

            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?")
            if confirm:
                self.db.delete_product(product_id)
                load_admin_products()
                self.load_products()
                messagebox.showinfo("Deleted", "Product deleted successfully.")

        # Buttons for Admin
        tk.Button(admin_win, text="Add Product", command=add_product).pack(pady=5)
        tk.Button(admin_win, text="Edit Product", command=edit_product).pack(pady=5)
        tk.Button(admin_win, text="Delete Product", command=delete_product).pack(pady=5)

        load_admin_products()

    def run(self):
        self.root.mainloop()
