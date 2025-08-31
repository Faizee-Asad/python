import customtkinter as ctk
from controllers.app_controller import AppController
from database import Database
from utils.styles import COLORS

class DineDashPOS:
    def _init_(self):
        # Initialize database
        self.db = Database()
        
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("DineDash POS System")
        self.root.geometry("1400x800")
        self.root.configure(fg_color=COLORS['bg_primary'])
        
        # Center window on screen
        self.center_window()
        
        # Initialize app controller
        self.controller = AppController(self.root, self.db)
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def run(self):
        self.root.mainloop()
        self.db.close()

if _name_ == "_main_":
    app = DineDashPOS()
    app.run()