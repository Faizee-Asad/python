import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.utils.style import Style
import os # Import the os module

class TableScreen(ctk.CTkFrame):
    """
    The main screen after login, displaying the restaurant's floor plan.
    It shows the status of each table and provides navigation to other parts
    of the application like settings and reports.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        
        # Header frame
        header = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0, height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Left side - title and stats
        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", padx=30, pady=20)
        
        ctk.CTkLabel(
            left_header, text="🏢 Floor Management", 
            font=Style.TITLE_FONT, text_color=Style.ACCENT
        ).pack(anchor="w")
        
        self.stats_label = ctk.CTkLabel(
            left_header, text="", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED
        )
        self.stats_label.pack(anchor="w")
        
        # Right side - user info and buttons
        right_header = ctk.CTkFrame(header, fg_color="transparent")
        right_header.pack(side="right", padx=30, pady=20)
        
        self.user_label = ctk.CTkLabel(right_header, text="", font=Style.BODY_FONT, text_color=Style.TEXT)
        self.user_label.pack(side="right", padx=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(right_header, fg_color="transparent")
        button_frame.pack(side="right", padx=10)
        
        self.stats_button = ctk.CTkButton(
            button_frame, text="📊 Live Stats", 
            fg_color=Style.WARNING, hover_color="#e85d04",
            command=lambda: controller.show_frame("StatsScreen")
        )
        
        self.reports_button = ctk.CTkButton(
            button_frame, text="📈 Reports", 
            fg_color=Style.SECONDARY, hover_color="#fd8f30"
        )
        
        self.settings_button = ctk.CTkButton(
            button_frame, text="⚙️ Settings", 
            fg_color=Style.ADMIN, hover_color="#a855f7"
        )
        
        ctk.CTkButton(
            button_frame, text="🚪 Logout", fg_color=Style.DANGER, 
            hover_color="#c92a2a", command=self.logout
        ).pack(side="right", padx=5)
        
        # Tables grid
        self.table_grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_grid_frame.pack(fill="both", expand=True, padx=30, pady=20)

    def refresh(self):
        """Refreshes the screen content, including user info and the table grid."""
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

        for widget in self.table_grid_frame.winfo_children():
            widget.destroy()

        tables = self.db.crud.get_tables()
        
        if not tables:
            # --- UPDATED CODE BLOCK for better debugging ---
            db_path = os.path.join(os.path.expanduser("~"), "DineDashPOS", "restaurant_pos.db")
            
            no_tables_frame = ctk.CTkFrame(self.table_grid_frame, fg_color="transparent")
            no_tables_frame.pack(expand=True, pady=100)
            
            ctk.CTkLabel(
                no_tables_frame, text="No Tables Found in the Database",
                font=Style.HEADER_FONT, text_color=Style.TEXT_MUTED
            ).pack()
            ctk.CTkLabel(
                no_tables_frame, text="Admins can add new tables in the 'Settings' menu.",
                font=Style.BODY_FONT, text_color=Style.TEXT_MUTED
            ).pack(pady=5)
            ctk.CTkLabel(
                no_tables_frame, text="\nTo restore default tables, please delete the database file from:",
                font=Style.SMALL_FONT, text_color=Style.WARNING, wraplength=600
            ).pack(pady=(20, 5))
            
            db_path_label = ctk.CTkEntry(no_tables_frame, fg_color=Style.CARD_BG, width=600)
            db_path_label.insert(0, db_path)
            db_path_label.configure(state="readonly")
            db_path_label.pack()
            return
        # --- END OF UPDATED CODE BLOCK ---
            
        available = sum(1 for t in tables if t['status'] == 'available')
        occupied = len(tables) - available
        self.stats_label.configure(text=f"Tables: {len(tables)} total • {available} available • {occupied} occupied")
        
        num_columns = 5
        for i, table_data in enumerate(tables):
            row, col = divmod(i, num_columns)
            is_available = table_data['status'] == 'available'
            
            table_card = ctk.CTkFrame(self.table_grid_frame, fg_color=Style.CARD_BG, corner_radius=15)
            table_card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew", ipadx=10, ipady=10)
            
            status_icon = "✅" if is_available else "🔴"
            
            ctk.CTkLabel(table_card, text=f"{status_icon}", font=("Arial", 24)).pack(pady=(10, 5))
            ctk.CTkLabel(table_card, text=table_data['name'], font=Style.HEADER_FONT, text_color=Style.TEXT).pack()
            ctk.CTkLabel(table_card, text=f"{table_data['capacity']} seats", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 5))
            
            btn_text = "💺 Take Order" if is_available else "👥 View Order"
            btn_color = Style.SUCCESS if is_available else Style.WARNING
            
            table_btn = ctk.CTkButton(
                table_card, text=btn_text, font=Style.BUTTON_FONT,
                fg_color=btn_color, hover_color=status_color,
                command=lambda t_id=table_data['id'], t_name=table_data['name']: self.select_table(t_id, t_name)
            )
            table_btn.pack(pady=10, padx=10, fill="x")
            
            if not is_available:
                table_btn.bind("<Button-3>", lambda e, t_id=table_data['id']: self.show_reprint_menu(e, t_id))
        
        for i in range(num_columns):
            self.table_grid_frame.grid_columnconfigure(i, weight=1)

    def select_table(self, table_id, table_name):
        self.controller.selected_table_id = table_id
        self.controller.selected_table_name = table_name
        self.controller.show_frame("OrderScreen")

    def show_reprint_menu(self, event, table_id):
        menu = tk.Menu(self, tearoff=0, bg=Style.CARD_BG, fg=Style.TEXT, font=Style.BODY_FONT)
        menu.add_command(label="🖨️ Reprint Receipt", command=lambda: self.reprint_receipt(table_id))
        menu.tk_popup(event.x_root, event.y_root)

    def reprint_receipt(self, table_id):
        last_order = self.db.orders.get_last_closed_order_for_table(table_id)
        if not last_order:
            messagebox.showinfo("ℹ️ No Receipt", "No previous closed orders found for this table.")
            return
        
        order_items = self.db.orders.get_order_items(last_order['id'])
        
        subtotal = sum(item['quantity'] * item['price_at_time'] for item in order_items)
        tax = subtotal * 0.10
        total = subtotal + tax
        
        user = self.db.crud.get_user_by_id(last_order['user_id'])
        table = self.db.crud.get_table_by_id(table_id)
        
        receipt_details = {
            "items": order_items, "subtotal": subtotal, "tax": tax, "total": total,
            "table_name": table['name'] if table else 'N/A', 
            "user_name": user['username'] if user else 'N/A',
            "timestamp": last_order['closed_at']
        }
        
        self.controller.frames["OrderScreen"]._print_receipt_logic(receipt_details, is_reprint=True)

    def logout(self):
        if messagebox.askyesno("🚪 Logout", "Are you sure you want to logout?"):
            self.controller.current_user = None
            self.controller.show_frame("LoginScreen")

