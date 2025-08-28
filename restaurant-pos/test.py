# Templete
# from tkinter import *

# root = Tk()
# root.title('Hello World')

# root.mainloop()

# import tkinter as tk
# from tkinter import ttk

# root = tk.Tk()
# root.title("Tico Taco POS")
# root.geometry("1200x700")

# # Sidebar
# sidebar = tk.Frame(root, bg="#2C3E50", width=200)
# sidebar.pack(side="left", fill="y")

# buttons = ["Home", "Menu", "Payments", "Receipts", "Delivery", "Back Office"]
# for b in buttons:
#     btn = tk.Button(sidebar, text=b, bg="#34495E", fg="white", bd=0, padx=20, pady=15)
#     btn.pack(fill="x", pady=5)

# # Main content
# content = tk.Frame(root, bg="#ECF0F1")
# content.pack(side="left", fill="both", expand=True)

# # Top bar
# topbar = tk.Frame(content, bg="#1ABC9C", height=50)
# topbar.pack(side="top", fill="x")
# tk.Label(topbar, text="Tico Taco Restaurant", bg="#1ABC9C", fg="white", font=("Arial", 16)).pack(side="left", padx=20)

# # Menu grid
# menu_frame = tk.Frame(content, bg="white")
# menu_frame.pack(fill="both", expand=True, padx=20, pady=20)

# for i in range(3):
#     for j in range(3):
#         item = tk.Frame(menu_frame, bg="#F8F9F9", relief="raised", bd=2)
#         item.grid(row=i, column=j, padx=20, pady=20, ipadx=40, ipady=40)
#         tk.Label(item, text="Burger", font=("Arial", 14)).pack()
#         tk.Label(item, text="$59", font=("Arial", 12), fg="green").pack()

# root.mainloop()

# import customtkinter as ctk

# ctk.set_appearance_mode("dark")  # "light" or "system"
# ctk.set_default_color_theme("blue")  # "green", "dark-blue"

# root = ctk.CTk()
# root.title("POS System")
# root.geometry("400x300")

# ctk.CTkLabel(root, text="POS Login", font=("Arial", 20)).pack(pady=20)
# username = ctk.CTkEntry(root, placeholder_text="Username")
# username.pack(pady=10)
# password = ctk.CTkEntry(root, placeholder_text="Password", show="*")
# password.pack(pady=10)
# ctk.CTkButton(root, text="Login", command=lambda: print("Login clicked")).pack(pady=20)

# root.mainloop()

# import tkinter as tk
# from ttkbootstrap import Style
# from ttkbootstrap.widgets import Entry, Button

# # Create app window
# root = tk.Tk()
# root.title("POS System")
# root.geometry("400x300")

# # Apply Bootstrap style (themes: flatly, darkly, cyborg, solar, journal, etc.)
# style = Style(theme="darkly")

# # Main frame
# frame = tk.Frame(root, bg=style.colors.bg)
# frame.pack(fill="both", expand=True, padx=20, pady=20)

# # Title
# title = tk.Label(frame, text="POS Login", font=("Arial", 20), bg=style.colors.bg, fg="white")
# title.pack(pady=20)

# # Username Entry
# username = Entry(frame, bootstyle="info", width=30)
# username.insert(0, "Username")
# username.pack(pady=10)

# # Password Entry
# password = Entry(frame, bootstyle="info", width=30, show="*")
# password.insert(0, "Password")
# password.pack(pady=10)

# # Login Button
# login_btn = Button(frame, text="Login", bootstyle="success", command=lambda: print("Login clicked"))
# login_btn.pack(pady=20)

# root.mainloop()


