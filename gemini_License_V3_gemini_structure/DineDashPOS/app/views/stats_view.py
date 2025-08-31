import customtkinter as ctk
from app.utils.style import Style
from datetime import datetime

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except (ImportError, ModuleNotFoundError):
    plt = None
    FigureCanvasTkAgg = None

class StatsScreen(ctk.CTkFrame):
    """
    Admin-only screen for viewing a live dashboard of restaurant activity.
    Displays key performance indicators and charts that update automatically.
    """
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
        
        ctk.CTkButton(
            header_content, text="← Back", font=Style.BUTTON_FONT,
            fg_color=Style.SECONDARY, command=self.go_back
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_content, text="📊 Live Dashboard", font=Style.TITLE_FONT,
            text_color=Style.ACCENT
        ).pack(side="left", padx=20)
        
        self.last_update_label = ctk.CTkLabel(
            header_content, text="", font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED
        )
        self.last_update_label.pack(side="right")
        
        # Main content grid for stat cards
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        for i in range(3):
            self.content_frame.grid_columnconfigure(i, weight=1)
        
        # Create stat cards
        self.create_stat_cards()
        
        # Charts section
        self.charts_frame = ctk.CTkFrame(self.content_frame, fg_color=Style.FRAME_BG, corner_radius=15)
        self.charts_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=20)
        self.charts_frame.grid_rowconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(1, weight=1)

    def create_stat_cards(self):
        """Initializes all the key performance indicator (KPI) card widgets."""
        self.revenue_card = self.create_stat_card(0, 0, "💰 Today's Revenue", "$0.00", Style.SUCCESS)
        self.orders_card = self.create_stat_card(0, 1, "📋 Active Orders", "0", Style.WARNING)
        self.tables_card = self.create_stat_card(0, 2, "🪑 Tables Occupied", "0/0", Style.ACCENT)
        self.avg_order_card = self.create_stat_card(1, 0, "💵 Avg Order Value", "$0.00", Style.ADMIN)
        self.top_product_card = self.create_stat_card(1, 1, "🏆 Top Product Today", "N/A", Style.SECONDARY)
        self.staff_card = self.create_stat_card(1, 2, "👥 Staff Active", "0", Style.DANGER)

    def create_stat_card(self, row, col, title, initial_value, color):
        """Helper function to create a consistent stat card widget."""
        card = ctk.CTkFrame(self.content_frame, fg_color=Style.CARD_BG, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        title_frame = ctk.CTkFrame(card, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(title_frame, text=title, font=Style.BUTTON_FONT, text_color=Style.TEXT_MUTED).pack(side="left")
        
        value_label = ctk.CTkLabel(card, text=initial_value, font=("SF Pro Display", 28, "bold"), text_color=color)
        value_label.pack(pady=(0, 20))
        
        progress_frame = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2)
        progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        return {"value_label": value_label}

    def refresh(self):
        """Called when the screen is shown. Starts the auto-update loop."""
        self.update_stats()
        self.start_auto_update()

    def update_stats(self):
        """Fetches fresh data and updates all widgets on the dashboard."""
        try:
            # --- UPDATED LINE ---
            stats = self.db.analytics.get_live_stats()
            
            self.revenue_card["value_label"].configure(text=f"${stats['today_revenue']:.2f}")
            self.orders_card["value_label"].configure(text=str(stats['active_orders']))
            self.tables_card["value_label"].configure(text=f"{stats['occupied_tables']}/{stats['total_tables']}")
            self.avg_order_card["value_label"].configure(text=f"${stats['avg_order_value']:.2f}")
            self.top_product_card["value_label"].configure(text=stats.get('top_product_today') or "N/A")
            self.staff_card["value_label"].configure(text=str(stats['active_staff']))
            
            self.last_update_label.configure(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
            self.update_charts(stats)
        except Exception as e:
            print(f"Error updating stats: {e}")

    def update_charts(self, stats):
        """Redraws the charts with the latest statistics."""
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        if not plt:
            ctk.CTkLabel(self.charts_frame, text="Charts require matplotlib library", font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).grid(row=0, column=0, columnspan=2, pady=50)
            return
        
        self.create_hourly_sales_chart(stats.get('hourly_sales', {}))
        self.create_category_chart(stats.get('category_distribution', {}))

    def create_hourly_sales_chart(self, hourly_data):
        """Creates and embeds the hourly sales line chart."""
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=Style.FRAME_BG)
        ax.set_facecolor(Style.FRAME_BG)
        
        if hourly_data:
            hours, sales = list(hourly_data.keys()), list(hourly_data.values())
            ax.plot(hours, sales, color=Style.ACCENT, linewidth=2, marker='o')
            ax.fill_between(hours, sales, alpha=0.3, color=Style.ACCENT)
            ax.set_xlabel('Hour', color=Style.TEXT)
            ax.set_ylabel('Sales ($)', color=Style.TEXT)
            ax.set_title('Sales by Hour', color=Style.TEXT, fontsize=14)
        else:
            ax.text(0.5, 0.5, 'No sales data for today', ha='center', va='center', transform=ax.transAxes, color=Style.TEXT_MUTED)
        
        ax.tick_params(colors=Style.TEXT)
        for spine in ax.spines.values(): spine.set_color(Style.TEXT_MUTED)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def create_category_chart(self, category_data):
        """Creates and embeds the category distribution pie chart."""
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=Style.FRAME_BG)
        ax.set_facecolor(Style.FRAME_BG)
        
        if category_data:
            categories, values = list(category_data.keys()), list(category_data.values())
            colors = [Style.SUCCESS, Style.WARNING, Style.ACCENT, Style.ADMIN]
            
            wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors[:len(categories)],
                                              autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            for text in texts: text.set_color(Style.TEXT)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Sales by Category', color=Style.TEXT, fontsize=14)
        else:
            ax.text(0.5, 0.5, 'No category data for today', ha='center', va='center', transform=ax.transAxes, color=Style.TEXT_MUTED)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def start_auto_update(self):
        """Starts the periodic update loop."""
        self.update_job = self.after(5000, self.auto_update)

    def auto_update(self):
        """The function that runs periodically to update stats."""
        self.update_stats()
        self.update_job = self.after(5000, self.auto_update)

    def go_back(self):
        """Stops the update loop and returns to the table screen."""
        self.stop_auto_update()
        self.controller.show_frame("TableScreen")

    def stop_auto_update(self):
        """Cancels the scheduled auto-update job."""
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None

