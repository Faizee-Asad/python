import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.utils.style import Style
from datetime import datetime
import os

try:
    import pandas as pd
except (ImportError, ModuleNotFoundError):
    pd = None
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except (ImportError, ModuleNotFoundError):
    plt = None
    FigureCanvasTkAgg = None

class ReportsScreen(ctk.CTkFrame):
    """
    Admin-only screen for viewing historical reports and analytics.
    Provides various views like daily sales, top products, and data export.
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
            header_content, text="📈 Reports & Analytics", font=Style.TITLE_FONT,
            text_color=Style.ACCENT
        ).pack(side="left", padx=20)
        
        # Main content grid for report cards
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        reports_grid = ctk.CTkFrame(content_frame, fg_color="transparent")
        reports_grid.pack(fill="both", expand=True)
        
        for i in range(3):
            reports_grid.grid_columnconfigure(i, weight=1)
        
        # Report card definitions
        self.create_report_card(reports_grid, 0, 0, "💰 Daily Sales", "View today's sales summary", self.show_daily_sales)
        self.create_report_card(reports_grid, 0, 1, "📊 Sales by Period", "Analyze sales over time", self.show_period_sales)
        self.create_report_card(reports_grid, 0, 2, "🏆 Top Products", "Best selling items", self.show_top_products)
        self.create_report_card(reports_grid, 1, 0, "👥 Staff Performance", "Sales by staff member", self.show_staff_performance)
        self.create_report_card(reports_grid, 1, 1, "📋 Order History", "View all past orders", self.show_order_history)
        self.create_report_card(reports_grid, 1, 2, "💾 Export Data", "Export reports to Excel", self.export_data)

    def create_report_card(self, parent, row, col, title, description, command):
        """Helper function to create a consistent report card widget."""
        card = ctk.CTkFrame(parent, fg_color=Style.CARD_BG, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=Style.HEADER_FONT, text_color=Style.TEXT).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=description, font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 20))
        
        ctk.CTkButton(card, text="View Report", font=Style.BUTTON_FONT,
                      fg_color=Style.ACCENT, hover_color=Style.ACCENT_HOVER,
                      command=command).pack(pady=(0, 20))

    def show_daily_sales(self):
        """Displays a dialog with a summary of today's sales."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Daily Sales Report")
        dialog.geometry("800x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()

        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(header_frame, text="💰 Daily Sales Report", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(side="left")
        ctk.CTkLabel(header_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d')}", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(side="right")
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- UPDATED LINE ---
        sales_data = self.db.analytics.get_daily_sales_summary()
        
        if not sales_data or not sales_data['total_orders']:
            ctk.CTkLabel(content_frame, text="No sales data for today", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        summary_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        summary_frame.pack(fill="x", pady=20)
        
        self.create_summary_card(summary_frame, "Total Sales", f"${sales_data['total_sales']:.2f}", Style.SUCCESS)
        self.create_summary_card(summary_frame, "Orders", str(sales_data['total_orders']), Style.ACCENT)
        self.create_summary_card(summary_frame, "Avg Order", f"${sales_data['average_order']:.2f}", Style.WARNING)
        
        if sales_data['sales_by_category']:
            ctk.CTkLabel(content_frame, text="Sales by Category", font=Style.HEADER_FONT, text_color=Style.TEXT).pack(pady=(30, 10))
            for category, amount in sales_data['sales_by_category'].items():
                cat_frame = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
                cat_frame.pack(fill="x", pady=5)
                ctk.CTkLabel(cat_frame, text=category, font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(side="left", padx=20, pady=10)
                ctk.CTkLabel(cat_frame, text=f"${amount:.2f}", font=Style.BUTTON_FONT, text_color=Style.ACCENT).pack(side="right", padx=20, pady=10)

    def create_summary_card(self, parent, title, value, color):
        """Helper function to create a summary card for report dialogs."""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, width=200, height=100)
        card.pack(side="left", padx=10, fill="x", expand=True)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=Style.SMALL_FONT, text_color="white").pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, font=Style.HEADER_FONT, text_color="white").pack()

    def show_period_sales(self):
        """Displays a dialog with a chart for sales over a selected period."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sales by Period")
        dialog.geometry("900x700")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="📊 Sales Analysis", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        period_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        period_frame.pack(pady=10)
        
        chart_frame = ctk.CTkFrame(dialog, fg_color=Style.BACKGROUND)
        chart_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        def update_chart(period_choice):
            for widget in chart_frame.winfo_children():
                widget.destroy()
            
            # --- UPDATED LINE ---
            sales_data = self.db.analytics.get_sales_by_period(period_choice)
            
            if not sales_data or not plt:
                ctk.CTkLabel(chart_frame, text="No data available or matplotlib not installed", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(expand=True)
                return
            
            fig, ax = plt.subplots(figsize=(10, 6), facecolor=Style.BACKGROUND)
            ax.set_facecolor(Style.FRAME_BG)
            
            dates, amounts = list(sales_data.keys()), list(sales_data.values())
            
            ax.bar(dates, amounts, color=Style.ACCENT)
            ax.set_xlabel('Date', color=Style.TEXT)
            ax.set_ylabel('Sales ($)', color=Style.TEXT)
            ax.set_title(f'Sales for {period_choice}', color=Style.TEXT, fontsize=16)
            
            ax.tick_params(colors=Style.TEXT)
            for spine in ['bottom', 'left']: ax.spines[spine].set_color(Style.TEXT_MUTED)
            for spine in ['top', 'right']: ax.spines[spine].set_visible(False)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        ctk.CTkOptionMenu(period_frame, values=["Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
                          command=update_chart).pack()
        update_chart("Last 7 Days") # Initial chart

    def show_top_products(self):
        """Displays a dialog with the best-selling products."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Top Products Report")
        dialog.geometry("700x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="🏆 Best Selling Products", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- UPDATED LINE ---
        top_products = self.db.analytics.get_top_products(limit=10)
        
        if not top_products:
            ctk.CTkLabel(content_frame, text="No sales data available", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        for i, product in enumerate(top_products, 1):
            product_frame = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
            product_frame.pack(fill="x", pady=5)
            
            rank_color = Style.WARNING if i <= 3 else Style.TEXT_MUTED
            ctk.CTkLabel(product_frame, text=f"#{i}", font=Style.HEADER_FONT, text_color=rank_color, width=50).pack(side="left", padx=20)
            
            info_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, pady=15)
            
            ctk.CTkLabel(info_frame, text=product['name'], font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Sold: {product['quantity_sold']} units", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            ctk.CTkLabel(product_frame, text=f"${product['revenue']:.2f}", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(side="right", padx=20)

    def show_staff_performance(self):
        """Displays a dialog with sales performance for each staff member."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Staff Performance Report")
        dialog.geometry("800x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="👥 Staff Performance", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- UPDATED LINE ---
        staff_data = self.db.analytics.get_staff_performance()
        
        if not staff_data:
            ctk.CTkLabel(content_frame, text="No performance data available", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
            
        for staff in staff_data:
            staff_card = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
            staff_card.pack(fill="x", pady=10)
            
            info_frame = ctk.CTkFrame(staff_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=20, pady=15)
            
            icon = "👑" if staff['role'] == 'Admin' else "👨‍🍳"
            ctk.CTkLabel(info_frame, text=f"{icon} {staff['username']}", font=Style.HEADER_FONT, text_color=Style.TEXT).pack(anchor="w")
            
            stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            stats_frame.pack(fill="x", pady=10)
            
            self.create_stat_item(stats_frame, "Orders", str(staff['total_orders']), 0)
            self.create_stat_item(stats_frame, "Revenue", f"${staff['total_sales']:.2f}", 1)
            self.create_stat_item(stats_frame, "Avg Order", f"${staff['average_order']:.2f}", 2)

    def create_stat_item(self, parent, label, value, column):
        """Helper to create a small stat display item."""
        stat_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stat_frame.grid(row=0, column=column, padx=20, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        ctk.CTkLabel(stat_frame, text=label, font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack()
        ctk.CTkLabel(stat_frame, text=value, font=Style.BUTTON_FONT, text_color=Style.ACCENT).pack()

    def show_order_history(self):
        """Displays a dialog with a filterable list of all past orders."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Order History")
        dialog.geometry("1000x700")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="📋 Order History", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        filter_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        filter_frame.pack(pady=10)
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        def load_orders(date_filter):
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            # --- UPDATED LINE ---
            orders = self.db.analytics.get_order_history(date_filter)
            
            if not orders:
                ctk.CTkLabel(content_frame, text="No orders found for this period", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
                return
            
            for order in orders:
                order_card = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
                order_card.pack(fill="x", pady=5)
                
                header_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=15)
                
                ctk.CTkLabel(header_frame, text=f"Order #{order['id']}", font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(side="left")
                ctk.CTkLabel(header_frame, text=f"${order['total']:.2f}", font=Style.BUTTON_FONT, text_color=Style.ACCENT).pack(side="right")
                
                details_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                details_frame.pack(fill="x", padx=20, pady=(0, 15))
                
                ctk.CTkLabel(details_frame, text=f"Table: {order['table_name']} | Server: {order['user_name']}", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
                ctk.CTkLabel(details_frame, text=f"Date: {order['closed_at']}", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
                
                ctk.CTkButton(order_card, text="View Details", height=25, fg_color=Style.SECONDARY, hover_color="#fd8f30",
                              command=lambda o=order: self.show_order_details(o)).pack(pady=(0, 10))
        
        ctk.CTkOptionMenu(filter_frame, values=["Today", "Last 7 Days", "Last 30 Days", "All Time"],
                          command=load_orders).pack(side="left", padx=5)
        load_orders("Today") # Initial view

    def show_order_details(self, order):
        """Displays a dialog showing the itemized details of a single past order."""
        detail_dialog = ctk.CTkToplevel(self)
        detail_dialog.title(f"Order #{order['id']} Details")
        detail_dialog.geometry("600x500")
        detail_dialog.configure(fg_color=Style.FRAME_BG)
        detail_dialog.transient(self)
        detail_dialog.grab_set()

        ctk.CTkLabel(detail_dialog, text=f"Order #{order['id']}", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        info_frame = ctk.CTkFrame(detail_dialog, fg_color=Style.CARD_BG, corner_radius=10)
        info_frame.pack(fill="x", padx=30, pady=10)
        
        info_text = f"Table: {order['table_name']}\nServer: {order['user_name']}\nDate: {order['closed_at']}"
        ctk.CTkLabel(info_frame, text=info_text, font=Style.BODY_FONT, text_color=Style.TEXT, justify="left").pack(padx=20, pady=15)
        
        items_frame = ctk.CTkScrollableFrame(detail_dialog, fg_color=Style.BACKGROUND)
        items_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # --- UPDATED LINE ---
        order_items = self.db.orders.get_order_items(order['id'])
        
        for item in order_items:
            item_frame = ctk.CTkFrame(items_frame, fg_color=Style.CARD_BG, corner_radius=10)
            item_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(item_frame, text=f"{item['product_name']} x{item['quantity']}", font=Style.BODY_FONT, text_color=Style.TEXT).pack(side="left", padx=20, pady=10)
            ctk.CTkLabel(item_frame, text=f"${item['price_at_time'] * item['quantity']:.2f}", font=Style.BODY_FONT, text_color=Style.ACCENT).pack(side="right", padx=20, pady=10)
            
        total_frame = ctk.CTkFrame(detail_dialog, fg_color=Style.CARD_BG, corner_radius=10)
        total_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(total_frame, text=f"Total: ${order['total']:.2f}", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=15)

    def export_data(self):
        """Opens a dialog to export various reports to an Excel file."""
        if not pd:
            messagebox.showerror("❌ Missing Library", "Excel export requires the 'pandas' library.\nPlease install it using: pip install pandas")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Export Data")
        dialog.geometry("500x400")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self.controller)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="💾 Export Data", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
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
            ctk.CTkRadioButton(options_frame, text=text, variable=export_type, value=value, font=Style.BODY_FONT).pack(anchor="w", pady=5)
        
        def export():
            export_dir = filedialog.askdirectory(title="Select Export Location")
            if not export_dir: return
            
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"DineDash_{export_type.get()}_{timestamp}.xlsx"
                filepath = os.path.join(export_dir, filename)
                
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    report_map = {
                        "daily_sales": self.db.analytics.get_daily_sales_details,
                        "monthly_sales": self.db.analytics.get_monthly_sales_details,
                        "product_sales": self.db.analytics.get_product_sales_details,
                        "staff_performance": self.db.analytics.get_staff_performance_details,
                        "order_history": self.db.analytics.get_complete_order_history
                    }
                    sheet_name = export_type.get().replace('_', ' ').title()
                    data = report_map[export_type.get()]()
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                messagebox.showinfo("✅ Success", f"Data exported successfully!\nFile saved to: {filepath}")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("❌ Export Error", f"Failed to export data: {str(e)}", parent=dialog)
        
        ctk.CTkButton(dialog, text="📥 Export to Excel", font=Style.BUTTON_FONT, fg_color=Style.SUCCESS, command=export).pack(pady=30)