# old login
# import tkinter as tk from tkinter import messagebox from PIL import Image, ImageTk # pip install pillow from pos_app.database.db_manager import DBManager from pos_app.gui.main_window import MainWindow import os # Get the base directory (project root where main.py runs) BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png") class LoginWindow: def __init__(self, root): self.root = root self.root.title("Restaurant POS - Admin Login") self.root.geometry("500x400") self.root.resizable(False, False) self.root.iconbitmap("assets/icon.ico") # Colors bg_color = "#2C3E50" # dark blue-gray frame_color = "#ECF0F1" # light gray btn_color = "#27AE60" # green btn_text = "#ffffff" self.root.configure(bg=bg_color) self.db = DBManager() # ---------- Logo Section ---------- try: #img = Image.open("assets\logo.png") # Add your logo in assets folder img = img.resize((100, 100)) self.logo = ImageTk.PhotoImage(img) tk.Label(root, image=self.logo, bg=bg_color).pack(pady=15) except: tk.Label(root, text="🍽️ POS System", font=("Arial", 20, "bold"), fg="white", bg=bg_color).pack(pady=20) # ---------- Frame for Login ---------- frame = tk.Frame(root, bg=frame_color, bd=5, relief="groove") frame.pack(pady=10, padx=40, fill="both", expand=True) tk.Label(frame, text="Username", font=("Arial", 12), bg=frame_color).pack(pady=10) self.username = tk.Entry(frame, font=("Arial", 12), bd=2, relief="groove") self.username.pack(pady=5, ipadx=5, ipady=5) tk.Label(frame, text="Password", font=("Arial", 12), bg=frame_color).pack(pady=10) self.password = tk.Entry(frame, show="*", font=("Arial", 12), bd=2, relief="groove") self.password.pack(pady=5, ipadx=5, ipady=5) tk.Button(frame, text="Login", font=("Arial", 12, "bold"), bg=btn_color, fg=btn_text, activebackground="#219150", activeforeground="white", relief="flat", command=self.login).pack(pady=20, ipadx=10, ipady=5) def login(self): user = self.username.get() pwd = self.password.get() if self.db.validate_admin(user, pwd): self.root.destroy() main_root = tk.Tk() MainWindow(main_root) main_root.mainloop() else: messagebox.showerror("Error", "Invalid credentials")

# import customtkinter as ctk
# from tkinter import messagebox
# from PIL import Image, ImageTk


# class POSApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("POS System")
#         self.root.geometry("900x600")

#         ctk.set_appearance_mode("light")  # or "dark"
#         ctk.set_default_color_theme("blue")

#         # ------- MAIN LAYOUT -------
#         main_frame = ctk.CTkFrame(self.root, fg_color="white")
#         main_frame.pack(fill="both", expand=True)

#         main_frame.grid_rowconfigure(0, weight=1)
#         main_frame.grid_columnconfigure(0, weight=3)  # Products area
#         main_frame.grid_columnconfigure(1, weight=2)  # Cart area

#         # Left: Products grid
#         self.products_frame = ctk.CTkFrame(main_frame, corner_radius=10)
#         self.products_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

#         self._build_products_grid()

#         # Right: Cart + checkout
#         self.cart_frame = ctk.CTkFrame(main_frame, corner_radius=10)
#         self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

#         self._build_cart_ui()

#         # Cart data
#         self.cart = []

#     # ---------------- PRODUCTS GRID ----------------
#     def _build_products_grid(self):
#         products = [
#             ("Cinnamon Roll", "E:/GITHUB/python/restaurant-pos/assets/logo.png", 3.0),
#             ("PB Cookie", "E:/GITHUB/python/restaurant-pos/assets/logo.png", 2.5),
#             ("Carrot Cake", "E:/GITHUB/python/restaurant-pos/assets/logo.png", 4.0),
#             ("Cappuccino", "assets/cappuccino.png", 5.0),
#             ("Espresso", "assets/espresso.png", 3.5),
#             ("Oatmeal Cookie", "assets/oatmeal.png", 2.0),
#             ("Cupcake", "assets/cupcake.png", 3.0),
#             ("Hot Chocolate", "assets/hotchoco.png", 3.5),
#         ]

#         rows, cols = 4, 3
#         for i, (name, img_path, price) in enumerate(products):
#             try:
#                 img = Image.open(img_path).resize((80, 80))
#                 img = ImageTk.PhotoImage(img)
#             except:
#                 img = None

