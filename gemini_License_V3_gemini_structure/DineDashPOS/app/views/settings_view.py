import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.utils.style import Style
from app.utils.image_manager import ImageManager
import os

class SettingsScreen(ctk.CTkFrame):
    """
    Admin-only screen for managing core restaurant data, including users,
    tables, and menu products.
    """
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
        
        ctk.CTkButton(
            header_content, text="← Back", font=Style.BUTTON_FONT,
            fg_color=Style.SECONDARY, command=lambda: controller.show_frame("TableScreen")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_content, text="⚙️ Settings", font=Style.TITLE_FONT,
            text_color=Style.ACCENT
        ).pack(side="left", padx=20)
        
        # Tab view for different settings categories
        self.tabview = ctk.CTkTabview(self, fg_color=Style.FRAME_BG)
        self.tabview.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.tabview.add("👥 Users")
        self.tabview.add("🍽️ Tables")
        self.tabview.add("📦 Products")
        
        self.setup_users_tab()
        self.setup_tables_tab()
        self.setup_products_tab()

    # --- User Management Tab ---
    def setup_users_tab(self):
        users_tab = self.tabview.tab("👥 Users")
        
        ctk.CTkButton(
            users_tab, text="➕ Add New User", font=Style.BUTTON_FONT,
            fg_color=Style.SUCCESS, command=self.add_user
        ).pack(pady=20)
        
        self.users_frame = ctk.CTkScrollableFrame(users_tab, fg_color=Style.BACKGROUND)
        self.users_frame.pack(fill="both", expand=True, padx=20)
        
        self.load_users()

    def load_users(self):
        """Loads and displays all user profiles."""
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # --- UPDATED LINE ---
        users = self.db.crud.get_users()
        for user in users:
            user_card = ctk.CTkFrame(self.users_frame, fg_color=Style.CARD_BG, corner_radius=10)
            user_card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(user_card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
            
            icon = "👑" if user['role'] == "Admin" else "👨‍🍳"
            ctk.CTkLabel(info_frame, text=f"{icon} {user['username']}", font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Role: {user['role']}", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            if user['username'].lower() != 'admin': # Prevent deleting default admin
                ctk.CTkButton(
                    user_card, text="🗑️ Delete", width=80,
                    fg_color=Style.DANGER, hover_color="#c92a2a",
                    command=lambda u=user: self.delete_user(u)
                ).pack(side="right", padx=20)

    def add_user(self):
        """Opens a dialog to add a new user."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New User")
        dialog.geometry("400x300")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Add New User", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        username_entry = ctk.CTkEntry(dialog, placeholder_text="Username", width=300)
        username_entry.pack(pady=10)
        
        role_var = ctk.StringVar(value="Server")
        role_menu = ctk.CTkOptionMenu(dialog, values=["Server", "Admin"], variable=role_var, width=300)
        role_menu.pack(pady=10)
        
        def save_user():
            username = username_entry.get().strip()
            if username:
                # --- UPDATED LINE ---
                if self.db.crud.add_user(username, role_var.get()):
                    self.load_users()
                    dialog.destroy()
                    messagebox.showinfo("✅ Success", "User added successfully!")
                else:
                    messagebox.showerror("❌ Error", "Username already exists!", parent=dialog)
        
        ctk.CTkButton(dialog, text="💾 Save User", font=Style.BUTTON_FONT, fg_color=Style.SUCCESS, command=save_user).pack(pady=20)

    def delete_user(self, user):
        """Deletes a selected user after confirmation."""
        if messagebox.askyesno("🗑️ Delete User", f"Are you sure you want to delete the user '{user['username']}'?"):
            # --- UPDATED LINE ---
            self.db.crud.delete_user(user['id'])
            self.load_users()
            messagebox.showinfo("✅ Success", "User deleted successfully!")

    # --- Table Management Tab ---
    def setup_tables_tab(self):
        tables_tab = self.tabview.tab("🍽️ Tables")
        
        ctk.CTkButton(
            tables_tab, text="➕ Add New Table", font=Style.BUTTON_FONT,
            fg_color=Style.SUCCESS, command=self.add_table
        ).pack(pady=20)
        
        self.tables_frame = ctk.CTkScrollableFrame(tables_tab, fg_color=Style.BACKGROUND)
        self.tables_frame.pack(fill="both", expand=True, padx=20)
        
        self.load_tables()

    def load_tables(self):
        """Loads and displays all restaurant tables."""
        for widget in self.tables_frame.winfo_children():
            widget.destroy()
        
        # --- UPDATED LINE ---
        tables = self.db.crud.get_all_tables_for_management()
        for table in tables:
            table_card = ctk.CTkFrame(self.tables_frame, fg_color=Style.CARD_BG, corner_radius=10)
            table_card.pack(fill="x", pady=5)
            
            info_frame = ctk.CTkFrame(table_card, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
            
            status_icon = "✅" if table['status'] == 'available' else "🔴"
            ctk.CTkLabel(info_frame, text=f"{status_icon} {table['name']}", font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Capacity: {table['capacity']} seats", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            ctk.CTkButton(
                table_card, text="🗑️ Delete", width=80,
                fg_color=Style.DANGER, hover_color="#c92a2a",
                command=lambda t=table: self.delete_table(t)
            ).pack(side="right", padx=20)

    def add_table(self):
        """Opens a dialog to add a new table."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Table")
        dialog.geometry("400x350")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Add New Table", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Table Name (e.g., T1)", width=300)
        name_entry.pack(pady=10)
        
        capacity_var = ctk.StringVar(value="4")
        capacity_menu = ctk.CTkOptionMenu(dialog, values=["2", "4", "6", "8", "10", "12", "16"], variable=capacity_var, width=300)
        capacity_menu.pack(pady=10)
        
        def save_table():
            name = name_entry.get().strip()
            if name:
                # --- UPDATED LINE ---
                if self.db.crud.add_table(name, int(capacity_var.get())):
                    self.load_tables()
                    dialog.destroy()
                    messagebox.showinfo("✅ Success", "Table added successfully!")
                else:
                    messagebox.showerror("❌ Error", "Table name already exists!", parent=dialog)
        
        ctk.CTkButton(dialog, text="💾 Save Table", font=Style.BUTTON_FONT, fg_color=Style.SUCCESS, command=save_table).pack(pady=20)

    def delete_table(self, table):
        """Deletes a table after confirming it's available."""
        if table['status'] != 'available':
            messagebox.showwarning("⚠️ Cannot Delete", "Cannot delete an occupied table. Please close the order first.")
            return
        
        if messagebox.askyesno("🗑️ Delete Table", f"Are you sure you want to delete table '{table['name']}'?"):
            # --- UPDATED LINE ---
            self.db.crud.delete_table(table['id'])
            self.load_tables()
            messagebox.showinfo("✅ Success", "Table deleted successfully!")

    # --- Product Management Tab ---
    def setup_products_tab(self):
        products_tab = self.tabview.tab("📦 Products")
        
        ctk.CTkButton(
            products_tab, text="➕ Add New Product", font=Style.BUTTON_FONT,
            fg_color=Style.SUCCESS, command=self.add_product
        ).pack(pady=20)
        
        self.products_frame = ctk.CTkScrollableFrame(products_tab, fg_color=Style.BACKGROUND)
        self.products_frame.pack(fill="both", expand=True, padx=20)
        
        self.load_products()

    def load_products(self):
        """Loads and displays all menu products, grouped by category."""
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # --- UPDATED LINE ---
        products = self.db.crud.get_products()
        
        categories = {}
        for product in products:
            if product['category'] not in categories:
                categories[product['category']] = []
            categories[product['category']].append(product)
        
        for category, items in categories.items():
            category_header = ctk.CTkFrame(self.products_frame, fg_color=Style.ACCENT, corner_radius=10)
            category_header.pack(fill="x", pady=(20, 10))
            ctk.CTkLabel(category_header, text=f"📁 {category}", font=Style.BUTTON_FONT, text_color="white").pack(pady=10)
            
            for product in items:
                product_card = ctk.CTkFrame(self.products_frame, fg_color=Style.CARD_BG, corner_radius=10)
                product_card.pack(fill="x", pady=5, padx=20)
                
                image_frame = ctk.CTkFrame(product_card, fg_color="transparent", width=60, height=60)
                image_frame.pack(side="left", padx=10, pady=10)
                image_frame.pack_propagate(False)
                
                try:
                    product_image = ImageManager.get_product_image(product.get('image'), (50, 50))
                    if product_image:
                        image_label = ctk.CTkLabel(image_frame, image=product_image, text="")
                        image_label.pack(expand=True)
                        image_label.image = product_image
                except Exception:
                    pass
                
                info_frame = ctk.CTkFrame(product_card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=15)
                
                ctk.CTkLabel(info_frame, text=product['name'], font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"${product['price']:.2f}", font=Style.SMALL_FONT, text_color=Style.ACCENT).pack(anchor="w")
                
                actions_frame = ctk.CTkFrame(product_card, fg_color="transparent")
                actions_frame.pack(side="right", padx=20)
                
                ctk.CTkButton(actions_frame, text="✏️ Edit", width=70, fg_color=Style.WARNING, hover_color="#e85d04",
                              command=lambda p=product: self.edit_product(p)).pack(side="left", padx=5)
                ctk.CTkButton(actions_frame, text="🗑️ Delete", width=70, fg_color=Style.DANGER, hover_color="#c92a2a",
                              command=lambda p=product: self.delete_product(p)).pack(side="left")

    def add_product(self):
        """Opens a dialog to add a new product."""
        self.show_product_dialog()

    def edit_product(self, product):
        """Opens a dialog to edit an existing product."""
        self.show_product_dialog(product)

    def show_product_dialog(self, product=None):
        """A generic dialog for adding or editing a product."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Product" if product else "Add New Product")
        dialog.geometry("500x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Edit Product" if product else "Add New Product", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Product Name", width=400)
        name_entry.pack(pady=10)
        if product: name_entry.insert(0, product['name'])
        
        price_entry = ctk.CTkEntry(dialog, placeholder_text="Price (e.g., 9.99)", width=400)
        price_entry.pack(pady=10)
        if product: price_entry.insert(0, str(product['price']))
        
        category_var = ctk.StringVar(value=product['category'] if product else "Mains")
        category_menu = ctk.CTkOptionMenu(dialog, values=["Appetizers", "Mains", "Desserts", "Drinks"], variable=category_var, width=400)
        category_menu.pack(pady=10)
        
        image_path_var = ctk.StringVar()
        image_label = ctk.CTkLabel(dialog, text="No new image selected", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED)
        image_label.pack(pady=10)
        
        def select_image():
            path = filedialog.askopenfilename(title="Select Product Image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
            if path:
                image_path_var.set(path)
                image_label.configure(text=f"Selected: {os.path.basename(path)}")
        
        ctk.CTkButton(dialog, text="📷 Select Image", font=Style.BUTTON_FONT, fg_color=Style.SECONDARY, command=select_image).pack(pady=10)
        
        def save_product():
            name = name_entry.get().strip()
            try:
                price = float(price_entry.get().strip())
            except ValueError:
                messagebox.showerror("❌ Error", "Invalid price format!", parent=dialog)
                return
            
            if name and price > 0:
                if product:
                    # --- UPDATED LINE ---
                    self.db.crud.update_product(product['id'], name, price, category_var.get())
                    product_id = product['id']
                else:
                    # --- UPDATED LINE ---
                    product_id = self.db.crud.add_product(name, price, category_var.get())
                
                if product_id and image_path_var.get():
                    image_filename = ImageManager.save_product_image(product_id, image_path_var.get())
                    if image_filename:
                        # --- UPDATED LINE ---
                        self.db.crud.update_product_image(product_id, image_filename)
                
                self.load_products()
                dialog.destroy()
                messagebox.showinfo("✅ Success", "Product saved successfully!")
        
        ctk.CTkButton(dialog, text="💾 Save Product", font=Style.BUTTON_FONT, fg_color=Style.SUCCESS, command=save_product).pack(pady=20)

    def delete_product(self, product):
        """Deletes a product after confirmation."""
        if messagebox.askyesno("🗑️ Delete Product", f"Are you sure you want to delete '{product['name']}'?"):
            # --- UPDATED LINE ---
            self.db.crud.delete_product(product['id'])
            self.load_products()
            messagebox.showinfo("✅ Success", "Product deleted successfully!")

