import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
from database import Database
from datetime import datetime, timedelta
import os
import hashlib
import base64
import shutil

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

class LicenseManager:
    SECRET_KEY = "DineDashPOS-Malegaon-Secret-2025"

    @staticmethod
    def generate_signature(key):
        return hashlib.sha256((key + LicenseManager.SECRET_KEY).encode()).hexdigest()

    @staticmethod
    def validate_license_key(key):
        try:
            decoded_key = base64.b64decode(key).decode()
            return decoded_key == "VALID-LICENSE-FOR-DINEDASH"
        except Exception:
            return False

class ImageManager:
    @staticmethod
    def get_images_dir():
        home_dir = os.path.expanduser("~")
        images_dir = os.path.join(home_dir, "DineDashPOS", "images")
        os.makedirs(images_dir, exist_ok=True)
        return images_dir
    
    @staticmethod
    def save_product_image(product_id, source_path):
        if not os.path.exists(source_path):
            return None
        
        images_dir = ImageManager.get_images_dir()
        file_ext = os.path.splitext(source_path)[1].lower()
        if file_ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return None
        
        filename = f"product_{product_id}{file_ext}"
        destination = os.path.join(images_dir, filename)
        
        try:
            # Resize and save image
            with Image.open(source_path) as img:
                img = img.convert('RGB')
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(destination, 'JPEG', quality=85)
            return filename
        except Exception:
            return None
    
    @staticmethod
    def get_product_image(image_filename, size=(150, 150)):
        if not image_filename:
            # Return default image
            try:
                default_img = Image.new('RGB', size, color='#404040')
                return ImageTk.PhotoImage(default_img)
            except Exception:
                return None
        
        images_dir = ImageManager.get_images_dir()
        image_path = os.path.join(images_dir, image_filename)
        
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception:
            # Return default image on error
            try:
                default_img = Image.new('RGB', size, color='#404040')
                return ImageTk.PhotoImage(default_img)
            except Exception:
                return None