#             r, c = divmod(i, cols)
#             frame = ctk.CTkFrame(self.products_frame, corner_radius=8)
#             frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

#             if img:
#                 lbl_img = ctk.CTkLabel(frame, image=img, text="")
#                 lbl_img.image = img  # keep reference
#                 lbl_img.pack(pady=5)

#             ctk.CTkLabel(frame, text=name, font=("Arial", 12, "bold")).pack()
#             ctk.CTkButton(frame, text=f"${price:.2f}", command=lambda n=name, p=price: self.add_to_cart(n, p)).pack(pady=5)

#     # ---------------- CART UI ----------------
#     def _build_cart_ui(self):
#         ctk.CTkLabel(self.cart_frame, text="Cart", font=("Arial", 18, "bold")).pack(pady=10)

#         self.cart_list = ctk.CTkTextbox(self.cart_frame, width=300, height=300)
#         self.cart_list.pack(pady=10, padx=10)

#         self.total_var = ctk.StringVar(value="Total: $0.00")
#         ctk.CTkLabel(self.cart_frame, textvariable=self.total_var, font=("Arial", 14, "bold")).pack(pady=5)

#         ctk.CTkButton(self.cart_frame, text="Checkout", fg_color="green", command=self.checkout).pack(pady=10)
#         ctk.CTkButton(self.cart_frame, text="Clear List", fg_color="red", command=self.clear_cart).pack(pady=5)

#     # ---------------- CART LOGIC ----------------
#     def add_to_cart(self, name, price):
#         self.cart.append((name, price))
#         self.refresh_cart()

#     def refresh_cart(self):
#         self.cart_list.delete("0.0", "end")
#         total = 0
#         for item, price in self.cart:
#             self.cart_list.insert("end", f"{item} - ${price:.2f}\n")
#             total += price
#         self.total_var.set(f"Total: ${total:.2f}")

#     def clear_cart(self):
#         self.cart.clear()
#         self.refresh_cart()

#     def checkout(self):
#         if not self.cart:
#             messagebox.showinfo("Empty", "Cart is empty!")
#             return
#         total = sum(price for _, price in self.cart)
#         messagebox.showinfo("Checkout", f"Charged: ${total:.2f}")
#         self.clear_cart()


# if __name__ == "__main__":
#     root = ctk.CTk()
#     app = POSApp(root)
#     root.mainloop()

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from dataclasses import dataclass

# --- Mock Application Constants & Services (Replace with your actual imports) ---
# These are placeholders to make the script runnable.
APP_TITLE = "POS System"
WINDOW_SIZE = "1024x768"
CURRENCY = "$"
TAX_RATE = 0.0825

# # Mocking the CartItem data structure from your logic
# @dataclass
# class CartItem:
#     product_id: int
#     name: str
#     price: float
#     qty: int

#     @property
#     def line_total(self):
#         return self.price * self.qty

# # Mocking the ProductService to provide sample data
# class ProductService:
#     def list_products(self):
#         # NOTE: You must create an 'images' folder and place your product images there.
#         # The image names should match the 'image_path' values.
#         return [
#             {"id": 1, "name": "Cinnamon Roll", "price": 3.50, "image_path": "E:\GITHUB\python\restaurant-pos\assets\logo.png"},
#             {"id": 2, "name": "PB Cookie", "price": 2.25, "image_path": "images/pb_cookie.png"},
#             {"id": 3, "name": "Carrot Cake", "price": 4.00, "image_path": "images/carrot_cake.png"},
#             {"id": 4, "name": "Cappuccino", "price": 5.00, "image_path": "images/cappuccino.png"},
#             {"id": 5, "name": "Apple Biscuit", "price": 3.00, "image_path": "images/apple_biscuit.png"},
#             {"id": 6, "name": "Oatmeal Cookie", "price": 2.50, "image_path": "images/oatmeal_cookie.png"},
#             {"id": 7, "name": "Cupcake", "price": 2.75, "image_path": "images/cupcake.png"},
#             {"id": 8, "name": "Espresso", "price": 3.50, "image_path": "images/espresso.png"},
#         ]

