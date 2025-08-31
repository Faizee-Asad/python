import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image
from database import Database
from datetime import datetime, timedelta
import os
import hashlib
import base64

# Try to import required libraries
try: from escpos.printer import Usb
except (ImportError, ModuleNotFoundError): Usb = None
try: import openpyxl
except (ImportError, ModuleNotFoundError): openpyxl = None
try: import pandas as pd
except (ImportError, ModuleNotFoundError): pd = None
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except (ImportError, ModuleNotFoundError):
    plt = None
    FigureCanvasTkAgg = None

class Style:
    BACKGROUND = "#0d1117"; FRAME_BG = "#161b22"; CARD_BG = "#21262d"
    TEXT = "#f0f6fc"; TEXT_MUTED = "#7d8590"; ACCENT = "#238636"
    ACCENT_HOVER = "#2ea043"; SUCCESS = "#1a7f37"; DANGER = "#da3633"
    WARNING = "#fb8500"; ADMIN = "#8b5cf6"; SECONDARY = "#fd7e14"
    TITLE_FONT = ("SF Pro Display", 32, "bold"); HEADER_FONT = ("SF Pro Display", 20, "bold")
    BODY_FONT = ("SF Pro Display", 13); BUTTON_FONT = ("SF Pro Display", 12, "bold")
    SMALL_FONT = ("SF Pro Display", 11)

# --- NEW: License Management ---
class LicenseManager:
    # This secret key should be unique and kept private in your final application.
    SECRET_KEY = "DineDashPOS-Malegaon-Secret-2025"

    @staticmethod
    def generate_signature(key):
        """Generates a verifiable signature for a license key."""
        return hashlib.sha256((key + LicenseManager.SECRET_KEY).encode()).hexdigest()

    @staticmethod
    def validate_license_key(key):
        """Validates if a given license key is authentic."""
        try:
            # A valid key is a base64 encoded string of a specific phrase
            decoded_key = base64.b64decode(key).decode()
            return decoded_key == "VALID-LICENSE-FOR-DINEDASH"
        except Exception:
            return False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Iqbal Zaika")
        self.geometry("1400x900")
        self.configure(fg_color=Style.BACKGROUND)
        ctk.set_appearance_mode("dark")

        # Set app icon if available
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        self.db = Database()
        self.current_user = None
        self.current_order_id = None
        self.selected_table_id = None
        self.selected_table_name = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Add LicenseScreen to the frames
        for F in (LicenseScreen, LoginScreen, TableScreen, OrderScreen, SettingsScreen, ReportsScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.check_license()

    def check_license(self):
        """Checks the license status and shows the appropriate screen."""
        status = self.db.get_setting('license_status')
        if status == 'licensed':
            self.show_frame("LoginScreen")
        else:
            self.show_frame("LicenseScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'refresh'):
            frame.refresh()

    def get_db(self):
        return self.db

# --- NEW: License Screen ---
# class LicenseScreen(ctk.CTkFrame):
#     def __init__(self, parent, controller):
#         super().__init__(parent, fg_color=Style.FRAME_BG)
#         self.controller = controller
#         self.db = controller.get_db()

#         main_frame = ctk.CTkFrame(self, fg_color=Style.BACKGROUND)
#         main_frame.place(relx=0.5, rely=0.5, anchor="center")

#         ctk.CTkLabel(main_frame, text="Software Activation", font=Style.TITLE_FONT, text_color=Style.TEXT).pack(pady=(20, 10), padx=40)
#         ctk.CTkLabel(main_frame, text="Please enter your license key to activate the software.", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 30))

#         self.key_entry = ctk.CTkEntry(main_frame, width=400, font=Style.BODY_FONT)
#         self.key_entry.pack(pady=10, padx=20)

#         ctk.CTkButton(main_frame, text="Activate", font=Style.BUTTON_FONT, fg_color=Style.SUCCESS, command=self.activate_license).pack(pady=20)

#     def activate_license(self):
#         entered_key = self.key_entry.get()
#         if LicenseManager.validate_license_key(entered_key):
#             # If the key is valid, update the database
#             self.db.set_setting('license_status', 'licensed')
#             messagebox.showinfo("Success", "Software activated successfully!")
#             self.controller.show_frame("LoginScreen")
#         else:
#             messagebox.showerror("Activation Failed", "The license key is invalid. Please try again.")

class LicenseScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()

        # Create gradient background effect
        gradient_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=20)
        gradient_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.6)

        # Logo/Title section
        title_frame = ctk.CTkFrame(gradient_frame, fg_color="transparent")
        title_frame.pack(pady=(40, 20), padx=40, fill="x")
        
        ctk.CTkLabel(title_frame, text="Iqbal Zaika", font=("SF Pro Display", 36, "bold"), 
                     text_color=Style.ACCENT).pack()
        ctk.CTkLabel(title_frame, text="Premium POS System", font=Style.HEADER_FONT, 
                     text_color=Style.TEXT_MUTED).pack(pady=(5, 0))

        # Activation section
        activation_frame = ctk.CTkFrame(gradient_frame, fg_color="transparent")
        activation_frame.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(activation_frame, text="Software Activation Required", 
                     font=Style.HEADER_FONT, text_color=Style.TEXT).pack(pady=(0, 10))
        ctk.CTkLabel(activation_frame, text="Enter your license key to unlock all features", 
                     font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 30))

        self.key_entry = ctk.CTkEntry(activation_frame, width=350, height=40, font=Style.BODY_FONT,
                                      placeholder_text="Enter license key here...")
        self.key_entry.pack(pady=10)

        activate_btn = ctk.CTkButton(activation_frame, text="🔓 Activate License", 
                                     font=Style.BUTTON_FONT, fg_color=Style.SUCCESS,
                                     hover_color=Style.ACCENT_HOVER, height=45,
                                     command=self.activate_license)
        activate_btn.pack(pady=20)

    def activate_license(self):
        entered_key = self.key_entry.get().strip()
        if LicenseManager.validate_license_key(entered_key):
            self.db.set_setting('license_status', 'licensed')
            messagebox.showinfo("🎉 Success", "Software activated successfully!\nWelcome to DineDash POS!")
            self.controller.show_frame("LoginScreen")
        else:
            messagebox.showerror("❌ Activation Failed", "Invalid license key. Please check and try again.")


# The rest of the classes (LoginScreen, TableScreen, etc.) remain the same
# ... (all other classes from your previous main.py go here)
# class LoginScreen(ctk.CTkFrame):
#     def __init__(self, parent, controller):
#         super().__init__(parent, fg_color=Style.FRAME_BG)
#         self.controller = controller
#         self.db = controller.get_db()
#         main_frame = ctk.CTkFrame(self, fg_color=Style.BACKGROUND)
#         main_frame.place(relx=0.5, rely=0.5, anchor="center")
#         ctk.CTkLabel(main_frame, text="Welcome Back", font=Style.TITLE_FONT, text_color=Style.TEXT).pack(pady=(20, 10), padx=40)
#         ctk.CTkLabel(main_frame, text="Please select your user profile", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 30))
#         users_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
#         users_frame.pack(pady=20, padx=20, fill="x")
#         users = self.db.get_users()
#         for user in users:
#             color = Style.ADMIN if user['role'] == "Admin" else Style.ACCENT
#             user_button = ctk.CTkButton(users_frame, text=user['username'], font=Style.BUTTON_FONT, fg_color=color,
#                                         hover_color=Style.ACCENT_HOVER, command=lambda u=user: self.login(u))
#             user_button.pack(side="left", padx=10, expand=True, fill="x")
#     def login(self, user):
#         self.controller.current_user = dict(user)
#         self.controller.show_frame("TableScreen")

class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=25)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.7)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=(40, 30), padx=40, fill="x")
        
        ctk.CTkLabel(header_frame, text="Welcome to IZ POS SYSTEM", 
                     font=Style.TITLE_FONT, text_color=Style.ACCENT).pack()
        ctk.CTkLabel(header_frame, text="Select your profile to continue", 
                     font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(10, 0))
        
        # Users section
        users_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        users_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        users = self.db.get_users()
        for i, user in enumerate(users):
            color = Style.ADMIN if user['role'] == "Admin" else Style.ACCENT
            hover_color = "#a855f7" if user['role'] == "Admin" else Style.ACCENT_HOVER
            
            user_card = ctk.CTkFrame(users_frame, fg_color=Style.CARD_BG, corner_radius=15)
            user_card.pack(pady=10, fill="x", ipady=20)
            
            icon = "👑" if user['role'] == "Admin" else "👨‍🍳"
            
            user_btn = ctk.CTkButton(user_card, 
                                     text=f"{icon} {user['username']}\n{user['role']}", 
                                     font=Style.BUTTON_FONT, fg_color=color,
                                     hover_color=hover_color, height=60,
                                     command=lambda u=user: self.login(u))
            user_btn.pack(expand=True, fill="x", padx=20, pady=10)

    def login(self, user):
        self.controller.current_user = dict(user)
        self.controller.show_frame("TableScreen")