class AnimatedButton(ctk.CTkButton):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.original_y = None
    
    def on_enter(self, event):
        if self.original_y is None:
            self.original_y = self.winfo_y()
        self.place(y=self.original_y - 2)
    
    def on_leave(self, event):
        if self.original_y is not None:
            self.place(y=self.original_y)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DineDash POS - Premium Restaurant Management")
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
        for F in (LicenseScreen, LoginScreen, TableScreen,OrderScreen,SettingsScreen, ReportsScreen, StatsScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.check_license()

    def check_license(self):
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
        
        ctk.CTkLabel(title_frame, text="🍽️ DineDash", font=("SF Pro Display", 36, "bold"), 
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
        
        ctk.CTkLabel(header_frame, text="🍽️ Welcome to DineDash", 
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
        
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Menu
        menu_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0)
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.grid_rowconfigure(2, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)
        
        # Menu header
        menu_header = ctk.CTkFrame(menu_frame, fg_color="transparent", height=60)
        menu_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        menu_header.pack_propagate(False)
        
        ctk.CTkButton(menu_header, text="← Back to Tables", 
                      font=Style.BUTTON_FONT, fg_color=Style.SECONDARY,
                      command=lambda: controller.show_frame("TableScreen")).pack(side="left")
        
        self.table_label = ctk.CTkLabel(menu_header, text="", font=Style.HEADER_FONT, text_color=Style.ACCENT)
        self.table_label.pack(side="right")
        
        # Category tabs
        self.category_frame = ctk.CTkScrollableFrame(menu_frame, fg_color="transparent", 
                                                     orientation="horizontal", height=60)
        self.category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Menu items grid
        self.menu_items_frame = ctk.CTkScrollableFrame(menu_frame, fg_color=Style.BACKGROUND)
        self.menu_items_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Right panel - Order
        order_frame = ctk.CTkFrame(self, fg_color=Style.CARD_BG, corner_radius=0)
        order_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        order_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)
        
        # Order header
        order_header = ctk.CTkFrame(order_frame, fg_color="transparent", height=60)
        order_header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        order_header.pack_propagate(False)
        
        ctk.CTkLabel(order_header, text="🛒 Current Order", font=Style.HEADER_FONT, 
                     text_color=Style.TEXT).pack()
        
        # Order items
        self.order_items_frame = ctk.CTkScrollableFrame(order_frame, fg_color=Style.FRAME_BG)
        self.order_items_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        # Totals and actions
        self.totals_frame = ctk.CTkFrame(order_frame, fg_color="transparent")
        self.totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.totals_frame.grid_columnconfigure(1, weight=1)
        
        self.subtotal_label = self.create_total_row(self.totals_frame, 0, "Subtotal")
        self.tax_label = self.create_total_row(self.totals_frame, 1, "Tax (10%)")
        self.total_label = self.create_total_row(self.totals_frame, 2, "💰 Total", Style.HEADER_FONT)
        
        # Action buttons
        self.settle_button = ctk.CTkButton(self.totals_frame, text="💳 Settle & Pay", 
                                           font=Style.BUTTON_FONT, fg_color=Style.SUCCESS,
                                           height=50, command=self.settle_order)
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        
        self.print_button = ctk.CTkButton(self.totals_frame, text="🖨️ Print Receipt", 
                                          font=Style.BUTTON_FONT, fg_color=Style.ACCENT,
                                          height=50, command=self.print_last_receipt)

    def create_total_row(self, parent, row, text, font=Style.BODY_FONT):
        ctk.CTkLabel(parent, text=text, font=font, text_color=Style.TEXT).grid(
            row=row, column=0, sticky="w", pady=5)
        label = ctk.CTkLabel(parent, text="$0.00", font=font, text_color=Style.TEXT)
        label.grid(row=row, column=1, sticky="e", pady=5)
        return label

    def refresh(self):
        if not self.controller.selected_table_id:
            return
        
        self.table_label.configure(text=f"🍽️ {self.controller.selected_table_name}")
        
        order = self.db.get_open_order_for_table(self.controller.selected_table_id)
        if order:
            self.controller.current_order_id = order['id']
        else:
            self.controller.current_order_id = self.db.create_order(
                self.controller.selected_table_id, self.controller.current_user['id'])
        
        self._set_pre_payment_state()
        self.load_categories()
        self.load_order_items(is_editable=True)

    def load_categories(self, is_enabled=True):
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        categories = self.db.get_product_categories()
        if categories:
            self.current_category = categories[0]
            
            for i, category in enumerate(categories):
                # Category icons
                icons = {"Appetizers": "🥗", "Mains": "🍽️", "Desserts": "🍰", "Drinks": "🥤"}
                icon = icons.get(category, "🍴")
                
                btn = ctk.CTkButton(self.category_frame, text=f"{icon} {category}",
                                    font=Style.BUTTON_FONT, fg_color=Style.ACCENT if category == self.current_category else Style.FRAME_BG,
                                    command=lambda c=category: self.set_category(c))
                btn.pack(side="left", padx=8, pady=5)
                
                if not is_enabled:
                    btn.configure(state="disabled")
            
            self.load_menu_items(is_enabled=is_enabled)

    def set_category(self, category):
        self.current_category = category
        self.load_categories()
        self.load_menu_items()

    def load_menu_items(self, is_enabled=True):
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        products = [p for p in self.db.get_products() if p['category'] == self.current_category]
        num_columns = 3
        
        for i, product in enumerate(products):
            row, col = divmod(i, num_columns)
            
            # Product card
            product_card = ctk.CTkFrame(self.menu_items_frame, fg_color=Style.CARD_BG, corner_radius=15)
            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=10)
            
            # Product image
            try:
                product_image = ImageManager.get_product_image(product.get('image'), (120, 120))
                if product_image:
                    image_label = ctk.CTkLabel(product_card, image=product_image, text="")
                    image_label.pack(pady=(10, 5))
                    # Keep reference to prevent garbage collection
                    image_label.image = product_image
            except Exception:
                pass
            
            # Product info
            ctk.CTkLabel(product_card, text=product['name'], font=Style.BUTTON_FONT, 
                         text_color=Style.TEXT).pack(pady=(5, 2))
            ctk.CTkLabel(product_card, text=f"${product['price']:.2f}", 
                         font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=(0, 10))
            
            # Add button
            add_btn = ctk.CTkButton(product_card, text="+ Add to Order",
                                    fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
                                    command=lambda p=product: self.add_to_order(p))
            add_btn.pack(pady=(0, 10), padx=10, fill="x")
            if not is_enabled:
                add_btn.configure(state="disabled")
        
        # Configure grid weights
        for i in range(num_columns):
            self.menu_items_frame.grid_columnconfigure(i, weight=1)

    def add_to_order(self, product):
        if not self.controller.current_order_id:
            return
        
        self.db.add_order_item(self.controller.current_order_id, product['id'], 1, product['price'])
        self.load_order_items(is_editable=True)

    def load_order_items(self, is_editable=True):
        for widget in self.order_items_frame.winfo_children():
            widget.destroy()
        
        if not self.controller.current_order_id:
            return
        
        order_items = self.db.get_order_items(self.controller.current_order_id)
        
        if not order_items:
            ctk.CTkLabel(self.order_items_frame, text="No items in order", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
        
        subtotal = 0
        for item in order_items:
            item_frame = ctk.CTkFrame(self.order_items_frame, fg_color=Style.BACKGROUND, corner_radius=10)
            item_frame.pack(fill="x", pady=5, padx=5)
            
            # Item details
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(details_frame, text=item['product_name'], 
                         font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(details_frame, text=f"${item['price_at_time']:.2f} × {item['quantity']} = ${item['price_at_time'] * item['quantity']:.2f}", 
                         font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            # Quantity controls
            if is_editable:
                controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                controls_frame.pack(side="right", padx=10)
                
                ctk.CTkButton(controls_frame, text="-", width=30, height=30,
                              fg_color=Style.DANGER, hover_color="#c92a2a",
                              command=lambda i=item: self.update_quantity(i, -1)).pack(side="left", padx=2)
                
                qty_label = ctk.CTkLabel(controls_frame, text=str(item['quantity']), 
                                         font=Style.BUTTON_FONT, text_color=Style.TEXT)
                qty_label.pack(side="left", padx=10)
                
                ctk.CTkButton(controls_frame, text="+", width=30, height=30,
                              fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
                              command=lambda i=item: self.update_quantity(i, 1)).pack(side="left", padx=2)
            
            subtotal += item['price_at_time'] * item['quantity']
        
        # Update totals
        tax = subtotal * 0.10
        total = subtotal + tax
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.tax_label.configure(text=f"${tax:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        
        # Store for later use
        self.current_order_details = {
            "items": order_items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total
        }

    def update_quantity(self, item, delta):
        new_quantity = item['quantity'] + delta
        if new_quantity <= 0:
            self.db.remove_order_item(item['id'])
        else:
            self.db.update_order_item_quantity(item['id'], new_quantity)
        self.load_order_items(is_editable=True)

    def settle_order(self):
        if not self.controller.current_order_id:
            return
        
        order_items = self.db.get_order_items(self.controller.current_order_id)
        if not order_items:
            messagebox.showwarning("⚠️ Empty Order", "Cannot settle an empty order.")
            return
        
        if messagebox.askyesno("💳 Confirm Payment", "Has the customer paid for this order?"):
            # Close the order
            self.db.close_order(self.controller.current_order_id)
            
            # Print receipt
            self.print_receipt()
            
            # Update UI
            self._set_post_payment_state()
            messagebox.showinfo("✅ Success", "Order settled successfully!")

    def _set_pre_payment_state(self):
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        self.print_button.grid_forget()

    def _set_post_payment_state(self):
        self.settle_button.grid_forget()
        self.print_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        self.load_categories(is_enabled=False)
        self.load_order_items(is_editable=False)

    def print_receipt(self):
        receipt_details = self.current_order_details.copy()
        receipt_details["table_name"] = self.controller.selected_table_name
        receipt_details["user_name"] = self.controller.current_user['username']
        receipt_details["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._print_receipt_logic(receipt_details)

    def print_last_receipt(self):
        if self.controller.selected_table_id:
            last_order = self.db.get_last_closed_order_for_table(self.controller.selected_table_id)
            if last_order:
                order_items = self.db.get_order_items(last_order['id'])
                subtotal = sum(item['quantity'] * item['price_at_time'] for item in order_items)
                tax = subtotal * 0.10
                total = subtotal + tax
                
                receipt_details = {
                    "items": order_items,
                    "subtotal": subtotal,
                    "tax": tax,
                    "total": total,
                    "table_name": self.controller.selected_table_name,
                    "user_name": self.controller.current_user['username'],
                    "timestamp": last_order['closed_at']
                }
                
                self._print_receipt_logic(receipt_details, is_reprint=True)

    def _print_receipt_logic(self, receipt_details, is_reprint=False):
        # Create receipt text
        receipt_text = self._format_receipt(receipt_details, is_reprint)
        
        # Try to print to thermal printer
        if Usb:
            try:
                # Common USB printer vendor/product IDs
                printer = Usb(0x04b8, 0x0202)  # Epson TM-T88
                printer.text(receipt_text)
                printer.cut()
                return
            except:
                pass
        
        # Fallback: Save to file
        try:
            receipts_dir = os.path.join(os.path.expanduser("~"), "DineDashPOS", "receipts")
            os.makedirs(receipts_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{timestamp}.txt"
            filepath = os.path.join(receipts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            
            messagebox.showinfo("🖨️ Receipt Saved", f"Receipt saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("❌ Print Error", f"Failed to print receipt: {str(e)}")

    def _format_receipt(self, details, is_reprint=False):
        lines = []
        lines.append("=" * 40)
        lines.append("         DINEDASH RESTAURANT")
        lines.append("         Premium Dining Experience")
        lines.append("=" * 40)
        
        if is_reprint:
            lines.append("         *** REPRINT ***")
            lines.append("")
        
        lines.append(f"Date: {details['timestamp']}")
        lines.append(f"Table: {details['table_name']}")
        lines.append(f"Server: {details['user_name']}")
        lines.append("-" * 40)
        
        # Items
        for item in details['items']:
            name = item['product_name'][:20].ljust(20)
            qty = str(item['quantity']).rjust(3)
            price = f"${item['price_at_time']:.2f}".rjust(7)
            total = f"${item['price_at_time'] * item['quantity']:.2f}".rjust(8)
            lines.append(f"{name} {qty} {price} {total}")
        
        lines.append("-" * 40)
        lines.append(f"Subtotal: ${details['subtotal']:.2f}".rjust(40))
        lines.append(f"Tax (10%): ${details['tax']:.2f}".rjust(40))
        lines.append("=" * 40)
        lines.append(f"TOTAL: ${details['total']:.2f}".rjust(40))
        lines.append("=" * 40)
        lines.append("")
        lines.append("      Thank you for dining with us!")
        lines.append("         Visit us again soon!")
        lines.append("")
        lines.append("")
        
        return "\n".join(lines)

class SettingsScreen(ctk.CTkFrame):
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
        
        ctk.CTkLabel(header_content, text="⚙️ Settings", font=Style.TITLE_FONT,
                     text_color=Style.ACCENT).pack(side="left", padx=20)
        
        # Tab view
        self.tabview = ctk.CTkTabview(self, fg_color=Style.FRAME_BG)
        self.tabview.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create tabs
        self.tabview.add("👥 Users")
        self.tabview.add("🍽️ Tables")
        self.tabview.add("📦 Products")
        
        self.setup_users_tab()
        self.setup_tables_tab()
        self.setup_products_tab()

    def setup_users_tab(self):
        users_tab = self.tabview.tab("👥 Users")
        
        # Add user button
        ctk.CTkButton(users_tab, text="➕ Add New User", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=self.add_user).pack(pady=20)
        
        # Users list
        self.users_frame = ctk.CTkScrollableFrame(users_tab, fg_color=Style.BACKGROUND)
        self.users_frame.pack(fill="both", expand=True, padx=20)
        
        self.load_users()

    def load_users(self):
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        users = self.db.get_users()
        for user in users:
            user_card = ctk.CTkFrame(self.users_frame, fg_color=Style.CARD_BG, corner_radius=10)
            user_card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(user_card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
            
            icon = "👑" if user['role'] == "Admin" else "👨‍🍳"
            ctk.CTkLabel(info_frame, text=f"{icon} {user['username']}", 
                         font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Role: {user['role']}", 
                         font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            if user['username'] != 'admin':  # Prevent deleting default admin
                ctk.CTkButton(user_card, text="🗑️ Delete", width=80,
                              fg_color=Style.DANGER, hover_color="#c92a2a",
                              command=lambda u=user: self.delete_user(u)).pack(side="right", padx=20)

    def add_user(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("400x300")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="Add New User", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        username_entry = ctk.CTkEntry(dialog, placeholder_text="Username", width=300)
        username_entry.pack(pady=10)
        
        role_var = ctk.StringVar(value="Staff")
        role_menu = ctk.CTkOptionMenu(dialog, values=["Staff", "Admin"], variable=role_var, width=300)
        role_menu.pack(pady=10)
        
        def save_user():
            username = username_entry.get().strip()
            if username:
                if self.db.add_user(username, role_var.get()):
                    self.load_users()
                    dialog.destroy()
                    messagebox.showinfo("✅ Success", "User added successfully!")
                else:
                    messagebox.showerror("❌ Error", "Username already exists!")
        
        ctk.CTkButton(dialog, text="💾 Save User", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=save_user).pack(pady=20)

    def delete_user(self, user):
        if messagebox.askyesno("🗑️ Delete User", f"Delete user '{user['username']}'?"):
            self.db.delete_user(user['id'])
            self.load_users()
            messagebox.showinfo("✅ Success", "User deleted successfully!")

    def setup_tables_tab(self):
        tables_tab = self.tabview.tab("🍽️ Tables")
        
        # Add table button
        ctk.CTkButton(tables_tab, text="➕ Add New Table", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=self.add_table).pack(pady=20)
        
        # Tables list
        self.tables_frame = ctk.CTkScrollableFrame(tables_tab, fg_color=Style.BACKGROUND)
        self.tables_frame.pack(fill="both", expand=True, padx=20)
        
        self.load_tables()

    def load_tables(self):
        for widget in self.tables_frame.winfo_children():
            widget.destroy()
        
        tables = self.db.get_all_tables_for_management()
        for table in tables:
            table_card = ctk.CTkFrame(self.tables_frame, fg_color=Style.CARD_BG, corner_radius=10)
            table_card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(table_card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
            
            status_icon = "✅" if table['status'] == 'available' else "🔴"
            ctk.CTkLabel(info_frame, text=f"{status_icon} {table['name']}", 
                         font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Capacity: {table['capacity']} seats", 
                         font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            ctk.CTkButton(table_card, text="🗑️ Delete", width=80,
                          fg_color=Style.DANGER, hover_color="#c92a2a",
                          command=lambda t=table: self.delete_table(t)).pack(side="right", padx=20)

    def add_table(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Table")
        dialog.geometry("400x350")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="Add New Table", font=Style.HEADER_FONT,
                     text_color=Style.ACCENT).pack(pady=20)
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Table Name (e.g., Table 1)", width=300)
        name_entry.pack(pady=10)
        
        capacity_var = ctk.StringVar(value="4")
        capacity_menu = ctk.CTkOptionMenu(dialog, values=["2", "4", "6", "8", "10"], 
                                          variable=capacity_var, width=300)
        capacity_menu.pack(pady=10)
        
        def save_table():
            name = name_entry.get().strip()
            if name:
                if self.db.add_table(name, int(capacity_var.get())):
                    self.load_tables()
                    dialog.destroy()
                    messagebox.showinfo("✅ Success", "Table added successfully!")
                else:
                    messagebox.showerror("❌ Error", "Table name already exists!")
        
        ctk.CTkButton(dialog, text="💾 Save Table", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=save_table).pack(pady=20)

    def delete_table(self, table):
        if table['status'] != 'available':
            messagebox.showwarning("⚠️ Cannot Delete", "Cannot delete an occupied table!")
            return
        
        if messagebox.askyesno("🗑️ Delete Table", f"Delete table '{table['name']}'?"):
            self.db.delete_table(table['id'])
            self.load_tables()
            messagebox.showinfo("✅ Success", "Table deleted successfully!")

    def setup_products_tab(self):
        products_tab = self.tabview.tab("📦 Products")
        
        # Add product button
        ctk.CTkButton(products_tab, text="➕ Add New Product", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=self.add_product).pack(pady=20)
        
        # Products list
        self.products_frame = ctk.CTkScrollableFrame(products_tab, fg_color=Style.BACKGROUND)
        self.products_frame.pack(fill="both", expand=True, padx=20)
        
        self.load_products()

    def load_products(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        products = self.db.get_products()
        
        # Group by category
        categories = {}
        for product in products:
            if product['category'] not in categories:
                categories[product['category']] = []
            categories[product['category']].append(product)
        
        for category, items in categories.items():
            # Category header
            category_header = ctk.CTkFrame(self.products_frame, fg_color=Style.ACCENT, corner_radius=10)
            category_header.pack(fill="x", pady=(20, 10))
            
            ctk.CTkLabel(category_header, text=f"📁 {category}", font=Style.BUTTON_FONT,
                         text_color="white").pack(pady=10)
            
            # Products in category
            for product in items:
                product_card = ctk.CTkFrame(self.products_frame, fg_color=Style.CARD_BG, corner_radius=10)
                product_card.pack(fill="x", pady=5, padx=20)
                
                # Product image
                image_frame = ctk.CTkFrame(product_card, fg_color="transparent", width=60, height=60)
                image_frame.pack(side="left", padx=10, pady=10)
                image_frame.pack_propagate(False)
                
                try:
                    product_image = ImageManager.get_product_image(product.get('image'), (50, 50))
                    if product_image:
                        image_label = ctk.CTkLabel(image_frame, image=product_image, text="")
                        image_label.pack(expand=True)
                        image_label.image = product_image
                except:
                    pass
                
                info_frame = ctk.CTkFrame(product_card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=15)
                
                ctk.CTkLabel(info_frame, text=product['name'], 
                             font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"${product['price']:.2f}", 
                             font=Style.SMALL_FONT, text_color=Style.ACCENT).pack(anchor="w")
                
                # Action buttons
                actions_frame = ctk.CTkFrame(product_card, fg_color="transparent")
                actions_frame.pack(side="right", padx=20)
                
                ctk.CTkButton(actions_frame, text="✏️ Edit", width=70,
                              fg_color=Style.WARNING, hover_color="#e85d04",
                              command=lambda p=product: self.edit_product(p)).pack(side="left", padx=5)
                
                ctk.CTkButton(actions_frame, text="🗑️ Delete", width=70,
                              fg_color=Style.DANGER, hover_color="#c92a2a",
                              command=lambda p=product: self.delete_product(p)).pack(side="left")

    def add_product(self):
        self.show_product_dialog()

    def edit_product(self, product):
        self.show_product_dialog(product)

    def show_product_dialog(self, product=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Product" if product else "Add New Product")
        dialog.geometry("500x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        
        ctk.CTkLabel(dialog, text="Edit Product" if product else "Add New Product", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        # Form fields
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Product Name", width=400)
        name_entry.pack(pady=10)
        if product:
            name_entry.insert(0, product['name'])
        
        price_entry = ctk.CTkEntry(dialog, placeholder_text="Price (e.g., 9.99)", width=400)
        price_entry.pack(pady=10)
        if product:
            price_entry.insert(0, str(product['price']))
        
        category_var = ctk.StringVar(value=product['category'] if product else "Mains")
        category_menu = ctk.CTkOptionMenu(dialog, values=["Appetizers", "Mains", "Desserts", "Drinks"], 
                                          variable=category_var, width=400)
        category_menu.pack(pady=10)
        
        # Image selection
        image_path_var = ctk.StringVar()
        image_label = ctk.CTkLabel(dialog, text="No image selected", font=Style.SMALL_FONT,
                                   text_color=Style.TEXT_MUTED)
        image_label.pack(pady=10)
        
        def select_image():
            path = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
            )
            if path:
                image_path_var.set(path)
                image_label.configure(text=f"Selected: {os.path.basename(path)}")
        
        ctk.CTkButton(dialog, text="📷 Select Image", font=Style.BUTTON_FONT,
                      fg_color=Style.SECONDARY, command=select_image).pack(pady=10)
        
        def save_product():
            name = name_entry.get().strip()
            try:
                price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("❌ Error", "Invalid price format!")
                return
            
            if name and price > 0:
                if product:
                    # Update existing product
                    self.db.update_product(product['id'], name, price, category_var.get())
                    
                    # Update image if new one selected
                    if image_path_var.get():
                        image_filename = ImageManager.save_product_image(product['id'], image_path_var.get())
                        if image_filename:
                            self.db.update_product_image(product['id'], image_filename)
                else:
                    # Add new product
                    product_id = self.db.add_product(name, price, category_var.get())
                    if product_id:
                        # Save image if selected
                        if image_path_var.get():
                            image_filename = ImageManager.save_product_image(product_id, image_path_var.get())
                            if image_filename:
                                self.db.update_product_image(product_id, image_filename)
                
                self.load_products()
                dialog.destroy()
                messagebox.showinfo("✅ Success", 
                                    "Product updated successfully!" if product else "Product added successfully!")
        
        ctk.CTkButton(dialog, text="💾 Save Product", font=Style.BUTTON_FONT,
                      fg_color=Style.SUCCESS, command=save_product).pack(pady=20)

    def delete_product(self, product):
        if messagebox.askyesno("🗑️ Delete Product", f"Delete product '{product['name']}'?"):
            self.db.delete_product(product['id'])
            self.load_products()
            messagebox.showinfo("✅ Success", "Product deleted successfully!")

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

class StatsScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        self.update_job = None
        
        # Header
        header = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="x", padx=30)
        
        ctk.CTkButton(header_content, text="← Back", font=Style.BUTTON_FONT,
                      fg_color=Style.SECONDARY, command=self.go_back).pack(side="left")
        
        ctk.CTkLabel(header_content, text="📊 Live Dashboard", font=Style.TITLE_FONT,
                     text_color=Style.ACCENT).pack(side="left", padx=20)
        
        self.last_update_label = ctk.CTkLabel(header_content, text="", 
                                              font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED)
        self.last_update_label.pack(side="right")
        
        # Main content grid
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Configure grid
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(2, weight=1)
        
        # Create stat cards
        self.create_stat_cards()
        
        # Charts section
        self.charts_frame = ctk.CTkFrame(self.content_frame, fg_color=Style.FRAME_BG, corner_radius=15)
        self.charts_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=20)
        self.charts_frame.grid_rowconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(1, weight=1)

    def create_stat_cards(self):
        # Today's Revenue
        self.revenue_card = self.create_stat_card(0, 0, "💰 Today's Revenue", "$0.00", Style.SUCCESS)
        
        # Active Orders
        self.orders_card = self.create_stat_card(0, 1, "📋 Active Orders", "0", Style.WARNING)
        
        # Tables Occupied
        self.tables_card = self.create_stat_card(0, 2, "🪑 Tables Occupied", "0/0", Style.ACCENT)
        
        # Average Order Value
        self.avg_order_card = self.create_stat_card(1, 0, "💵 Avg Order Value", "$0.00", Style.ADMIN)
        
        # Top Product Today
        self.top_product_card = self.create_stat_card(1, 1, "🏆 Top Product", "N/A", Style.SECONDARY)
        
        # Staff Online
        self.staff_card = self.create_stat_card(1, 2, "👥 Staff Active", "0", Style.DANGER)

    def create_stat_card(self, row, col, title, initial_value, color):
        card = ctk.CTkFrame(self.content_frame, fg_color=Style.CARD_BG, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Icon and title
        title_frame = ctk.CTkFrame(card, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(title_frame, text=title, font=Style.BUTTON_FONT,
                     text_color=Style.TEXT_MUTED).pack(side="left")
        
        # Value
        value_label = ctk.CTkLabel(card, text=initial_value, font=("SF Pro Display", 28, "bold"),
                                   text_color=color)
        value_label.pack(pady=(0, 20))
        
        # Progress indicator
        progress_frame = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2)
        progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        return {"card": card, "value_label": value_label, "color": color}

    def refresh(self):
        self.update_stats()
        self.start_auto_update()

    def update_stats(self):
        try:
            # Get live stats
            stats = self.db.get_live_stats()
            
            # Update stat cards
            self.revenue_card["value_label"].configure(text=f"${stats['today_revenue']:.2f}")
            self.orders_card["value_label"].configure(text=str(stats['active_orders']))
            self.tables_card["value_label"].configure(text=f"{stats['occupied_tables']}/{stats['total_tables']}")
            self.avg_order_card["value_label"].configure(text=f"${stats['avg_order_value']:.2f}")
            self.top_product_card["value_label"].configure(text=stats['top_product'] or "N/A")
            self.staff_card["value_label"].configure(text=str(stats['active_staff']))
            
            # Update timestamp
            self.last_update_label.configure(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            # Update charts
            self.update_charts(stats)
            
        except Exception as e:
            print(f"Error updating stats: {e}")

    def update_charts(self, stats):
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        if not plt or not FigureCanvasTkAgg:
            ctk.CTkLabel(self.charts_frame, text="Charts require matplotlib", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).grid(row=0, column=0, columnspan=2, pady=50)
            return
        
        # Hourly sales chart
        self.create_hourly_sales_chart(stats.get('hourly_sales', {}))
        
        # Category distribution chart
        self.create_category_chart(stats.get('category_distribution', {}))

    def create_hourly_sales_chart(self, hourly_data):
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=Style.FRAME_BG)
        ax.set_facecolor(Style.FRAME_BG)
        
        if hourly_data:
            hours = list(hourly_data.keys())
            sales = list(hourly_data.values())
            
            ax.plot(hours, sales, color=Style.ACCENT, linewidth=2, marker='o')
            ax.fill_between(hours, sales, alpha=0.3, color=Style.ACCENT)
            
            ax.set_xlabel('Hour', color=Style.TEXT)
            ax.set_ylabel('Sales ($)', color=Style.TEXT)
            ax.set_title('Sales by Hour', color=Style.TEXT, fontsize=14)
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                    transform=ax.transAxes, color=Style.TEXT_MUTED)
        
        # Style
        ax.tick_params(colors=Style.TEXT)
        for spine in ax.spines.values():
            spine.set_color(Style.TEXT_MUTED)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def create_category_chart(self, category_data):
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=Style.FRAME_BG)
        ax.set_facecolor(Style.FRAME_BG)
        
        if category_data:
            categories = list(category_data.keys())
            values = list(category_data.values())
            colors = [Style.SUCCESS, Style.WARNING, Style.ACCENT, Style.ADMIN]
            
            wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors[:len(categories)],
                                               autopct='%1.1f%%', startangle=90)
            
            # Style text
            for text in texts:
                text.set_color(Style.TEXT)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Sales by Category', color=Style.TEXT, fontsize=14)
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                    transform=ax.transAxes, color=Style.TEXT_MUTED)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def start_auto_update(self):
        # Update every 5 seconds
        self.update_job = self.after(5000, self.auto_update)

    def auto_update(self):
        self.update_stats()
        self.update_job = self.after(5000, self.auto_update)

    def go_back(self):
        self.stop_auto_update()
        self.controller.show_frame("TableScreen")

    def stop_auto_update(self):
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None

def main():
    # Set DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Check for required directories
    home_dir = os.path.expanduser("~")
    app_dir = os.path.join(home_dir, "DineDashPOS")
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "receipts"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "exports"), exist_ok=True)
    
    # Create and run app
    app = App()
    
    # Center window on screen
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f'{width}x{height}+{x}+{y}')
    
    # Set minimum window size
    app.minsize(1200, 700)
    
    # Run the application
    app.mainloop()

if __name__ == "__main__":
    main()