# # Mocking the DBManager
# class DBManager:
#     def create_order(self, total, items):
#         print("--- Creating Order in DB ---")
#         print(f"Total: {total}")
#         print(f"Items: {items}")
#         return 1001 # Return a dummy order ID

# # Mocking the billing logic
# def calculate_totals(cart: list[CartItem]):
#     subtotal = sum(item.line_total for item in cart)
#     tax = subtotal * TAX_RATE
#     total = subtotal + tax
#     return {"subtotal": subtotal, "tax": tax, "total": total}

# def process_order(cart: list[CartItem], use_thermal=False):
#     totals = calculate_totals(cart)
#     # In a real app, this would generate a receipt file
#     pdf_path = "receipt.pdf" 
#     print(f"Order processed. PDF would be saved to {pdf_path}")
#     return {"total": totals["total"], "pdf": pdf_path}

# # Mocking the AdminPanel
# class AdminPanel:
#     def __init__(self, root):
#         messagebox.showinfo("Admin Panel", "Admin Panel would open here.")

# # --- Main Application Class ---
# class MainWindow:
#     def __init__(self, root):
#         self.root = root
#         self.root.title(APP_TITLE)
#         self.root.geometry(WINDOW_SIZE)

#         # CustomTkinter setup
#         ctk.set_appearance_mode("light")
#         ctk.set_default_color_theme("blue")

#         # Backend
#         self.products_service = ProductService()
#         self.db = DBManager()
#         self.cart: list[CartItem] = []

#         # Build layout
#         self._build_menu()
#         self._build_layout()
#         self._load_products()

#     # ---------------- MENU ----------------
#     def _build_menu(self):
#         # Fallback to Tkinter menu (CustomTkinter has no native Menu)
#         import tkinter as tk
#         menubar = tk.Menu(self.root)
#         admin_menu = tk.Menu(menubar, tearoff=0)
#         admin_menu.add_command(label="Open Admin Panel", command=self._open_admin)
#         menubar.add_cascade(label="Admin", menu=admin_menu)
#         self.root.config(menu=menubar)

#     def _open_admin(self):
#         AdminPanel(self.root)

#     # ---------------- LAYOUT ----------------
#     def _build_layout(self):
#         main_frame = ctk.CTkFrame(self.root, fg_color="white")
#         main_frame.pack(fill="both", expand=True)

#         main_frame.grid_rowconfigure(0, weight=1)
#         main_frame.grid_columnconfigure(0, weight=3)  # Products area
#         main_frame.grid_columnconfigure(1, weight=2)  # Cart area

#         # Left: Products grid
#         products_container = ctk.CTkFrame(main_frame, corner_radius=10)
#         products_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
#         products_container.grid_rowconfigure(0, weight=1)
#         products_container.grid_columnconfigure(0, weight=1)
        
#         self.products_frame = ctk.CTkScrollableFrame(products_container, label_text="Products")
#         self.products_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)


#         # Right: Cart
#         self.cart_frame = ctk.CTkFrame(main_frame, corner_radius=10)
#         self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

#         self._build_cart_ui()

#     # ---------------- PRODUCTS GRID ----------------
#     def _load_products(self):
#         for widget in self.products_frame.winfo_children():
#             widget.destroy()

#         products = self.products_service.list_products()

#         cols = 3
#         for i in range(cols):
#             self.products_frame.grid_columnconfigure(i, weight=1)

#         for i, row in enumerate(products):
#             r, c = divmod(i, cols)
#             frame = ctk.CTkFrame(self.products_frame, corner_radius=8)
#             frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

