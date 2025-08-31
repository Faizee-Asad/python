import customtkinter as ctk
import os

# --- Core Application Logic ---
from app.core.database import Database

# --- User Interface Views ---
from app.views.license_view import LicenseScreen
from app.views.login_view import LoginScreen
from app.views.table_view import TableScreen
from app.views.order_view import OrderScreen
from app.views.settings_view import SettingsScreen
from app.views.reports_view import ReportsScreen
from app.views.stats_view import StatsScreen

# --- Utilities ---
from app.utils.style import Style

class App(ctk.CTk):
    """
    The main application controller. This class is responsible for creating the main
    window, managing all the different screens (frames), and handling the
    flow of the application from one screen to another.
    """
    def __init__(self):
        super().__init__()
        self.title("DineDash POS - Premium Restaurant Management")
        self.geometry("1400x900")
        self.configure(fg_color=Style.BACKGROUND)
        ctk.set_appearance_mode("dark")
        
        # --- Application State ---
        self.db = Database()
        self.current_user = None
        self.current_order_id = None
        self.selected_table_id = None
        self.selected_table_name = None

        # --- Frame Management ---
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Iterate over all screen classes and create an instance of each
        for F in (LicenseScreen, LoginScreen, TableScreen, OrderScreen, 
                  SettingsScreen, ReportsScreen, StatsScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.check_license()

    def check_license(self):
        """Checks the license status and shows the appropriate first screen."""
        status = self.db.get_setting('license_status')
        if status == 'licensed':
            self.show_frame("LoginScreen")
        else:
            self.show_frame("LicenseScreen")

    def show_frame(self, page_name):
        """Brings the specified frame to the top of the view."""
        frame = self.frames[page_name]
        frame.tkraise()
        # If the frame has a 'refresh' method, call it to update its data
        if hasattr(frame, 'refresh'):
            frame.refresh()

    def get_db(self):
        """Provides access to the database instance for all frames."""
        return self.db

def main():
    """The main function to set up and run the application."""
    # Set DPI awareness for better scaling on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    
    # Create necessary application directories in the user's home folder
    home_dir = os.path.expanduser("~")
    app_dir = os.path.join(home_dir, "DineDashPOS")
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "receipts"), exist_ok=True)
    os.makedirs(os.path.join(app_dir, "exports"), exist_ok=True)
    
    # Create and run the application
    app = App()
    
    # Center the window on the screen upon launch
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f'{width}x{height}+{x}+{y}')
    
    app.minsize(1200, 800)
    
    app.mainloop()

if __name__ == "__main__":
    main()