# class TableScreen(ctk.CTkFrame):
#     def __init__(self, parent, controller):
#         super().__init__(parent, fg_color=Style.BACKGROUND)
#         self.controller = controller
#         self.db = controller.get_db()
#         header = ctk.CTkFrame(self, fg_color="transparent")
#         header.pack(fill="x", padx=20, pady=20)
#         ctk.CTkLabel(header, text="Floor Plan", font=Style.TITLE_FONT, text_color=Style.ACCENT).pack(side="left")
#         self.user_label = ctk.CTkLabel(header, text="", font=Style.BODY_FONT, text_color=Style.TEXT)
#         self.user_label.pack(side="right", padx=10)
#         self.reports_button = ctk.CTkButton(header, text="Reports", command=lambda: controller.show_frame("ReportsScreen"))
#         self.settings_button = ctk.CTkButton(header, text="Settings", command=lambda: controller.show_frame("SettingsScreen"))
#         ctk.CTkButton(header, text="Logout", fg_color=Style.DANGER, hover_color=Style.DANGER, command=self.logout).pack(side="right", padx=10)
#         self.table_grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
#         self.table_grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
#     def refresh(self):
#         if self.controller.current_user:
#             user = self.controller.current_user
#             self.user_label.configure(text=f"User: {user['username']} ({user['role']})")
#             if user['role'] == 'Admin':
#                 self.reports_button.pack(side="right", padx=10)
#                 self.settings_button.pack(side="right", padx=10)
#             else:
#                 self.reports_button.pack_forget()
#                 self.settings_button.pack_forget()
#         for widget in self.table_grid_frame.winfo_children(): widget.destroy()
#         tables = self.db.get_tables()
#         num_columns = 6
#         for i, table_data in enumerate(tables):
#             row, col = divmod(i, num_columns)
#             is_available = table_data['status'] == 'available'
#             border_color = Style.SUCCESS if is_available else Style.DANGER
#             table_btn = ctk.CTkButton(self.table_grid_frame,
#                                       text=f"{table_data['name']}\n{table_data['capacity']} seats\n{table_data['status'].upper()}",
#                                       font=Style.BUTTON_FONT, border_color=border_color, border_width=2,
#                                       fg_color=Style.FRAME_BG, hover_color=Style.ACCENT_HOVER,
#                                       command=lambda t_id=table_data['id'], t_name=table_data['name']: self.select_table(t_id, t_name))
#             table_btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipady=20)
#             if not is_available:
#                 table_btn.bind("<Button-3>", lambda e, t_id=table_data['id']: self.show_reprint_menu(e, t_id))
#         for i in range(num_columns): self.table_grid_frame.grid_columnconfigure(i, weight=1)
#     def select_table(self, table_id, table_name):
#         self.controller.selected_table_id = table_id
#         self.controller.selected_table_name = table_name
#         self.controller.show_frame("OrderScreen")
#     def show_reprint_menu(self, event, table_id):
#         menu = tk.Menu(self, tearoff=0, bg=Style.FRAME_BG, fg=Style.TEXT)
#         menu.add_command(label="Reprint Last Receipt", command=lambda: self.reprint_receipt(table_id))
#         menu.tk_popup(event.x_root, event.y_root)
#     def reprint_receipt(self, table_id):
#         last_order = self.db.get_last_closed_order_for_table(table_id)
#         if not last_order:
#             messagebox.showinfo("No Receipt", "No previously closed orders found for this table.")
#             return
#         order_items = self.db.get_order_items(last_order['id'])
#         subtotal = sum(item['quantity'] * item['price_at_time'] for item in order_items)
#         tax = subtotal * 0.10
#         total = subtotal + tax
#         user = self.db.get_user_by_name(self.controller.current_user['username'])
#         receipt_details = { "items": order_items, "subtotal": subtotal, "tax": tax, "total": total, "table_name": "N/A", "user_name": user['username'] if user else 'N/A', "timestamp": last_order['closed_at'] }
#         for table in self.db.get_all_tables_for_management():
#             if table['id'] == table_id:
#                 receipt_details["table_name"] = table['name']
#                 break
#         self.controller.frames["OrderScreen"]._print_receipt_logic(receipt_details, is_reprint=True)
#         messagebox.showinfo("Reprint", "Receipt has been sent to the printer.")
#     def logout(self):
#         self.controller.current_user = None
#         self.controller.show_frame("LoginScreen")

class TableScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        
        # Header with gradient
        header = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0, height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Left side - title and stats
        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", padx=30, pady=20)
        
        ctk.CTkLabel(left_header, text="🏢 Floor Management", 
                     font=Style.TITLE_FONT, text_color=Style.ACCENT).pack(anchor="w")
        
        self.stats_label = ctk.CTkLabel(left_header, text="", 
                                        font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED)
        self.stats_label.pack(anchor="w")
        
        # Right side - user info and buttons
        right_header = ctk.CTkFrame(header, fg_color="transparent")
        right_header.pack(side="right", padx=30, pady=20)
        
        self.user_label = ctk.CTkLabel(right_header, text="", font=Style.BODY_FONT, text_color=Style.TEXT)
        self.user_label.pack(side="right", padx=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        button_frame.pack(side="right", padx=10)
        
        self.stats_button = ctk.CTkButton(button_frame, text="📊 Live Stats", 
                                          fg_color=Style.WARNING, hover_color="#e85d04",
                                          command=lambda: controller.show_frame("StatsScreen"))
        
        self.reports_button = ctk.CTkButton(button_frame, text="📈 Reports", 
                                            fg_color=Style.SECONDARY, hover_color="#fd8f30")
        
        self.settings_button = ctk.CTkButton(button_frame, text="⚙️ Settings", 
                                             fg_color=Style.ADMIN, hover_color="#a855f7")
        
        ctk.CTkButton(button_frame, text="🚪 Logout", fg_color=Style.DANGER, 
                      hover_color="#c92a2a", command=self.logout).pack(side="right", padx=5)
        
        # Tables grid with better spacing
        self.table_grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_grid_frame.pack(fill="both", expand=True, padx=30, pady=20)

    def refresh(self):
        if self.controller.current_user:
            user = self.controller.current_user
            self.user_label.configure(text=f"👤 {user['username']} ({user['role']})")
            
            if user['role'] == 'Admin':
                self.stats_button.pack(side="right", padx=5)
                self.reports_button.pack(side="right", padx=5)
                self.settings_button.pack(side="right", padx=5)
                self.reports_button.configure(command=lambda: self.controller.show_frame("ReportsScreen"))
                self.settings_button.configure(command=lambda: self.controller.show_frame("SettingsScreen"))
            else:
                self.stats_button.pack_forget()
                self.reports_button.pack_forget()
                self.settings_button.pack_forget()

        # Clear existing widgets
        for widget in self.table_grid_frame.winfo_children():
            widget.destroy()

        tables = self.db.get_tables()
        
        # Update stats
        available = sum(1 for t in tables if t['status'] == 'available')
        occupied = len(tables) - available
        self.stats_label.configure(text=f"Tables: {len(tables)} total • {available} available • {occupied} occupied")
        
        # Create table grid
        num_columns = 5
        for i, table_data in enumerate(tables):
            row, col = divmod(i, num_columns)
            is_available = table_data['status'] == 'available'
            
            # Create table card
            table_card = ctk.CTkFrame(self.table_grid_frame, fg_color=Style.CARD_BG, corner_radius=15)
            table_card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew", ipadx=10, ipady=10)
            
            # Table icon and status
            status_color = Style.SUCCESS if is_available else Style.DANGER
            status_icon = "✅" if is_available else "🔴"
            
            ctk.CTkLabel(table_card, text=f"{status_icon}", font=("Arial", 24)).pack(pady=(10, 5))
            ctk.CTkLabel(table_card, text=table_data['name'], 
                         font=Style.HEADER_FONT, text_color=Style.TEXT).pack()
            ctk.CTkLabel(table_card, text=f"{table_data['capacity']} seats", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 5))
            
            # Action button
            if is_available:
                btn_text = "💺 Take Order"
                btn_color = Style.SUCCESS
            else:
                btn_text = "👥 View Order"
                btn_color = Style.WARNING
            
            table_btn = ctk.CTkButton(table_card, text=btn_text, font=Style.BUTTON_FONT,
                                      fg_color=btn_color, hover_color=status_color,
                                      command=lambda t_id=table_data['id'], t_name=table_data['name']: self.select_table(t_id, t_name))
            table_btn.pack(pady=10, padx=10, fill="x")
            
            # Right-click menu for occupied tables
            if not is_available:
                table_btn.bind("<Button-3>", lambda e, t_id=table_data['id']: self.show_reprint_menu(e, t_id))
        
        # Configure grid weights
        for i in range(num_columns):
            self.table_grid_frame.grid_columnconfigure(i, weight=1)

    def select_table(self, table_id, table_name):
        self.controller.selected_table_id = table_id
        self.controller.selected_table_name = table_name
        self.controller.show_frame("OrderScreen")

    def show_reprint_menu(self, event, table_id):
        menu = tk.Menu(self, tearoff=0, bg=Style.CARD_BG, fg=Style.TEXT,
                       font=Style.BODY_FONT)
        menu.add_command(label="🖨️ Reprint Receipt", command=lambda: self.reprint_receipt(table_id))
        menu.tk_popup(event.x_root, event.y_root)

    def reprint_receipt(self, table_id):
        last_order = self.db.get_last_closed_order_for_table(table_id)
        if not last_order:
            messagebox.showinfo("ℹ️ No Receipt", "No previous orders found for this table.")
            return
        
        order_items = self.db.get_order_items(last_order['id'])
        subtotal = sum(item['quantity'] * item['price_at_time'] for item in order_items)
        tax = subtotal * 0.10
        total = subtotal + tax
        user = self.db.get_user_by_name(self.controller.current_user['username'])
        
        receipt_details = {
            "items": order_items, "subtotal": subtotal, "tax": tax, "total": total,
            "table_name": "N/A", "user_name": user['username'] if user else 'N/A',
            "timestamp": last_order['closed_at']
        }
        
        for table in self.db.get_all_tables_for_management():
            if table['id'] == table_id:
                receipt_details["table_name"] = table['name']
                break
        
        self.controller.frames["OrderScreen"]._print_receipt_logic(receipt_details, is_reprint=True)
        messagebox.showinfo("✅ Success", "Receipt sent to printer successfully!")

    def logout(self):
        if messagebox.askyesno("🚪 Logout", "Are you sure you want to logout?"):
            self.controller.current_user = None
            self.controller.show_frame("LoginScreen")


class OrderScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        self.current_category = None
        self.current_order_details = {}
        self.grid_columnconfigure(0, weight=2); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        menu_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0)
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.grid_rowconfigure(2, weight=1); menu_frame.grid_columnconfigure(0, weight=1)
        menu_header = ctk.CTkFrame(menu_frame, fg_color="transparent")
        menu_header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkButton(menu_header, text="< Back to Tables", command=lambda: controller.show_frame("TableScreen")).pack(side="left")
        self.table_label = ctk.CTkLabel(menu_header, text="Table: -", font=Style.HEADER_FONT)
        self.table_label.pack(side="right")
        self.category_frame = ctk.CTkScrollableFrame(menu_frame, fg_color="transparent", orientation="horizontal", height=50)
        self.category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.menu_items_frame = ctk.CTkScrollableFrame(menu_frame, fg_color=Style.BACKGROUND)
        self.menu_items_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        order_frame = ctk.CTkFrame(self, fg_color=Style.BACKGROUND, corner_radius=0)
        order_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        order_frame.grid_rowconfigure(1, weight=1); order_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(order_frame, text="Current Order", font=Style.HEADER_FONT).grid(row=0, column=0, pady=20)
        self.order_items_frame = ctk.CTkScrollableFrame(order_frame, fg_color=Style.FRAME_BG)
        self.order_items_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        self.totals_frame = ctk.CTkFrame(order_frame, fg_color="transparent")
        self.totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.totals_frame.grid_columnconfigure(1, weight=1)
        self.subtotal_label = self.create_total_row(self.totals_frame, 0, "Subtotal")
        self.tax_label = self.create_total_row(self.totals_frame, 1, "Tax (10%)")
        self.total_label = self.create_total_row(self.totals_frame, 2, "Total", Style.HEADER_FONT)
        self.settle_button = ctk.CTkButton(self.totals_frame, text="Settle & Pay", font=Style.BUTTON_FONT, fg_color=Style.ACCENT, command=self.settle_order)
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(10,0))
        self.print_button = ctk.CTkButton(self.totals_frame, text="Print Receipt", font=Style.BUTTON_FONT, fg_color=Style.SUCCESS, command=self.print_last_receipt)
    def create_total_row(self, parent, row, text, font=Style.BODY_FONT):
        ctk.CTkLabel(parent, text=text, font=font).grid(row=row, column=0, sticky="w", pady=2)
        label = ctk.CTkLabel(parent, text="$0.00", font=font)
        label.grid(row=row, column=1, sticky="e", pady=2)
        return label
    def refresh(self):
        if not self.controller.selected_table_id: return
        self.table_label.configure(text=f"Table: {self.controller.selected_table_name}")
        order = self.db.get_open_order_for_table(self.controller.selected_table_id)
        if order: self.controller.current_order_id = order['id']
        else: self.controller.current_order_id = self.db.create_order(self.controller.selected_table_id, self.controller.current_user['id'])
        self._set_pre_payment_state()
        self.load_categories()
        self.load_order_items(is_editable=True)
    def load_categories(self, is_enabled=True):
        for widget in self.category_frame.winfo_children(): widget.destroy()
        categories = self.db.get_product_categories()
        if categories:
            self.current_category = categories[0]
            for category in categories:
                btn = ctk.CTkButton(self.category_frame, text=category, command=lambda c=category: self.set_category(c))
                btn.pack(side="left", padx=5)
                if not is_enabled: btn.configure(state="disabled")
            self.load_menu_items(is_enabled=is_enabled)
    def set_category(self, category):
        self.current_category = category
        self.load_menu_items()
    def load_menu_items(self, is_enabled=True):
        for widget in self.menu_items_frame.winfo_children(): widget.destroy()
        products = [p for p in self.db.get_products() if p['category'] == self.current_category]
        num_columns = 3
        for i, product in enumerate(products):
            row, col = divmod(i, num_columns)
            btn = ctk.CTkButton(self.menu_items_frame, text=f"{product['name']}\n${product['price']:.2f}",
                                fg_color=Style.FRAME_BG, hover_color=Style.ACCENT_HOVER,
                                command=lambda p=product: self.add_to_order(p))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew", ipady=15)
            if not is_enabled: btn.configure(state="disabled")
        for i in range(num_columns): self.menu_items_frame.grid_columnconfigure(i, weight=1)
    def add_to_order(self, product):
        self.db.add_item_to_order(self.controller.current_order_id, product['id'], 1, product['price'])
        self.load_order_items(is_editable=True)
    def load_order_items(self, is_editable):
        for widget in self.order_items_frame.winfo_children(): widget.destroy()
        items = self.db.get_order_items(self.controller.current_order_id)
        subtotal = 0
        if not items: ctk.CTkLabel(self.order_items_frame, text="No items added yet.", text_color=Style.TEXT_MUTED).pack(pady=20)
        for item in items:
            item_total = item['quantity'] * item['price_at_time']
            subtotal += item_total
            item_frame = ctk.CTkFrame(self.order_items_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=5)
            item_frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(item_frame, text=f"{item['name']}\n${item['price_at_time']:.2f} each", justify="left").grid(row=0, column=0, rowspan=2, sticky="w")
            qty_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            qty_frame.grid(row=0, column=1, rowspan=2)
            minus_btn = ctk.CTkButton(qty_frame, text="-", width=30, command=lambda oi_id=item['id'], q=item['quantity']: self.update_quantity(oi_id, q - 1))
            minus_btn.pack(side="left")
            ctk.CTkLabel(qty_frame, text=str(item['quantity']), width=30).pack(side="left")
            plus_btn = ctk.CTkButton(qty_frame, text="+", width=30, command=lambda oi_id=item['id'], q=item['quantity']: self.update_quantity(oi_id, q + 1))
            plus_btn.pack(side="left")
            if not is_editable: minus_btn.configure(state="disabled"); plus_btn.configure(state="disabled")
            ctk.CTkLabel(item_frame, text=f"${item_total:.2f}", font=Style.BUTTON_FONT).grid(row=0, column=2, rowspan=2, sticky="e", padx=10)
        tax = subtotal * 0.10
        total = subtotal + tax
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.tax_label.configure(text=f"${tax:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        self.current_order_details = {"items": items, "subtotal": subtotal, "tax": tax, "total": total, "table_name": self.controller.selected_table_name, "user_name": self.controller.current_user['username'], "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    def update_quantity(self, order_item_id, new_quantity):
        self.db.update_order_item_quantity(order_item_id, new_quantity)
        self.load_order_items(is_editable=True)
    def settle_order(self):
        if not self.current_order_details.get("items"):
            messagebox.showwarning("Empty Order", "Cannot settle an empty order.")
            return
        if messagebox.askyesno("Confirm Payment", "Has payment been received? This will close the order."):
            self.db.close_order(self.controller.current_order_id)
            messagebox.showinfo("Success", "Order has been settled. You can now print the receipt.")
            self._set_post_payment_state()
    def _set_post_payment_state(self):
        self.settle_button.grid_forget()
        self.print_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(10,0))
        self.load_order_items(is_editable=False)
        self.load_categories(is_enabled=False)
        self.load_menu_items(is_enabled=False)
    def _set_pre_payment_state(self):
        self.print_button.grid_forget()
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(10,0))
    def print_last_receipt(self):
        self._print_receipt_logic(self.current_order_details)
    def _print_receipt_logic(self, details, is_reprint=False):
        if Usb is None:
            messagebox.showerror("Printing Error", "Printing library 'python-escpos' is not installed.")
            return
        try:
            p = Usb(0x04b8, 0x0e28, 0)
            p.set(align='center', font='a', bold=True, width=2, height=2); p.text("DineDash\n")
            if is_reprint: p.text("** REPRINT **\n")
            p.set(align='center', font='b', bold=False, width=1, height=1)
            p.text(f"Date: {details['timestamp']}\n"); p.text(f"Server: {details['user_name']}\n"); p.text(f"Table: {details['table_name']}\n")
            p.text("--------------------------------\n")
            p.set(align='left')
            for item in details['items']:
                item_total = f"${(item['quantity'] * item['price_at_time']):.2f}"
                line = f"{item['quantity']}x {item['name'][:18]:<18} {item_total:>7}\n"; p.text(line)
            p.text("--------------------------------\n")
            p.set(align='right')
            p.text(f"Subtotal: ${details['subtotal']:.2f}\n"); p.text(f"Tax (10%): ${details['tax']:.2f}\n")
            p.set(bold=True, height=2); p.text(f"Total: ${details['total']:.2f}\n\n")
            p.set(align='center', font='b'); p.text("Thank you for dining with us!\n"); p.cut()
        except Exception as e:
            messagebox.showerror("Printing Error", f"Could not print to POS machine.\nError: {e}")