#             # Try product image (fallback: text)
#             try:
#                 img = Image.open(row["image_path"]).resize((80, 80))
#                 img_tk = ImageTk.PhotoImage(img)
#                 lbl_img = ctk.CTkLabel(frame, image=img_tk, text="")
#                 lbl_img.image = img_tk # Keep a reference
#                 lbl_img.pack(pady=5)
#             except Exception as e:
#                 print(f"Could not load image {row['image_path']}: {e}")
#                 ctk.CTkLabel(frame, text=row["name"], font=("Arial", 12, "bold")).pack()

#             ctk.CTkButton(
#                 frame,
#                 text=f"{row['name']} - {CURRENCY}{row['price']:.2f}",
#                 command=lambda r=row: self._add_to_cart(r)
#             ).pack(pady=5, padx=5, fill="x")

#     # ---------------- CART UI ----------------
#     def _build_cart_ui(self):
#         self.cart_frame.grid_rowconfigure(1, weight=1)
#         self.cart_frame.grid_columnconfigure(0, weight=1)

#         ctk.CTkLabel(self.cart_frame, text="Cart", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10, sticky="ew")

#         self.cart_list = ctk.CTkTextbox(self.cart_frame)
#         self.cart_list.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

#         totals_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
#         totals_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
#         totals_frame.grid_columnconfigure(0, weight=1)

#         self.subtotal_var = ctk.StringVar(value=f"Subtotal: {CURRENCY} 0.00")
#         self.tax_var = ctk.StringVar(value=f"Tax: {CURRENCY} 0.00")
#         self.total_var = ctk.StringVar(value=f"Total: {CURRENCY} 0.00")

#         ctk.CTkLabel(totals_frame, textvariable=self.subtotal_var).pack(anchor="e")
#         ctk.CTkLabel(totals_frame, textvariable=self.tax_var).pack(anchor="e")
#         ctk.CTkLabel(totals_frame, textvariable=self.total_var, font=("Arial", 14, "bold")).pack(anchor="e", pady=5)

#         button_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
#         button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
#         button_frame.grid_columnconfigure(0, weight=1)
#         button_frame.grid_columnconfigure(1, weight=1)

#         ctk.CTkButton(button_frame, text="Checkout", fg_color="green", command=self._checkout).grid(row=0, column=0, padx=5, sticky="ew")
#         ctk.CTkButton(button_frame, text="Clear Cart", fg_color="red", command=self._clear_cart).grid(row=0, column=1, padx=5, sticky="ew")

#     # ---------------- CART LOGIC ----------------
#     def _add_to_cart(self, product):
#         for item in self.cart:
#             if item.product_id == product["id"]:
#                 item.qty += 1
#                 break
#         else:
#             self.cart.append(CartItem(product_id=product["id"], name=product["name"], price=product["price"], qty=1))
#         self._refresh_cart_view()

#     def _refresh_cart_view(self):
#         self.cart_list.configure(state="normal")
#         self.cart_list.delete("0.0", "end")
#         totals = calculate_totals(self.cart)

#         for item in self.cart:
#             self.cart_list.insert("end", f"{item.name} x{item.qty} - {CURRENCY}{item.line_total:.2f}\n")

#         self.subtotal_var.set(f"Subtotal: {CURRENCY} {totals['subtotal']:.2f}")
#         self.tax_var.set(f"Tax: {CURRENCY} {totals['tax']:.2f}")
#         self.total_var.set(f"Total: {CURRENCY} {totals['total']:.2f}")
#         self.cart_list.configure(state="disabled")


#     def _clear_cart(self):
#         self.cart.clear()
#         self._refresh_cart_view()

#     def _checkout(self):
#         if not self.cart:
#             messagebox.showinfo("Empty", "Cart is empty!")
#             return

#         try:
#             result = process_order(self.cart, use_thermal=False)

#             items_payload = [
#                 {
#                     "product_id": ci.product_id,
#                     "qty": ci.qty,
#                     "price": ci.price,
#                     "line_total": ci.line_total,
#                 }
#                 for ci in self.cart
#             ]
#             order_id = self.db.create_order(total=result["total"], items=items_payload)

