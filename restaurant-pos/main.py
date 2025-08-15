import tkinter as tk
from pos_app.database.db_manager import DBManager
from pos_app.gui.login_window import LoginWindow

if __name__ == "__main__":
    db = DBManager()
    db.create_tables()

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
