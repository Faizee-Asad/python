import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
import os
from datetime import datetime
from app.utils.style import Style

# Optional libraries for charting and export
try:
    import pandas as pd
    import openpyxl
except (ImportError, ModuleNotFoundError):
    pd = None
    openpyxl = None
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except (ImportError, ModuleNotFoundError):
    plt = None
    FigureCanvasTkAgg = None

class ReportsScreen(ctk.CTkFrame):
    """The main view for accessing all reports and data exports."""
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
        
        reports_grid = ctk.CTkFrame(content_frame, fg_color="transparent")
        reports_grid.pack(fill="both", expand=True)
        
        for i in range(3):
            reports_grid.grid_columnconfigure(i, weight=1)
            reports_grid.grid_rowconfigure(i, weight=1)

        # Report cards
        self._create_report_card(reports_grid, 0, 0, "💰 Daily Sales", 
                                 "View today's sales summary", self._show_daily_sales)
        self._create_report_card(reports_grid, 0, 1, "📊 Sales by Period", 
                                 "Analyze sales over time", self._show_period_sales)
        self._create_report_card(reports_grid, 0, 2, "🏆 Top Products", 
                                 "Best selling items", self._show_top_products)
        self._create_report_card(reports_grid, 1, 0, "👥 Staff Performance", 
                                 "Sales by staff member", self._show_staff_performance)
        self._create_report_card(reports_grid, 1, 1, "📋 Order History", 
                                 "View all past orders", self._show_order_history)
        self._create_report_card(reports_grid, 1, 2, "💾 Export Data", 
                                 "Export reports to Excel", self._export_data)

    def _create_report_card(self, parent, row, col, title, description, command):
        card = ctk.CTkFrame(parent, fg_color=Style.CARD_BG, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=Style.HEADER_FONT, 
                     text_color=Style.TEXT).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=description, font=Style.SMALL_FONT, 
                     text_color=Style.TEXT_MUTED).pack(pady=(0, 20), padx=10)
        
        ctk.CTkButton(card, text="View Report", font=Style.BUTTON_FONT,
                      fg_color=Style.ACCENT, hover_color=Style.ACCENT_HOVER,
                      command=command).pack(pady=(0, 20))

    def _show_daily_sales(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Daily Sales Report")
        dialog.geometry("800x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self)
        dialog.grab_set()
        
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(header_frame, text="💰 Daily Sales Report", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(side="left")
        
        today = datetime.now().strftime("%Y-%m-%d")
        ctk.CTkLabel(header_frame, text=f"Date: {today}", 
                     font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(side="right")
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        sales_data = self.db.get_daily_sales_summary()
        
        if not sales_data or not sales_data.get('total_orders'):
            ctk.CTkLabel(content_frame, text="No sales data for today", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        summary_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        summary_frame.pack(fill="x", pady=20)
        
        self._create_summary_card(summary_frame, "Total Sales", f"${sales_data['total_sales']:.2f}", Style.SUCCESS)
        self._create_summary_card(summary_frame, "Orders", str(sales_data['total_orders']), Style.ACCENT)
        self._create_summary_card(summary_frame, "Avg Order", f"${sales_data['average_order']:.2f}", Style.WARNING)
        
        if sales_data.get('sales_by_category'):
            ctk.CTkLabel(content_frame, text="Sales by Category", 
                         font=Style.HEADER_FONT, text_color=Style.TEXT).pack(pady=(30, 10))
            
            for category, amount in sales_data['sales_by_category'].items():
                cat_frame = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
                cat_frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(cat_frame, text=category, font=Style.BUTTON_FONT, 
                             text_color=Style.TEXT).pack(side="left", padx=20, pady=10)
                ctk.CTkLabel(cat_frame, text=f"${amount:.2f}", font=Style.BUTTON_FONT, 
                             text_color=Style.ACCENT).pack(side="right", padx=20, pady=10)

    def _create_summary_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=100)
        card.pack(side="left", padx=10, fill="x", expand=True)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=title, font=Style.SMALL_FONT, 
                     text_color="white").pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, font=Style.HEADER_FONT, 
                     text_color="white").pack()

    def _show_period_sales(self):
        if not plt:
            messagebox.showerror("Missing Library", "Matplotlib is required for this feature.")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sales by Period")
        dialog.geometry("900x700")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="📊 Sales Analysis", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        period_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        period_frame.pack(pady=10)
        
        chart_frame = ctk.CTkFrame(dialog, fg_color=Style.BACKGROUND)
        chart_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        def update_chart(period):
            for widget in chart_frame.winfo_children():
                widget.destroy()
            
            sales_data = self.db.get_sales_by_period(period)
            
            if not sales_data:
                ctk.CTkLabel(chart_frame, text="No data available for this period", 
                             font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(expand=True)
                return
            
            fig, ax = plt.subplots(figsize=(10, 6), facecolor=Style.BACKGROUND)
            ax.set_facecolor(Style.FRAME_BG)
            
            dates = list(sales_data.keys())
            amounts = list(sales_data.values())
            
            ax.bar(dates, amounts, color=Style.ACCENT)
            ax.set_xlabel('Date', color=Style.TEXT)
            ax.set_ylabel('Sales ($)', color=Style.TEXT)
            ax.set_title(f'Sales for {period}', color=Style.TEXT, fontsize=16)
            
            ax.tick_params(colors=Style.TEXT)
            ax.spines['bottom'].set_color(Style.TEXT_MUTED)
            ax.spines['left'].set_color(Style.TEXT_MUTED)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.xticks(rotation=45, ha='right')
            
            for i, amount in enumerate(amounts):
                if amount > 0:
                    ax.text(i, amount + max(amounts) * 0.01, f'${amount:.0f}', 
                            ha='center', va='bottom', color=Style.TEXT)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        period_var = ctk.StringVar(value="Last 7 Days")
        ctk.CTkOptionMenu(period_frame, values=["Last 7 Days", "Last 30 Days", "This Month", "Last Month"],
                          variable=period_var, command=update_chart).pack()
        update_chart("Last 7 Days")

    def _show_top_products(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Top Products Report")
        dialog.geometry("700x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="🏆 Best Selling Products", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        top_products = self.db.get_top_products(limit=10)
        
        if not top_products:
            ctk.CTkLabel(content_frame, text="No sales data available", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
            return
        
        for i, product in enumerate(top_products, 1):
            product_frame = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
            product_frame.pack(fill="x", pady=5)
            
            rank_color = Style.WARNING if i <= 3 else Style.TEXT_MUTED
            ctk.CTkLabel(product_frame, text=f"#{i}", font=Style.HEADER_FONT,
                         text_color=rank_color, width=50).pack(side="left", padx=20)
            
            info_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, pady=15)
            
            ctk.CTkLabel(info_frame, text=product['name'], font=Style.BUTTON_FONT,
                         text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Sold: {product['quantity_sold']} units", 
                         font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            ctk.CTkLabel(product_frame, text=f"${product['revenue']:.2f}", 
                         font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(side="right", padx=20)

    def _show_staff_performance(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Staff Performance Report")
        dialog.geometry("800x600")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="👥 Staff Performance", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
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
            
            info_frame = ctk.CTkFrame(staff_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=20, pady=15)
            
            icon = "👑" if staff['role'] == 'Admin' else "👨‍🍳"
            ctk.CTkLabel(info_frame, text=f"{icon} {staff['username']}", 
                         font=Style.HEADER_FONT, text_color=Style.TEXT).pack(anchor="w")
            
            stats_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            stats_frame.pack(fill="x", pady=10)
            
            self._create_stat_item(stats_frame, "Orders", str(staff['total_orders']), 0)
            self._create_stat_item(stats_frame, "Revenue", f"${staff['total_sales']:.2f}", 1)
            self._create_stat_item(stats_frame, "Avg Order", f"${staff['average_order']:.2f}", 2)

    def _create_stat_item(self, parent, label, value, column):
        stat_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stat_frame.grid(row=0, column=column, padx=20, sticky="w")
        parent.grid_columnconfigure(column, weight=1)
        
        ctk.CTkLabel(stat_frame, text=label, font=Style.SMALL_FONT,
                     text_color=Style.TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(stat_frame, text=value, font=Style.BUTTON_FONT,
                     text_color=Style.ACCENT).pack(anchor="w")

    def _show_order_history(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Order History")
        dialog.geometry("1000x700")
        dialog.configure(fg_color=Style.FRAME_BG)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="📋 Order History", font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        filter_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        filter_frame.pack(pady=10)
        
        content_frame = ctk.CTkScrollableFrame(dialog, fg_color=Style.BACKGROUND)
        content_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        def load_orders(date_filter):
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            orders = self.db.get_order_history(date_filter)
            
            if not orders:
                ctk.CTkLabel(content_frame, text="No orders found for this period", 
                             font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
                return
            
            for order in orders:
                order_card = ctk.CTkFrame(content_frame, fg_color=Style.CARD_BG, corner_radius=10)
                order_card.pack(fill="x", pady=5)
                
                header_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=10)
                
                ctk.CTkLabel(header_frame, text=f"Order #{order['id']}", 
                             font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(side="left")
                ctk.CTkLabel(header_frame, text=f"${order['total']:.2f}", 
                             font=Style.BUTTON_FONT, text_color=Style.ACCENT).pack(side="right")
                
                details_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                details_frame.pack(fill="x", padx=20, pady=(0, 10))
                
                info_text = f"Table: {order['table_name']} | Server: {order['user_name']} | Date: {order['closed_at']}"
                ctk.CTkLabel(details_frame, text=info_text, 
                             font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
                
                ctk.CTkButton(order_card, text="View Details", height=25,
                              fg_color=Style.SECONDARY, hover_color="#fd8f30",
                              command=lambda o=order: self._show_order_details(o, dialog)).pack(pady=(0, 10))
        
        date_var = ctk.StringVar(value="All Time")
        ctk.CTkOptionMenu(filter_frame, values=["Today", "Last 7 Days", "Last 30 Days", "All Time"],
                          variable=date_var, command=load_orders).pack(side="left", padx=5)
        load_orders("All Time")

    def _show_order_details(self, order, parent_dialog):
        detail_dialog = ctk.CTkToplevel(self)
        detail_dialog.title(f"Order #{order['id']} Details")
        detail_dialog.geometry("600x500")
        detail_dialog.configure(fg_color=Style.FRAME_BG)
        detail_dialog.transient(parent_dialog)
        detail_dialog.grab_set()

        ctk.CTkLabel(detail_dialog, text=f"Order #{order['id']}", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=20)
        
        info_frame = ctk.CTkFrame(detail_dialog, fg_color=Style.CARD_BG, corner_radius=10)
        info_frame.pack(fill="x", padx=30, pady=10)
        
        info_text = f"Table: {order['table_name']}\nServer: {order['user_name']}\nDate: {order['closed_at']}"
        ctk.CTkLabel(info_frame, text=info_text, font=Style.BODY_FONT,
                     text_color=Style.TEXT, justify="left").pack(padx=20, pady=15)
        
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
        
        total_frame = ctk.CTkFrame(detail_dialog, fg_color=Style.CARD_BG, corner_radius=10)
        total_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(total_frame, text=f"Total: ${order['total']:.2f}", 
                     font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=15)

    def _export_data(self):
        if not pd or not openpyxl:
            messagebox.showerror("Missing Libraries", "Pandas and OpenPyXL are required for this feature.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Excel Export",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=f"DineDash_Export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        if not filepath:
            return

        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Top Products
                top_products = self.db.get_top_products(limit=1000)
                pd.DataFrame(top_products).to_excel(writer, sheet_name='Top Products', index=False)
                
                # Staff Performance
                staff_perf = self.db.get_staff_performance()
                pd.DataFrame(staff_perf).to_excel(writer, sheet_name='Staff Performance', index=False)
                
                # Raw Sales Data
                raw_data = self.db.get_complete_order_history()
                pd.DataFrame(raw_data).to_excel(writer, sheet_name='Raw Sales Data', index=False)
            
            messagebox.showinfo("✅ Success", f"Data exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("❌ Export Error", f"An error occurred during export: {str(e)}")