#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to process order: {e}")
#             return

#         self._clear_cart()
#         messagebox.showinfo("Success", f"Order #{order_id} placed!\nTotal: {CURRENCY}{result['total']:.2f}\nPDF saved at: {result['pdf']}")


# if __name__ == "__main__":
#     # Create the images directory if it doesn't exist
#     if not os.path.exists("images"):
#         os.makedirs("images")
#         print("Created 'images' directory. Please add your product images there.")

#     root = ctk.CTk()
#     app = MainWindow(root)
#     root.mainloop()


import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import requests
import threading
import json

# --- Style and Configuration ---
# Using the same color palette from the web design
class Style:
    BACKGROUND = "#0f172a"  # slate-900
    FRAME_BG = "#1e293b"    # slate-800
    TEXT = "#e2e8f0"        # slate-200
    TEXT_MUTED = "#94a3b8"  # slate-400
    ACCENT = "#14b8a6"      # teal-500
    ACCENT_HOVER = "#0d9488" # teal-600
    SUCCESS = "#10b981"     # emerald-500
    DANGER = "#ef4444"      # red-500
    DANGER_HOVER = "#dc2626" # red-600
    ADMIN = "#f43f5e"       # rose-500
    
    TITLE_FONT = ("Inter", 28, "bold")
    HEADER_FONT = ("Inter", 18, "bold")
    BODY_FONT = ("Inter", 12, "normal")
    BUTTON_FONT = ("Inter", 12, "bold")

# --- Mock Data (same as web version) ---
TABLES_DATA = [
    { "id": 1, "name": 'T1', "status": 'available', "capacity": 2 },
    { "id": 2, "name": 'T2', "status": 'occupied', "capacity": 4 },
    { "id": 3, "name": 'T3', "status": 'available', "capacity": 4 },
    { "id": 4, "name": 'T4', "status": 'available', "capacity": 6 },
    { "id": 5, "name": 'P1', "status": 'occupied', "capacity": 8, "type": 'patio' },
    { "id": 6, "name": 'T5', "status": 'available', "capacity": 2 },
    { "id": 7, "name": 'T6', "status": 'available', "capacity": 4 },
    { "id": 8, "name": 'B1', "status": 'occupied', "capacity": 2, "type": 'bar' },
    { "id": 9, "name": 'B2', "status": 'available', "capacity": 2, "type": 'bar' },
    { "id": 10, "name": 'T7', "status": 'available', "capacity": 6 },
    { "id": 11, "name": 'T8', "status": 'available', "capacity": 4 },
    { "id": 12, "name": 'P2', "status": 'available', "capacity": 4, "type": 'patio' },
]

# --- Main Application Class ---
class RestaurantPOS(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("DineDash POS")
        self.geometry("1280x720")
        self.configure(bg=Style.BACKGROUND)

        # Container for all frames/pages
        container = tk.Frame(self, bg=Style.BACKGROUND)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Create and store each page
        for F in (LoginScreen, TableScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginScreen")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        # Call a refresh method if it exists, to update data
        if hasattr(frame, "refresh"):
            frame.refresh()

# --- Login Screen ---
class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=Style.FRAME_BG)
        self.controller = controller
        
        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self, bg=Style.BACKGROUND, padx=40, pady=40)
        main_frame.grid(row=0, column=0)

        title = tk.Label(main_frame, text="Welcome Back", font=Style.TITLE_FONT, bg=Style.BACKGROUND, fg=Style.TEXT)
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(main_frame, text="Please select your user profile to continue", font=Style.BODY_FONT, bg=Style.BACKGROUND, fg=Style.TEXT_MUTED)
        subtitle.pack(pady=(0, 30))

        users_frame = tk.Frame(main_frame, bg=Style.BACKGROUND)
        users_frame.pack()

        # User Profiles
        self.create_user_button(users_frame, "Jessica", Style.ACCENT)
        self.create_user_button(users_frame, "David", Style.ACCENT)
        self.create_user_button(users_frame, "Admin", Style.ADMIN)
        
    def create_user_button(self, parent, name, color):
        # In a real app, you'd load images. Here we use colored frames as placeholders.
        user_frame = tk.Frame(parent, bg=Style.BACKGROUND)
        user_frame.pack(side="left", padx=20)

        avatar = tk.Label(user_frame, text=name[0], font=("Inter", 36, "bold"), bg=color, fg="white", width=3, height=1, relief="raised", borderwidth=2)
        avatar.pack(pady=(0, 10))

        button = tk.Button(user_frame, text=name, font=Style.BUTTON_FONT, bg=Style.FRAME_BG, fg=Style.TEXT, relief="flat",
                           command=lambda: self.login(name))
        button.pack()

    def login(self, user_name):
        print(f"Logging in as {user_name}")
        # Here you would set the current user in the controller
        # For now, just switch to the table screen
        self.controller.show_frame("TableScreen")