# class OrderScreen(ctk.CTkFrame):
#     def __init__(self, parent, controller):
#         super().__init__(parent, fg_color=Style.BACKGROUND)
#         self.controller = controller
#         self.db = controller.get_db()
#         self.current_category = None
#         self.current_order_details = {}
        
#         # Configure grid
#         self.grid_columnconfigure(0, weight=2)
#         self.grid_columnconfigure(1, weight=1)
#         self.grid_rowconfigure(0, weight=1)
        
#         # Left panel - Menu
#         menu_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0)
#         menu_frame.grid(row=0, column=0, sticky="nsew")
#         menu_frame.grid_rowconfigure(2, weight=1)
#         menu_frame.grid_columnconfigure(0, weight=1)
        
#         # Menu header
#         menu_header = ctk.CTkFrame(menu_frame, fg_color="transparent", height=60)
#         menu_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
#         menu_header.pack_propagate(False)
        
#         ctk.CTkButton(menu_header, text="← Back to Tables", 
#                       font=Style.BUTTON_FONT, fg_color=Style.SECONDARY,
#                       command=lambda: controller.show_frame("TableScreen")).pack(side="left")
        
#         self.table_label = ctk.CTkLabel(menu_header, text="", font=Style.HEADER_FONT, text_color=Style.ACCENT)
#         self.table_label.pack(side="right")
        
#         # Category tabs
#         self.category_frame = ctk.CTkScrollableFrame(menu_frame, fg_color="transparent", 
#                                                      orientation="horizontal", height=60)
#         self.category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
#         # Menu items grid
#         self.menu_items_frame = ctk.CTkScrollableFrame(menu_frame, fg_color=Style.BACKGROUND)
#         self.menu_items_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
#         # Right panel - Order
#         order_frame = ctk.CTkFrame(self, fg_color=Style.CARD_BG, corner_radius=0)
#         order_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
#         order_frame.grid_rowconfigure(1, weight=1)
#         order_frame.grid_columnconfigure(0, weight=1)
        
#         # Order header
#         order_header = ctk.CTkFrame(order_frame, fg_color="transparent", height=60)
#         order_header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
#         order_header.pack_propagate(False)
        
#         ctk.CTkLabel(order_header, text="🛒 Current Order", font=Style.HEADER_FONT, 
#                      text_color=Style.TEXT).pack()
        
#         # Order items
#         self.order_items_frame = ctk.CTkScrollableFrame(order_frame, fg_color=Style.FRAME_BG)
#         self.order_items_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
#         # Totals and actions
#         self.totals_frame = ctk.CTkFrame(order_frame, fg_color="transparent")
#         self.totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
#         self.totals_frame.grid_columnconfigure(1, weight=1)
        
#         self.subtotal_label = self.create_total_row(self.totals_frame, 0, "Subtotal")
#         self.tax_label = self.create_total_row(self.totals_frame, 1, "Tax (10%)")
#         self.total_label = self.create_total_row(self.totals_frame, 2, "💰 Total", Style.HEADER_FONT)
        
#         # Action buttons
#         self.settle_button = ctk.CTkButton(self.totals_frame, text="💳 Settle & Pay", 
#                                            font=Style.BUTTON_FONT, fg_color=Style.SUCCESS,
#                                            height=50, command=self.settle_order)
#         self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        
#         self.print_button = ctk.CTkButton(self.totals_frame, text="🖨️ Print Receipt", 
#                                           font=Style.BUTTON_FONT, fg_color=Style.ACCENT,
#                                           height=50, command=self.print_last_receipt)

#     def create_total_row(self, parent, row, text, font=Style.BODY_FONT):
#         ctk.CTkLabel(parent, text=text, font=font, text_color=Style.TEXT).grid(
#             row=row, column=0, sticky="w", pady=5)
#         label = ctk.CTkLabel(parent, text="$0.00", font=font, text_color=Style.TEXT)
#         label.grid(row=row, column=1, sticky="e", pady=5)
#         return label

#     def refresh(self):
#         if not self.controller.selected_table_id:
#             return
        
#         self.table_label.configure(text=f"🍽️ {self.controller.selected_table_name}")
        
#         order = self.db.get_open_order_for_table(self.controller.selected_table_id)
#         if order:
#             self.controller.current_order_id = order['id']
#         else:
#             self.controller.current_order_id = self.db.create_order(
#                 self.controller.selected_table_id, self.controller.current_user['id'])
        
#         self._set_pre_payment_state()
#         self.load_categories()
#         self.load_order_items(is_editable=True)

#     def load_categories(self, is_enabled=True):
#         for widget in self.category_frame.winfo_children():
#             widget.destroy()
        
#         categories = self.db.get_product_categories()
#         if categories:
#             self.current_category = categories[0]
            
#             for i, category in enumerate(categories):
#                 # Category icons
#                 icons = {"Appetizers": "🥗", "Mains": "🍽️", "Desserts": "🍰", "Drinks": "🥤"}
#                 icon = icons.get(category, "🍴")
                
#                 btn = ctk.CTkButton(self.category_frame, text=f"{icon} {category}",
#                                     font=Style.BUTTON_FONT, fg_color=Style.ACCENT if category == self.current_category else Style.FRAME_BG,
#                                     command=lambda c=category: self.set_category(c))
#                 btn.pack(side="left", padx=8, pady=5)
                
#                 if not is_enabled:
#                     btn.configure(state="disabled")
            
#             self.load_menu_items(is_enabled=is_enabled)

#     def set_category(self, category):
#         self.current_category = category
#         self.load_categories()
#         self.load_menu_items()

#     def load_menu_items(self, is_enabled=True):
#         for widget in self.menu_items_frame.winfo_children():
#             widget.destroy()
        
#         products = [p for p in self.db.get_products() if p['category'] == self.current_category]
#         num_columns = 3
        
#         for i, product in enumerate(products):
#             row, col = divmod(i, num_columns)
            
#             # Product card
#             product_card = ctk.CTkFrame(self.menu_items_frame, fg_color=Style.CARD_BG, corner_radius=15)
#             product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=10)
            
#             # Product image
#             try:
#                 product_image = ImageManager.get_product_image(product.get('image'), (120, 120))
#                 if product_image:
#                     image_label = ctk.CTkLabel(product_card, image=product_image, text="")
#                     image_label.pack(pady=(10, 5))
#                     # Keep reference to prevent garbage collection
#                     image_label.image = product_image
#             except Exception:
#                 pass
            
#             # Product info
#             ctk.CTkLabel(product_card, text=product['name'], font=Style.BUTTON_FONT, 
#                          text_color=Style.TEXT).pack(pady=(5, 2))
#             ctk.CTkLabel(product_card, text=f"${product['price']:.2f}", 
#                          font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=(0, 10))
            
#             # Add button
#             add_btn = ctk.CTkButton(product_card, text="+ Add to Order",
#                                     fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
#                                     command=lambda p=product: self.add_to_order(p))
#             add_btn.pack(pady=(0, 10), padx=10, fill="x")
#             if not is_enabled:
#                 add_btn.configure(state="disabled")
        
#         # Configure grid weights
#         for i in range(num_columns):
#             self.menu_items_frame.grid_columnconfigure(i, weight=1)

#     def add_to_order(self, product):
#         if not self.controller.current_order_id:
#             return
        
