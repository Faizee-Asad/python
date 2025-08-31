import customtkinter as ctk
from utils.styles import COLORS, FONTS

class TablesView:
    def _init_(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()
        self.refresh_tables()
    
    def setup_ui(self):
        # Main container
        self.container = ctk.CTkFrame(self.parent, fg_color=COLORS['bg_primary'])
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Tables grid
        self.tables_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.tables_frame.pack(fill="both", expand=True, pady=(20, 0))
    
    def create_header(self):
        header = ctk.CTkFrame(self.container, fg_color=COLORS['bg_tertiary'], 
                             corner_radius=15, height=100)
        header.pack(fill="x", pady=(0, 20))
        
        # Left side
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=20)
        
        title = ctk.CTkLabel(left_frame, text="🏢 Floor Management", 
                            font=FONTS['title'], text_color=COLORS['accent_green'])
        title.pack(anchor="w")
        
        # Get table stats
        cursor = self.controller.db.cursor
        cursor.execute("SELECT COUNT(*) as total FROM tables")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as available FROM tables WHERE status = 'available'")
        available = cursor.fetchone()['available']
        
        occupied = total - available
        
        stats = ctk.CTkLabel(left_frame, 
                           text=f"Tables: {total} total • {available} available • {occupied} occupied",
                           font=FONTS['body'], text_color=COLORS['text_secondary'])
        stats.pack(anchor="w", pady=(5, 0))
        
        # Right side
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=20)
        
        # User info
        user_label = ctk.CTkLabel(right_frame, 
                                text=f"👤 {self.controller.current_user['username'].title()} ({self.controller.current_user['role']})",
                                font=FONTS['body'])
        user_label.pack(side="left", padx=(0, 15))
        
        # Buttons
        stats_btn = ctk.CTkButton(right_frame, text="📊 Live Stats", width=100,
                                 fg_color=COLORS['accent_yellow'],
                                 command=self.controller.show_stats)
        stats_btn.pack(side="left", padx=5)
        
        settings_btn = ctk.CTkButton(right_frame, text="⚙ Settings", width=100,
                                    fg_color=COLORS['accent_green'],
                                    command=self.controller.show_settings)
        settings_btn.pack(side="left", padx=5)
        
        logout_btn = ctk.CTkButton(right_frame, text="🚪 Logout", width=100,
                                  fg_color=COLORS['accent_red'],
                                  command=self.controller.logout)
        logout_btn.pack(side="left", padx=5)
    
    def refresh_tables(self):
        # Clear existing tables
        for widget in self.tables_frame.winfo_children():
            widget.destroy()
        
        # Create grid
        grid_frame = ctk.CTkFrame(self.tables_frame, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        
        # Get tables from database
        cursor = self.controller.db.cursor
        cursor.execute("SELECT * FROM tables ORDER BY name")
        tables = cursor.fetchall()
        
        # Create table cards
        row = 0
        col = 0
        for table in tables:
            self.create_table_card(grid_frame, table, row, col)
            col += 1
            if col > 3:  # 4 columns
                col = 0
                row += 1
    
    def create_table_card(self, parent, table, row, col):
        # Table card
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_tertiary'], 
                           corner_radius=15, width=200, height=200)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weight
        parent.grid_columnconfigure(col, weight=1)
        
        # Border color based on status
        if table['status'] == 'available':
            card.configure(border_width=2, border_color=COLORS['accent_green'])
            icon = "✅"
        else:
            card.configure(border_width=2, border_color=COLORS['accent_red'])
            icon = "🔴"
        
        # Table icon
        icon_label = ctk.CTkLabel(card, text=icon, font=('SF Pro Display', 40))
        icon_label.pack(pady=(20, 10))
        
        # Table name
        name_label = ctk.CTkLabel(card, text=table['name'], 
                                 font=FONTS['heading'])
        name_label.pack()
        
        # Capacity
        capacity_label = ctk.CTkLabel(card, text=f"{table['capacity']} seats",
                                     font=FONTS['body'], 
                                     text_color=COLORS['text_secondary'])
        capacity_label.pack(pady=(5, 15))
        
        # Action button
        if table['status'] == 'available':
            btn_text = "💺 Take Order"
            btn_color = COLORS['accent_green']
            command = lambda t=table: self.take_order(t['id'])
        else:
            btn_text = "👥 View Order"
            btn_color = COLORS['accent_yellow']
            command = lambda t=table: self.view_order(t['id'])
        
        action_btn = ctk.CTkButton(card, text=btn_text, 
                                  fg_color=btn_color, width=150,
                                  command=command)
        action_btn.pack()
    
    def take_order(self, table_id):
        # Update table status
        cursor = self.controller.db.cursor
        cursor.execute("UPDATE tables SET status = 'occupied' WHERE id = ?", (table_id,))
        
        # Create new order
        cursor.execute("INSERT INTO orders (table_id, user_id, status) VALUES (?, ?, 'active')",
                      (table_id, self.controller.current_user['id']))
        self.controller.db.conn.commit()
        
        # Navigate to order screen
        self.controller.show_order(table_id)
    
    def view_order(self, table_id):
        self.controller.show_order(table_id)