# --- Table Selection Screen ---
class TableScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=Style.BACKGROUND, padx=20, pady=20)
        self.controller = controller
        
        header_frame = tk.Frame(self, bg=Style.BACKGROUND)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = tk.Label(header_frame, text="Floor Plan", font=Style.TITLE_FONT, bg=Style.BACKGROUND, fg=Style.ACCENT)
        title.pack(side="left")

        # A frame to hold the grid of tables
        self.table_grid_frame = tk.Frame(self, bg=Style.BACKGROUND)
        self.table_grid_frame.pack(fill="both", expand=True)

    def refresh(self):
        # Clear existing widgets before redrawing
        for widget in self.table_grid_frame.winfo_children():
            widget.destroy()
            
        # Configure grid columns to be responsive
        num_columns = 6
        for i in range(num_columns):
            self.table_grid_frame.grid_columnconfigure(i, weight=1)

        # Create table buttons
        for i, table_data in enumerate(TABLES_DATA):
            row = i // num_columns
            col = i % num_columns
            
            is_available = table_data["status"] == 'available'
            
            bg_color = Style.FRAME_BG if is_available else "#334155" # slate-700
            fg_color = Style.TEXT
            border_color = Style.SUCCESS if is_available else Style.DANGER
            state = "normal" if is_available else "disabled"
            
            table_frame = tk.Frame(self.table_grid_frame, bg=bg_color, relief="solid", borderwidth=2, highlightbackground=border_color, highlightcolor=border_color, highlightthickness=2)
            table_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            name_label = tk.Label(table_frame, text=table_data["name"], font=Style.HEADER_FONT, bg=bg_color, fg=fg_color)
            name_label.pack(pady=(15, 5))
            
            capacity_label = tk.Label(table_frame, text=f"{table_data['capacity']} seats", font=Style.BODY_FONT, bg=bg_color, fg=Style.TEXT_MUTED)
            capacity_label.pack()
            
            status_bg = "#10b98120" # Not possible directly, use a solid color
            status_fg = Style.SUCCESS if is_available else Style.DANGER
            
            status_label = tk.Label(table_frame, text=table_data["status"].upper(), font=("Inter", 8, "bold"), bg=bg_color, fg=status_fg)
            status_label.pack(pady=(5, 15))

            if is_available:
                # Allow clicking the frame to select the table
                table_frame.bind("<Button-1>", lambda e, t=table_data['id']: self.select_table(t))
                name_label.bind("<Button-1>", lambda e, t=table_data['id']: self.select_table(t))
                capacity_label.bind("<Button-1>", lambda e, t=table_data['id']: self.select_table(t))
                status_label.bind("<Button-1>", lambda e, t=table_data['id']: self.select_table(t))


    def select_table(self, table_id):
        print(f"Table {table_id} selected.")
        # In a full app, you would switch to the OrderScreen
        # self.controller.show_frame("OrderScreen")
        # For now, we just print a message
        pass


if __name__ == "__main__":
    app = RestaurantPOS()
    app.mainloop()
