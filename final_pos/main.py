import tkinter as tk
from ui.main_ui import POSUI
from database.db_manager import DBManager

# Initialize Database with default menu if empty
db = DBManager()
if not db.get_menu_items():
    db.insert_menu_item("Pizza", 8.5)
    db.insert_menu_item("Burger", 5.0)
    db.insert_menu_item("Coke", 2.0)

# Start Tkinter App
root = tk.Tk()
app = POSUI(root)
root.mainloop()
