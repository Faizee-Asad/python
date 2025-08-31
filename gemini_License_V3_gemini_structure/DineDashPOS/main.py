import customtkinter as ctk
import os
from ctypes import windll

# Import the new central database manager
from app.db import DatabaseManager

# Import all the view modules
from app.views.license_view import LicenseScreen
from app.views.login_view import LoginScreen
from app.views.table_view import TableScreen
from app.views.order_view import OrderScreen
from app.views.settings_view import SettingsScreen
from app.views.reports_view import ReportsScreen
from app.views.stats_view import StatsScreen

# Import the centralized style
from app.utils.style import Style

class App(ctk.CTk):
    """
    The main application class that orchestrates the entire POS system.
    It initializes the main window, database, and all the different screens (frames),
    and manages the navigation between them.
    """
    def __init__(self, db_manager):
        super().__init__()
        self.title("DineDash POS - Premium Restaurant Management")
        self.geometry("1400x900")
        self.configure(fg_color=Style.BACKGROUND)
        ctk.set_appearance_mode("dark")
        
        # Set app icon if available
        try:
            # Note: For PyInstaller, icon path needs to be handled differently.
            # This works for local development.
            self.iconbitmap("icon.ico")
        except:
            pass

        self.db = db_manager
        self.current_user = None
        self.current_order_id = None
        self.selected_table_id = None
        self.selected_table_name = None

        # Container for all frames
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize all screen frames
        self.frames = {}
        for F in (LicenseScreen, LoginScreen, TableScreen, OrderScreen, SettingsScreen, ReportsScreen, StatsScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.check_license()
        
        # Protocol for graceful shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_license(self):
        """Checks the license status and shows the appropriate first screen."""
        status = self.db.crud.get_setting('license_status')
        if status == 'licensed':
            self.show_frame("LoginScreen")
        else:
            self.show_frame("LicenseScreen")

    def show_frame(self, page_name: str):
        """Raises the specified frame to the top."""
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'refresh'):
            frame.refresh()

    def get_db(self) -> DatabaseManager:
        """Provides access to the database manager instance."""
        return self.db
        
    def on_closing(self):
        """Handles application shutdown, ensuring database connection is closed."""
        self.db.close()
        self.destroy()

def main():
    """Main function to configure and run the application."""
    # Set DPI awareness for better scaling on Windows
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    # Initialize the database manager
    db_manager = DatabaseManager()
    
    # Create and run the app
    app = App(db_manager)
    
    # Center the window on the screen
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f'{width}x{height}+{x}+{y}')
    
    # Set a minimum window size
    app.minsize(1200, 700)
    
    # Run the application's main loop
    app.mainloop()

if __name__ == "__main__":
    main()

