import customtkinter as ctk
from utils.styles import COLORS, FONTS

class OrderView:
    def _init_(self, parent, controller, table_id):
        self.parent = parent
        self.controller = controller
        self.table_id = table_id
        self.current_order = None
        self.current_category = None
        self.order_items = {}
        self.setup_ui()
        self.load_order()
        self.load_categories()
    
    def setup_ui(self):
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color=COLORS['bg_primary'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create layout
        self.menu_panel = ctk.CTkFrame(container, fg_color=COLORS['bg_tertiary'], 
                                      corner_radius=15)
        self.menu_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.order_panel = ctk.CTkFrame(container, fg_color=COLORS['bg_tertiary'], 
                                       corner_radius=15, width=400)
        self.order_panel.pack(side="right", fill="both", padx=(10, 0))
        self.order_panel.pack_propagate(False)
        
        self.create_menu_panel()
        self.create_order_panel()
    
    def create_menu_panel(self):
        # Header
        header = ctk.CTkFrame(self.menu_panel, fg_color=COLORS['bg_secondary'], 
                             corner_radius=15, height=60)
        header.pack(fill="x", padx=20, pady=(20, 0))
        
        back_btn = ctk.CTkButton(header, text="← Back to Tables", 
                                fg_color=COLORS['accent_orange'], width=150,
                                command=self.controller.show_tables)
        back_btn.pack(side="left", padx=10, pady=10)
        
        # Get table info
        cursor = self.controller.db.cursor
        cursor.execute("SELECT name FROM tables WHERE id = ?", (self.table_id,))
        table = cursor.fetchone()
        
        table_label = ctk.CTkLabel(header, text=f"🍽 Table {table['name']}", 
                                  font=FONTS['heading'], 
                                  text_color=COLORS['accent_green'])
        table_label.pack(side="right", padx=10)
        
        # Category tabs
        self.category_frame = ctk.CTkFrame(self.menu_panel, fg_color="transparent", 
                                          height=50)
        self.category_frame.pack(fill="x", padx=20, pady=20)
        
        # Products area
        self.products_frame = ctk.CTkScrollableFrame(self.menu_panel, 
                                                    fg_color="transparent")
        self.products_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def create_order_panel(self):
        # Header
        header = ctk.CTkLabel(self.order_panel, text="🛒 Current Order", 
                             font=FONTS['heading'])
        header.pack(pady=20)
        
        # Order items area
        self.items_frame = ctk.CTkScrollableFrame(self.order_panel, 
                                                 fg_color="transparent", 
                                                 height=400)
        self.items_frame.pack(fill="both", expand=True, padx=20)
        
# Totals area
        self.totals_frame = ctk.CTkFrame(self.order_panel, 
                                        fg_color=COLORS['bg_secondary'], 
                                        corner_radius=15)
        self.totals_frame.pack(fill="x", padx=20, pady=20)
        
        # Create total labels
        self.subtotal_label = ctk.CTkLabel(self.totals_frame, text="Subtotal: $0.00", 
                                          font=FONTS['body'])
        self.subtotal_label.pack(anchor="e", padx=20, pady=(10, 5))
        
        self.tax_label = ctk.CTkLabel(self.totals_frame, text="Tax (10%): $0.00", 
                                     font=FONTS['body'])
        self.tax_label.pack(anchor="e", padx=20, pady=5)
        
        self.total_label = ctk.CTkLabel(self.totals_frame, text="💰 Total: $0.00", 
                                       font=FONTS['subheading'], 
                                       text_color=COLORS['accent_green'])
        self.total_label.pack(anchor="e", padx=20, pady=(5, 10))
        
        # Pay button
        pay_btn = ctk.CTkButton(self.order_panel, text="💳 Settle & Pay", 
                               height=50, font=FONTS['subheading'],
                               fg_color=COLORS['accent_green'],
                               command=self.process_payment)
        pay_btn.pack(fill="x", padx=20, pady=(0, 20))
    
    def load_order(self):
        cursor = self.controller.db.cursor
        cursor.execute("""
            SELECT * FROM orders 
            WHERE table_id = ? AND status = 'active' 
            ORDER BY created_at DESC LIMIT 1
        """, (self.table_id,))
        
        order = cursor.fetchone()
        if order:
            self.current_order = dict(order)
            self.load_order_items()
    
    def load_order_items(self):
        if not self.current_order:
            return
        
        cursor = self.controller.db.cursor
        cursor.execute("""
            SELECT oi.*, p.name, p.icon 
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (self.current_order['id'],))
        
        items = cursor.fetchall()
        for item in items:
            self.order_items[item['product_id']] = {
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'icon': item['icon']
            }
        
        self.refresh_order_display()
    
    def load_categories(self):
        cursor = self.controller.db.cursor
        cursor.execute("SELECT * FROM categories ORDER BY id")
        categories = cursor.fetchall()
        
        for i, category in enumerate(categories):
            btn = ctk.CTkButton(self.category_frame, text=f"{category['icon']} {category['name']}",
                               fg_color=COLORS['bg_secondary'] if i > 0 else COLORS['accent_green'],
                               hover_color=COLORS['accent_green_hover'],
                               corner_radius=25, width=150,
                               command=lambda c=category: self.select_category(c))
            btn.pack(side="left", padx=5)
            
            if i == 0:
                self.select_category(category)
    
    def select_category(self, category):
        self.current_category = category
        
        # Update button colors
        for widget in self.category_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                if category['name'] in widget.cget("text"):
                    widget.configure(fg_color=COLORS['accent_green'])
                else:
                    widget.configure(fg_color=COLORS['bg_secondary'])
        
        self.load_products()
    
    def load_products(self):
        # Clear existing products
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        
        # Create grid
        grid_frame = ctk.CTkFrame(self.products_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        
        # Get products
        cursor = self.controller.db.cursor
        cursor.execute("SELECT * FROM products WHERE category_id = ?", 
                      (self.current_category['id'],))
        products = cursor.fetchall()
        
        # Create product cards
        row = 0
        col = 0
        for product in products:
            self.create_product_card(grid_frame, product, row, col)
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
    
    def create_product_card(self, parent, product, row, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], 
                           corner_radius=15, width=180, height=220)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        
        # Product image/icon
        icon_frame = ctk.CTkFrame(card, fg_color=COLORS['border'], 
                                 corner_radius=10, width=100, height=100)
        icon_frame.pack(pady=(15, 10))
        icon_frame.pack_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text=product['icon'], 
                                 font=('SF Pro Display', 40))
        icon_label.pack(expand=True)
        
        # Product name
        name_label = ctk.CTkLabel(card, text=product['name'], 
                                 font=FONTS['body'], wraplength=150)
        name_label.pack()
        
        # Price
        price_label = ctk.CTkLabel(card, text=f"${product['price']:.2f}", 
                                  font=FONTS['subheading'], 
                                  text_color=COLORS['accent_green'])
        price_label.pack(pady=5)
        
        # Add button
        add_btn = ctk.CTkButton(card, text="+ Add to Order", 
                               fg_color=COLORS['accent_green'],
                               hover_color=COLORS['accent_green_hover'],
                               corner_radius=20, height=30,
                               command=lambda p=product: self.add_to_order(p))
        add_btn.pack(pady=(0, 10))
    
    def add_to_order(self, product):
        product_id = product['id']
        
        if product_id in self.order_items:
            self.order_items[product_id]['quantity'] += 1
        else:
            self.order_items[product_id] = {
                'name': product['name'],
                'price': product['price'],
                'quantity': 1,
                'icon': product['icon']
            }
        
        # Save to database
        if self.current_order:
            cursor = self.controller.db.cursor
            cursor.execute("""
                INSERT OR REPLACE INTO order_items (order_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (self.current_order['id'], product_id, 
                  self.order_items[product_id]['quantity'], product['price']))
            self.controller.db.conn.commit()
        
        self.refresh_order_display()
    
    def refresh_order_display(self):
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        
        subtotal = 0
        
        # Display order items
        for product_id, item in self.order_items.items():
            if item['quantity'] > 0:
                self.create_order_item(product_id, item)
                subtotal += item['price'] * item['quantity']
        
        # Update totals
        tax = subtotal * 0.1
        total = subtotal + tax
        
        self.subtotal_label.configure(text=f"Subtotal: ${subtotal:.2f}")
        self.tax_label.configure(text=f"Tax (10%): ${tax:.2f}")
        self.total_label.configure(text=f"💰 Total: ${total:.2f}")
        
        # Update order total in database
        if self.current_order:
            cursor = self.controller.db.cursor
            cursor.execute("UPDATE orders SET total = ? WHERE id = ?", 
                          (total, self.current_order['id']))
            self.controller.db.conn.commit()
    
    def create_order_item(self, product_id, item):
        item_frame = ctk.CTkFrame(self.items_frame, fg_color=COLORS['bg_secondary'], 
                                 corner_radius=10, height=80)
        item_frame.pack(fill="x", pady=5)
        item_frame.pack_propagate(False)
        
        # Item info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(info_frame, text=f"{item['icon']} {item['name']}", 
                                 font=FONTS['body'], anchor="w")
        name_label.pack(anchor="w")
        
        price_label = ctk.CTkLabel(info_frame, text=f"${item['price']:.2f} each", 
                                  font=FONTS['small'], 
                                  text_color=COLORS['text_secondary'], anchor="w")
        price_label.pack(anchor="w")
        
        # Quantity controls
        qty_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        qty_frame.pack(side="right", padx=15)
        
        minus_btn = ctk.CTkButton(qty_frame, text="−", width=30, height=30,
                                 fg_color=COLORS['accent_red'],
                                 command=lambda: self.update_quantity(product_id, -1))
        minus_btn.pack(side="left", padx=5)
        
        qty_label = ctk.CTkLabel(qty_frame, text=str(item['quantity']), 
                                font=FONTS['body'], width=30)
        qty_label.pack(side="left", padx=5)
        
        plus_btn = ctk.CTkButton(qty_frame, text="+", width=30, height=30,
                                fg_color=COLORS['accent_green'],
                                command=lambda: self.update_quantity(product_id, 1))
        plus_btn.pack(side="left", padx=5)
        
        # Total
        total_label = ctk.CTkLabel(qty_frame, 
                                  text=f"${item['price'] * item['quantity']:.2f}", 
                                  font=FONTS['subheading'], 
                                  text_color=COLORS['accent_green'], width=80)
        total_label.pack(side="left", padx=(10, 0))
    
    def update_quantity(self, product_id, change):
        if product_id in self.order_items:
            self.order_items[product_id]['quantity'] += change
            
            if self.order_items[product_id]['quantity'] <= 0:
                del self.order_items[product_id]
                # Remove from database
                if self.current_order:
                    cursor = self.controller.db.cursor
                    cursor.execute("DELETE FROM order_items WHERE order_id = ? AND product_id = ?",
                                  (self.current_order['id'], product_id))
                    self.controller.db.conn.commit()
            else:
                # Update database
                if self.current_order:
                    cursor = self.controller.db.cursor
                    cursor.execute("""
                        UPDATE order_items SET quantity = ? 
                        WHERE order_id = ? AND product_id = ?
                    """, (self.order_items[product_id]['quantity'], 
                          self.current_order['id'], product_id))
                    self.controller.db.conn.commit()
            
            self.refresh_order_display()
    
    def process_payment(self):
        if not self.current_order or not self.order_items:
            return
        
        # Update order status
        cursor = self.controller.db.cursor
        cursor.execute("UPDATE orders SET status = 'completed' WHERE id = ?", 
                      (self.current_order['id'],))
        
        # Update table status
        cursor.execute("UPDATE tables SET status = 'available' WHERE id = ?", 
                      (self.table_id,))
        
        self.controller.db.conn.commit()
        
        # Show success message and go back
        self.controller.show_tables()