#         self.db.add_order_item(self.controller.current_order_id, product['id'], 1, product['price'])
#         self.load_order_items(is_editable=True)

#     def load_order_items(self, is_editable=True):
#         for widget in self.order_items_frame.winfo_children():
#             widget.destroy()
        
#         if not self.controller.current_order_id:
#             return
        
#         order_items = self.db.get_order_items(self.controller.current_order_id)
        
#         if not order_items:
#             ctk.CTkLabel(self.order_items_frame, text="No items in order", 
#                          font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
        
#         subtotal = 0
#         for item in order_items:
#             item_frame = ctk.CTkFrame(self.order_items_frame, fg_color=Style.BACKGROUND, corner_radius=10)
#             item_frame.pack(fill="x", pady=5, padx=5)
            
#             # Item details
#             details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
#             details_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
#             ctk.CTkLabel(details_frame, text=item['product_name'], 
#                          font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
#             ctk.CTkLabel(details_frame, text=f"${item['price_at_time']:.2f} × {item['quantity']} = ${item['price_at_time'] * item['quantity']:.2f}", 
#                          font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
#             # Quantity controls
#             if is_editable:
#                 controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
#                 controls_frame.pack(side="right", padx=10)
                
#                 ctk.CTkButton(controls_frame, text="-", width=30, height=30,
#                               fg_color=Style.DANGER, hover_color="#c92a2a",
#                               command=lambda i=item: self.update_quantity(i, -1)).pack(side="left", padx=2)
                
#                 qty_label = ctk.CTkLabel(controls_frame, text=str(item['quantity']), 
#                                          font=Style.BUTTON_FONT, text_color=Style.TEXT)
#                 qty_label.pack(side="left", padx=10)
                
#                 ctk.CTkButton(controls_frame, text="+", width=30, height=30,
#                               fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
#                               command=lambda i=item: self.update_quantity(i, 1)).pack(side="left", padx=2)
            
#             subtotal += item['price_at_time'] * item['quantity']
        
#         # Update totals
#         tax = subtotal * 0.10
#         total = subtotal + tax
        
#         self.subtotal_label.configure(text=f"${subtotal:.2f}")
#         self.tax_label.configure(text=f"${tax:.2f}")
#         self.total_label.configure(text=f"${total:.2f}")
        
#         # Store for later use
#         self.current_order_details = {
#             "items": order_items,
#             "subtotal": subtotal,
#             "tax": tax,
#             "total": total
#         }

#     def update_quantity(self, item, delta):
#         new_quantity = item['quantity'] + delta
#         if new_quantity <= 0:
#             self.db.remove_order_item(item['id'])
#         else:
#             self.db.update_order_item_quantity(item['id'], new_quantity)
#         self.load_order_items(is_editable=True)

#     def settle_order(self):
#         if not self.controller.current_order_id:
#             return
        
#         order_items = self.db.get_order_items(self.controller.current_order_id)
#         if not order_items:
#             messagebox.showwarning("⚠️ Empty Order", "Cannot settle an empty order.")
#             return
        
#         if messagebox.askyesno("💳 Confirm Payment", "Has the customer paid for this order?"):
#             # Close the order
#             self.db.close_order(self.controller.current_order_id)
            
#             # Print receipt
#             self.print_receipt()
            
#             # Update UI
#             self._set_post_payment_state()
#             messagebox.showinfo("✅ Success", "Order settled successfully!")

#     def _set_pre_payment_state(self):
#         self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
#         self.print_button.grid_forget()

#     def _set_post_payment_state(self):
#         self.settle_button.grid_forget()
#         self.print_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
#         self.load_categories(is_enabled=False)
#         self.load_order_items(is_editable=False)

#     def print_receipt(self):
#         receipt_details = self.current_order_details.copy()
#         receipt_details["table_name"] = self.controller.selected_table_name
#         receipt_details["user_name"] = self.controller.current_user['username']
#         receipt_details["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         self._print_receipt_logic(receipt_details)

#     def print_last_receipt(self):
#         if self.controller.selected_table_id:
#             last_order = self.db.get_last_closed_order_for_table(self.controller.selected_table_id)
#             if last_order:
#                 order_items = self.db.get_order_items(last_order['id'])
#                 subtotal = sum(item['quantity'] * item['price_at_time'] for item in order_items)
#                 tax = subtotal * 0.10
#                 total = subtotal + tax
                
#                 receipt_details = {
#                     "items": order_items,
#                     "subtotal": subtotal,
#                     "tax": tax,
#                     "total": total,
#                     "table_name": self.controller.selected_table_name,
#                     "user_name": self.controller.current_user['username'],
#                     "timestamp": last_order['closed_at']
#                 }
                
#                 self._print_receipt_logic(receipt_details, is_reprint=True)

#     def _print_receipt_logic(self, receipt_details, is_reprint=False):
#         # Create receipt text
#         receipt_text = self._format_receipt(receipt_details, is_reprint)
        
#         # Try to print to thermal printer
#         if Usb:
#             try:
#                 # Common USB printer vendor/product IDs
#                 printer = Usb(0x04b8, 0x0202)  # Epson TM-T88
#                 printer.text(receipt_text)
#                 printer.cut()
#                 return
#             except:
#                 pass
        
#         # Fallback: Save to file
#         try:
#             receipts_dir = os.path.join(os.path.expanduser("~"), "DineDashPOS", "receipts")
#             os.makedirs(receipts_dir, exist_ok=True)
            
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"receipt_{timestamp}.txt"
#             filepath = os.path.join(receipts_dir, filename)
            
#             with open(filepath, 'w', encoding='utf-8') as f:
#                 f.write(receipt_text)
            
#             messagebox.showinfo("🖨️ Receipt Saved", f"Receipt saved to:\n{filepath}")
#         except Exception as e:
#             messagebox.showerror("❌ Print Error", f"Failed to print receipt: {str(e)}")

#     def _format_receipt(self, details, is_reprint=False):
#         lines = []
#         lines.append("=" * 40)
#         lines.append("         DINEDASH RESTAURANT")
#         lines.append("         Premium Dining Experience")
#         lines.append("=" * 40)
        
#         if is_reprint:
#             lines.append("         *** REPRINT ***")
#             lines.append("")
        
#         lines.append(f"Date: {details['timestamp']}")
#         lines.append(f"Table: {details['table_name']}")
#         lines.append(f"Server: {details['user_name']}")
#         lines.append("-" * 40)
        
#         # Items
#         for item in details['items']:
#             name = item['product_name'][:20].ljust(20)
#             qty = str(item['quantity']).rjust(3)
#             price = f"${item['price_at_time']:.2f}".rjust(7)
#             total = f"${item['price_at_time'] * item['quantity']:.2f}".rjust(8)
#             lines.append(f"{name} {qty} {price} {total}")
        
#         lines.append("-" * 40)
#         lines.append(f"Subtotal: ${details['subtotal']:.2f}".rjust(40))
#         lines.append(f"Tax (10%): ${details['tax']:.2f}".rjust(40))
#         lines.append("=" * 40)
#         lines.append(f"TOTAL: ${details['total']:.2f}".rjust(40))
#         lines.append("=" * 40)
#         lines.append("")
#         lines.append("      Thank you for dining with us!")
#         lines.append("         Visit us again soon!")
#         lines.append("")
#         lines.append("")
        
#         return "\n".join(lines)
    
