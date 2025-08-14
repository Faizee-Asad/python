import tkinter as tk
from tkinter import messagebox
from database import Database
from logic import calculate_total
from utils import format_currency

class POSApp:
    def __init__(self):
        self.db = Database("data/app.db")
        self.cart = []

        self.root = tk.Tk()
        self.root.title("Restaurant POS - Demo")
        self.root.geometry("400x400")

        # Product List
        self.products_listbox = tk.Listbox(self.root)
        self.products_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_products()

        # Buttons
        tk.Button(self.root, text="Add to Cart", command=self.add_to_cart).pack(pady=5)
        tk.Button(self.root, text="Show Total", command=self.show_total).pack(pady=5)

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

    def run(self):
        self.root.mainloop()