class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        self.selected_product_id = None
        self.selected_table_id = None
        self.grid_columnconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        menu_mgmt_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG)
        menu_mgmt_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        menu_mgmt_frame.grid_columnconfigure(0, weight=1); menu_mgmt_frame.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(menu_mgmt_frame, text="Menu Management", font=Style.HEADER_FONT).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(menu_mgmt_frame, text="< Back", command=lambda: controller.show_frame("TableScreen")).grid(row=0, column=1, padx=10)
        self.product_listbox = tk.Listbox(menu_mgmt_frame, bg=Style.BACKGROUND, fg=Style.TEXT, font=Style.BODY_FONT, selectbackground=Style.ACCENT, borderwidth=0, highlightthickness=0)
        self.product_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.product_listbox.bind('<<ListboxSelect>>', self.on_product_select)
        table_mgmt_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG)
        table_mgmt_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        table_mgmt_frame.grid_columnconfigure(0, weight=1); table_mgmt_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(table_mgmt_frame, text="Floor Plan Management", font=Style.HEADER_FONT).grid(row=0, column=0, padx=10, pady=10)
        self.table_listbox = tk.Listbox(table_mgmt_frame, bg=Style.BACKGROUND, fg=Style.TEXT, font=Style.BODY_FONT, selectbackground=Style.ACCENT, borderwidth=0, highlightthickness=0)
        self.table_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        self.create_menu_form(menu_mgmt_frame)
        self.create_table_form(table_mgmt_frame)
    def create_menu_form(self, parent):
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="Name"); self.name_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.price_entry = ctk.CTkEntry(form_frame, placeholder_text="Price"); self.price_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.category_combobox = ctk.CTkComboBox(form_frame, values=[]); self.category_combobox.pack(side="left", expand=True, fill="x", padx=5)
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent"); btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ctk.CTkButton(btn_frame, text="Save", command=self.save_product).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="New", command=self.clear_menu_form).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", fg_color=Style.DANGER, command=self.delete_product).pack(side="left", padx=5)
    def create_table_form(self, parent):
        form_frame = ctk.CTkFrame(parent, fg_color="transparent"); form_frame.grid(row=2, column=0, sticky="ew", padx=10)
        self.table_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Table Name"); self.table_name_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.table_capacity_entry = ctk.CTkEntry(form_frame, placeholder_text="Capacity"); self.table_capacity_entry.pack(side="left", expand=True, fill="x", padx=5)
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent"); btn_frame.grid(row=3, column=0, pady=10)
        ctk.CTkButton(btn_frame, text="Save Table", command=self.save_table).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="New Table", command=self.clear_table_form).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Table", fg_color=Style.DANGER, command=self.delete_table).pack(side="left", padx=5)
    def refresh(self):
        self.load_product_list(); self.load_categories(); self.clear_menu_form()
        self.load_table_list(); self.clear_table_form()
    def load_product_list(self):
        self.product_listbox.delete(0, tk.END)
        self.products = self.db.get_products()
        for p in self.products: self.product_listbox.insert(tk.END, f"{p['name']} ({p['category']}) - ${p['price']:.2f}")
    def load_categories(self): self.category_combobox.configure(values=self.db.get_product_categories())
    def on_product_select(self, event):
        if not self.product_listbox.curselection(): return
        product = self.products[self.product_listbox.curselection()[0]]
        self.selected_product_id = product['id']
        self.name_entry.delete(0, tk.END); self.name_entry.insert(0, product['name'])
        self.price_entry.delete(0, tk.END); self.price_entry.insert(0, str(product['price']))
        self.category_combobox.set(product['category'])
    def clear_menu_form(self):
        self.selected_product_id = None; self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END); self.category_combobox.set("")
    def save_product(self):
        name = self.name_entry.get(); price_str = self.price_entry.get(); category = self.category_combobox.get()
        if not all([name, price_str, category]): messagebox.showerror("Error", "All product fields are required."); return
        try: price = float(price_str)
        except ValueError: messagebox.showerror("Error", "Price must be a valid number."); return
        if self.selected_product_id: self.db.update_product(self.selected_product_id, name, price, category)
        else: self.db.add_product(name, price, category)
        self.refresh(); messagebox.showinfo("Success", "Product saved.")
    def delete_product(self):
        if not self.selected_product_id: messagebox.showerror("Error", "No product selected."); return
        if messagebox.askyesno("Confirm", "Delete this product?"):
            self.db.delete_product(self.selected_product_id); self.refresh(); messagebox.showinfo("Success", "Product deleted.")
    def load_table_list(self):
        self.table_listbox.delete(0, tk.END)
        self.tables = self.db.get_all_tables_for_management()
        for t in self.tables: self.table_listbox.insert(tk.END, f"{t['name']} (Capacity: {t['capacity']})")
    def on_table_select(self, event):
        if not self.table_listbox.curselection(): return
        table = self.tables[self.table_listbox.curselection()[0]]
        self.selected_table_id = table['id']
        self.table_name_entry.delete(0, tk.END); self.table_name_entry.insert(0, table['name'])
        self.table_capacity_entry.delete(0, tk.END); self.table_capacity_entry.insert(0, str(table['capacity']))
    def clear_table_form(self):
        self.selected_table_id = None; self.table_name_entry.delete(0, tk.END); self.table_capacity_entry.delete(0, tk.END)
    def save_table(self):
        name = self.table_name_entry.get(); capacity_str = self.table_capacity_entry.get()
        if not all([name, capacity_str]): messagebox.showerror("Error", "All table fields are required."); return
        try: capacity = int(capacity_str)
        except ValueError: messagebox.showerror("Error", "Capacity must be a number."); return
        if self.selected_table_id: self.db.update_table(self.selected_table_id, name, capacity)
        else: self.db.add_table(name, capacity)
        self.refresh(); messagebox.showinfo("Success", "Table saved.")
    def delete_table(self):
        if not self.selected_table_id: messagebox.showerror("Error", "No table selected."); return
        if messagebox.askyesno("Confirm", "Delete this table?"):
            if not self.db.delete_table(self.selected_table_id): messagebox.showerror("Error", "Cannot delete table with an open order.")
            else: self.refresh(); messagebox.showinfo("Success", "Table deleted.")


# class ReportsScreen(ctk.CTkFrame):
#     def __init__(self, parent, controller):
#         super().__init__(parent, fg_color=Style.BACKGROUND)
#         self.controller = controller
#         self.db = controller.get_db()
#         self.graph_widgets = []
#         header = ctk.CTkFrame(self, fg_color="transparent")
#         header.pack(fill="x", padx=20, pady=20)
#         ctk.CTkLabel(header, text="Analytics Dashboard", font=Style.TITLE_FONT, text_color=Style.ACCENT).pack(side="left")
#         ctk.CTkButton(header, text="Export Full Analytics", command=self.export_analytics_to_excel).pack(side="right", padx=10)
#         ctk.CTkButton(header, text="< Back", command=lambda: controller.show_frame("TableScreen")).pack(side="right")
#         self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
#         self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
#         self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_columnconfigure(1, weight=2)
#         self.main_frame.grid_rowconfigure(0, weight=1); self.main_frame.grid_rowconfigure(1, weight=1)
#     def refresh(self):
#         if pd is None or plt is None:
#             for widget in self.main_frame.winfo_children(): widget.destroy()
#             ctk.CTkLabel(self.main_frame, text="Required libraries for reporting are not installed.\nPlease run: pip install pandas matplotlib", font=Style.HEADER_FONT, text_color=Style.DANGER).pack(expand=True)
#             return
#         for widget in self.graph_widgets: widget.destroy()
#         self.graph_widgets.clear()
#         all_data = self.db.get_all_sales_data_for_export()
#         if not all_data:
#             for widget in self.main_frame.winfo_children(): widget.destroy()
#             no_data_label = ctk.CTkLabel(self.main_frame, text="No sales data available to generate reports.", font=Style.HEADER_FONT)
#             no_data_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
#             self.graph_widgets.append(no_data_label)
#             return
#         df = pd.DataFrame(all_data, columns=['timestamp', 'table', 'server', 'item', 'category', 'quantity', 'price'])
#         df['timestamp'] = pd.to_datetime(df['timestamp'])
#         df['total_price'] = df['quantity'] * df['price']
#         self.plot_bestsellers(df, 0, 0)
#         self.plot_monthly_sales(df, 0, 1)
#         self.plot_daily_trend(df, 1, 0, 2)
#     def plot_bestsellers(self, df, row, col):
#         frame = ctk.CTkFrame(self.main_frame, fg_color=Style.FRAME_BG)
#         frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
#         self.graph_widgets.append(frame)
#         bestsellers = df.groupby('item')['quantity'].sum().nlargest(5)
#         fig, ax = self._create_figure()
#         bestsellers.sort_values().plot(kind='barh', ax=ax, color=Style.ACCENT)
#         ax.set_title('Top 5 Best-Selling Items', color=Style.TEXT)
#         ax.set_xlabel('Quantity Sold', color=Style.TEXT_MUTED); ax.set_ylabel('')
#         self._embed_plot(fig, frame)
#     def plot_monthly_sales(self, df, row, col):
#         frame = ctk.CTkFrame(self.main_frame, fg_color=Style.FRAME_BG)
#         frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
#         self.graph_widgets.append(frame)
#         df_monthly = df[df['timestamp'].dt.year == datetime.now().year]
#         monthly_sales = df_monthly.groupby(df_monthly['timestamp'].dt.strftime('%b'))['total_price'].sum()
#         months = [datetime(2000, i, 1).strftime('%b') for i in range(1, 13)]
#         monthly_sales = monthly_sales.reindex(months, fill_value=0)
#         fig, ax = self._create_figure()
#         monthly_sales.plot(kind='bar', ax=ax, color=Style.SUCCESS)
#         ax.set_title('Monthly Sales (Current Year)', color=Style.TEXT)
#         ax.set_ylabel('Total Sales ($)', color=Style.TEXT_MUTED); ax.set_xlabel('')
#         plt.xticks(rotation=45)
#         self._embed_plot(fig, frame)
#     def plot_daily_trend(self, df, row, col, colspan):
#         frame = ctk.CTkFrame(self.main_frame, fg_color=Style.FRAME_BG)
#         frame.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=10, pady=10)
#         self.graph_widgets.append(frame)
#         last_30_days_df = df[df['timestamp'] >= (datetime.now() - timedelta(days=30))]
#         daily_sales = last_30_days_df.groupby(last_30_days_df['timestamp'].dt.date)['total_price'].sum()
#         fig, ax = self._create_figure()
#         daily_sales.plot(kind='line', ax=ax, color=Style.ADMIN, marker='o')
#         ax.set_title('Sales Trend (Last 30 Days)', color=Style.TEXT)
#         ax.set_ylabel('Total Sales ($)', color=Style.TEXT_MUTED); ax.set_xlabel('')
#         plt.xticks(rotation=45)
#         self._embed_plot(fig, frame)
#     def _create_figure(self):
#         fig, ax = plt.subplots()
#         fig.set_facecolor(Style.FRAME_BG); ax.set_facecolor(Style.BACKGROUND)
#         ax.tick_params(axis='x', colors=Style.TEXT_MUTED); ax.tick_params(axis='y', colors=Style.TEXT_MUTED)
#         ax.spines['bottom'].set_color(Style.TEXT_MUTED); ax.spines['left'].set_color(Style.TEXT_MUTED)
#         ax.spines['top'].set_color('none'); ax.spines['right'].set_color('none')
#         plt.tight_layout()
#         return fig, ax
#     def _embed_plot(self, fig, parent):
#         canvas = FigureCanvasTkAgg(fig, master=parent)
#         canvas.draw()
#         widget = canvas.get_tk_widget()
#         widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
#         self.graph_widgets.append(widget)
#         plt.close(fig)
#     def export_analytics_to_excel(self):
#         if pd is None or openpyxl is None:
#             messagebox.showerror("Library Not Found", "Pandas or OpenPyXL is not installed.\nPlease run: pip install pandas openpyxl")
#             return
#         filename = "sales_analytics.xlsx"
#         try:
#             all_data = self.db.get_all_sales_data_for_export()
#             if not all_data:
#                 messagebox.showinfo("No Data", "No sales data to export.")
#                 return
#             df = pd.DataFrame(all_data, columns=['timestamp', 'table', 'server', 'item', 'category', 'quantity', 'price'])
#             df['timestamp'] = pd.to_datetime(df['timestamp'])
#             df['total_price'] = df['quantity'] * df['price']
#             sales_by_server = df.groupby('server')['total_price'].sum().reset_index().sort_values('total_price', ascending=False)
#             best_sellers = df.groupby('item')['quantity'].sum().reset_index().sort_values('quantity', ascending=False)
#             df['month'] = df['timestamp'].dt.to_period('M')
#             monthly_sales = df.groupby('month')['total_price'].sum().reset_index()
#             monthly_sales['month'] = monthly_sales['month'].astype(str)
#             with pd.ExcelWriter(filename, engine='openpyxl') as writer:
#                 monthly_sales.to_excel(writer, sheet_name='Monthly Sales', index=False)
#                 best_sellers.to_excel(writer, sheet_name='Best Sellers', index=False)
#                 sales_by_server.to_excel(writer, sheet_name='Sales by Server', index=False)
#                 df.to_excel(writer, sheet_name='Raw Data', index=False)
#             messagebox.showinfo("Success", f"Analytics exported successfully to\n{filename}")
#         except PermissionError:
#             messagebox.showerror("File Error", f"Could not save to {filename}.\nPlease close the file if it's open.")
#         except Exception as e:
#             messagebox.showerror("Excel Error", f"An error occurred: {e}")

class ReportsScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        
        # Header
        header = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="x", padx=30)
        
        ctk.CTkButton(header_content, text="← Back", font=Style.BUTTON_FONT,
                      fg_color=Style.SECONDARY, command=lambda: controller.show_frame("TableScreen")).pack(side="left")
        
        ctk.CTkLabel(header_content, text="📈 Reports & Analytics", font=Style.TITLE_FONT,
                     text_color=Style.ACCENT).pack(side="left", padx=20)
        
        # Main content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Report buttons grid
        reports_grid = ctk.CTkFrame(content_frame, fg_color="transparent")
        reports_grid.pack(fill="both", expand=True)
        
        # Configure grid
        for i in range(3):
            reports_grid.grid_columnconfigure(i, weight=1)
        
        # Report cards
        self.create_report_card(reports_grid, 0, 0, "💰 Daily Sales", 
                                "View today's sales summary", self.show_daily_sales)
        self.create_report_card(reports_grid, 0, 1, "📊 Sales by Period", 
                                "Analyze sales over time", self.show_period_sales)
        self.create_report_card(reports_grid, 0, 2, "🏆 Top Products", 
                                "Best selling items", self.show_top_products)
        self.create_report_card(reports_grid, 1, 0, "👥 Staff Performance", 
                                "Sales by staff member", self.show_staff_performance)
        self.create_report_card(reports_grid, 1, 1, "📋 Order History", 
                                "View all past orders", self.show_order_history)
        self.create_report_card(reports_grid, 1, 2, "💾 Export Data", 
                                "Export reports to Excel", self.export_data)

    def create_report_card(self, parent, row, col, title, description, command):
        card = ctk.CTkFrame(parent, fg_color=Style.CARD_BG, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=Style.HEADER_FONT, 
                     text_color=Style.TEXT).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=description, font=Style.SMALL_FONT, 
                     text_color=Style.TEXT_MUTED).pack(pady=(0, 20))
        
        ctk.CTkButton(card, text="View Report", font=Style.BUTTON_FONT,
                      fg_color=Style.ACCENT, hover_color=Style.ACCENT_HOVER,
                      command=command).pack(pady=(0, 20))

    def show_daily_sales(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Daily Sales Report")
        dialog.geometry("800x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(header_frame, text="💰 Daily Sales Report", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(side="left")
        
        today = datetime.now().strftime("%Y-%m-%d")
        ctk.CTkLabel(header_frame, text=f"Date: {today}", 
                     font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(side="right")
        
        # Content
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Get daily sales data
        sales_data = self.db.get_daily_sales_summary()
        
        if not sales_data:
            ctk.CTkLabel(content_frame, text="No sales data for today", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        # Summary cards
        summary_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        summary_frame.pack(fill="x", pady=20)
        
        self.create_summary_card(summary_frame, "Total Sales", f"${sales_data['total_sales']:.2f}", Style.SUCCESS)
        self.create_summary_card(summary_frame, "Orders", str(sales_data['total_orders']), Style.ACCENT)
        self.create_summary_card(summary_frame, "Avg Order", f"${sales_data['average_order']:.2f}", Style.WARNING)
        
        # Sales by category
        if sales_data['sales_by_category']:
            ctk.CTkLabel(content_frame, text="Sales by Category", 
                         font=Style.HEADER_FONT, text_color=Style.TEXT).pack(pady=(30, 10))
            
            for category, amount in sales_data['sales_by_category'].items():
                cat_frame = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
                cat_frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(cat_frame, text=category, font=Style.BUTTON_FONT, 
                             text_color=Style.TEXT).pack(side="left", padx=20, pady=10)
                ctk.CTkLabel(cat_frame, text=f"${amount:.2f}", font=Style.BUTTON_FONT, 
                             text_color=Style.ACCENT).pack(side="right", padx=20, pady=10)

    def create_summary_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, width=200, height=100)
        card.pack(side="left", padx=10, fill="x", expand=True)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=Style.SMALL_FONT, 
                     text_color="white").pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, font=Style.HEADER_FONT, 
                     text_color="white").pack()

    def show_period_sales(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sales by Period")
        dialog.geometry("900x700")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        # Header
        ctk.CTkLabel(dialog, text="📊 Sales Analysis", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        # Period selection
        period_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        period_frame.pack(pady=10)
        
        period_var = ctk.StringVar(value="Last 7 Days")
        ctk.CTkOptionMenu(period_frame, values=["Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
                          variable=period_var, command=lambda _: update_chart()).pack()
        
        # Chart frame
        chart_frame = ctk.CTkFrame(dialog, fg_color=Style.BACKGROUND)
        chart_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        def update_chart():
            for widget in chart_frame.winfo_children():
                widget.destroy()
            
            period = period_var.get()
            sales_data = self.db.get_sales_by_period(period)
            
            if not sales_data or not plt:
                ctk.CTkLabel(chart_frame, text="No data available or matplotlib not installed", 
                             font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(expand=True)
                return
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 6), facecolor=Style.BACKGROUND)
            ax.set_facecolor(Style.FRAME_BG)
            
            dates = list(sales_data.keys())
            amounts = list(sales_data.values())
            
            ax.bar(dates, amounts, color=Style.ACCENT)
            ax.set_xlabel('Date', color=Style.TEXT)
            ax.set_ylabel('Sales ($)', color=Style.TEXT)
            ax.set_title(f'Sales for {period}', color=Style.TEXT, fontsize=16)
            
            # Style the plot
            ax.tick_params(colors=Style.TEXT)
            ax.spines['bottom'].set_color(Style.TEXT_MUTED)
            ax.spines['left'].set_color(Style.TEXT_MUTED)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for i, (date, amount) in enumerate(zip(dates, amounts)):
                ax.text(i, amount + max(amounts) * 0.01, f'${amount:.0f}', 
                        ha='center', va='bottom', color=Style.TEXT)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        
        update_chart()

    def show_top_products(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Top Products Report")
        dialog.geometry("700x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="🏆 Best Selling Products", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        # Content
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        top_products = self.db.get_top_products(limit=10)
        
        if not top_products:
            ctk.CTkLabel(content_frame, text="No sales data available", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        # Product list
        for i, product in enumerate(top_products, 1):
            product_frame = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
            product_frame.pack(fill="x", pady=5)
            
            # Rank
            rank_color = Style.WARNING if i <= 3 else Style.TEXT_MUTED
            ctk.CTkLabel(product_frame, text=f"#{i}", font=Style.HEADER_FONT,
                         text_color=rank_color, width=50).pack(side="left", padx=20)
            
            # Product info
            info_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, pady=15)
            
            ctk.CTkLabel(info_frame, text=product['name'], font=Style.BUTTON_FONT,
                         text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Sold: {product['quantity_sold']} units", 
                         font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            # Revenue
            ctk.CTkLabel(product_frame, text=f"${product['revenue']:.2f}", 
                         font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(side="right", padx=20)

    def show_staff_performance(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Staff Performance Report")
        dialog.geometry("800x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="👥 Staff Performance", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        # Content
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        staff_data = self.db.get_staff_performance()
        
        if not staff_data:
            ctk.CTkLabel(content_frame, text="No performance data available", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        for staff in staff_data:
            staff_card = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
            staff_card.pack(fill="x", pady=10)
            
            # Staff info
            info_frame = ctk.CTkFrame(staff_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=20, pady=15)
            
            icon = "👑" if staff['role'] == 'Admin' else "👨‍🍳"
            ctk.CTkLabel(info_frame, text=f"{icon} {staff['username']}", 
                         font=Style.HEADER_FONT, text_color=Style.TEXT).pack(anchor="w")
            
            # Stats grid
            stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            stats_frame.pack(fill="x", pady=10)
            
            self.create_stat_item(stats_frame, "Orders", str(staff['total_orders']), 0)
            self.create_stat_item(stats_frame, "Revenue", f"${staff['total_sales']:.2f}", 1)
            self.create_stat_item(stats_frame, "Avg Order", f"${staff['average_order']:.2f}", 2)

    def create_stat_item(self, parent, label, value, column):
        stat_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stat_frame.grid(row=0, column=column, padx=20, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        ctk.CTkLabel(stat_frame, text=label, font=Style.SMALL_FONT,
                     text_color=Style.TEXT_MUTED).pack()
        ctk.CTkLabel(stat_frame, text=value, font=Style.BUTTON_FONT,
                     text_color=Style.ACCENT).pack()

    def show_order_history(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Order History")
        dialog.geometry("1000x700")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="📋 Order History", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        # Filters
        filter_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        filter_frame.pack(pady=10)
        
        date_var = ctk.StringVar(value="All Time")
        ctk.CTkOptionMenu(filter_frame, values=["Today", "Last 7 Days", "Last 30 Days", "All Time"],
                          variable=date_var, command=lambda _: load_orders()).pack(side="left", padx=5)
        
        # Content
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        def load_orders():
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            orders = self.db.get_order_history(date_var.get())
            
            if not orders:
                ctk.CTkLabel(content_frame, text="No orders found", 
                             font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
                return
            
            for order in orders:
                order_card = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
                order_card.pack(fill="x", pady=5)
                
                # Order header
                header_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=15)
                
                ctk.CTkLabel(header_frame, text=f"Order #{order['id']}", 
                             font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(side="left")
                ctk.CTkLabel(header_frame, text=f"${order['total']:.2f}", 
                             font=Style.BUTTON_FONT, text_color=Style.ACCENT).pack(side="right")
                
                # Order details
                details_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                details_frame.pack(fill="x", padx=20, pady=(0, 15))
                
                ctk.CTkLabel(details_frame, text=f"Table: {order['table_name']} | Server: {order['user_name']}", 
                             font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
                ctk.CTkLabel(details_frame, text=f"Date: {order['closed_at']}", 
                             font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
                
                # View details button
                ctk.CTkButton(order_card, text="View Details", height=25,
                              fg_color=Style.SECONDARY, hover_color="#fd8f30",
                              command=lambda o=order: self.show_order_details(o)).pack(pady=(0, 10))
        
        load_orders()

    def show_order_details(self, order):
        detail_dialog = ctk.CTkToplevel(self)
        detail_dialog.title(f"Order #{order['id']} Details")
        detail_dialog.geometry("600x500")
        detail_dialog.configure(fg_color=Style.FRAME_BG)
        
        # Header
        ctk.CTkLabel(detail_dialog, text=f"Order #{order['id']}", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        # Order info
        info_frame = ctk.CTkFrame(detail_dialog, fg_color=Style.CARD_BG, corner_radius=10)
        info_frame.pack(fill="x", padx=30, pady=10)
        
        info_text = f"Table: {order['table_name']}\nServer: {order['user_name']}\nDate: {order['closed_at']}"
        ctk.CTkLabel(info_frame, text=info_text, font=Style.BODY_FONT,
                     text_color=Style.TEXT, justify="left").pack(padx=20, pady=15)
        
        # Items
        items_frame = ctk.CTkScrollableFrame(detail_dialog, fg_color=Style.BACKGROUND)
        items_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        order_items = self.db.get_order_items(order['id'])
        
        for item in order_items:
            item_frame = ctk.CTkFrame(items_frame, fg_color=Style.CARD_BG, corner_radius=10)
            item_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(item_frame, text=f"{item['product_name']} x{item['quantity']}", 
                         font=Style.BODY_FONT, text_color=Style.TEXT).pack(side="left", padx=20, pady=10)
            ctk.CTkLabel(item_frame, text=f"${item['price_at_time'] * item['quantity']:.2f}", 
                         font=Style.BODY_FONT, text_color=Style.ACCENT).pack(side="right", padx=20, pady=10)
        
        # Total
        total_frame = ctk.CTkFrame(detail_dialog, fg_color=Style.CARD_BG, corner_radius=10)
        total_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(total_frame, text=f"Total: ${order['total']:.2f}", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=15)

    def export_data(self):
        if not openpyxl or not pd:
            messagebox.showerror("❌ Error", "Excel export requires openpyxl and pandas libraries.\nPlease install them using: pip install openpyxl pandas")
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Export Data")
        dialog.geometry("500x400")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="💾 Export Data", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        # Export options
        options_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        options_frame.pack(pady=20)
        
        export_type = ctk.StringVar(value="daily_sales")
        
        options = [
            ("Daily Sales Report", "daily_sales"),
            ("Monthly Sales Report", "monthly_sales"),
            ("Product Sales Report", "product_sales"),
            ("Staff Performance Report", "staff_performance"),
            ("Complete Order History", "order_history")
        ]
        
        for text, value in options:
            ctk.CTkRadioButton(options_frame, text=text, variable=export_type,
                               value=value, font=Style.BODY_FONT).pack(anchor="w", pady=5)
        
        def export():
            try:
                # Get export directory
                export_dir = filedialog.askdirectory(title="Select Export Location")
                if not export_dir:
                    return
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"DineDash_{export_type.get()}_{timestamp}.xlsx"
                filepath = os.path.join(export_dir, filename)
                
                # Create Excel writer
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    if export_type.get() == "daily_sales":
                        data = self.db.get_daily_sales_details()
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name='Daily Sales', index=False)
                    
                    elif export_type.get() == "monthly_sales":
                        data = self.db.get_monthly_sales_details()
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name='Monthly Sales', index=False)
                    
                    elif export_type.get() == "product_sales":
                        data = self.db.get_product_sales_details()
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name='Product Sales', index=False)
                    
                    elif export_type.get() == "staff_performance":
                        data = self.db.get_staff_performance_details()
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name='Staff Performance', index=False)
                    
                    elif export_type.get() == "order_history":
                        data = self.db.get_complete_order_history()
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name='Order History', index=False)
                
                messagebox.showinfo("✅ Success", f"Data exported successfully!\nFile saved to: {filepath}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("❌ Export Error", f"Failed to export data: {str(e)}")
        
        ctk.CTkButton(dialog, text="📥 Export to Excel", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=export).pack(pady=30)

if __name__ == "__main__":
    missing = []
    if Usb is None: missing.append("'python-escpos' for printing")
    if openpyxl is None: missing.append("'openpyxl' for Excel export")
    if pd is None: missing.append("'pandas' for analytics")
    if plt is None: missing.append("'matplotlib' for graphs")
    if missing:
        message = "The following libraries are missing:\n\n" + "\n".join(missing) + \
                  "\n\nPlease install them using pip.\nSome features will be disabled."
        messagebox.showwarning("Missing Libraries", message)

    app = App()
    app.mainloop()
