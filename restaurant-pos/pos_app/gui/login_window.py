import tkinter as tk
from tkinter import messagebox
from pos_app.database.db_manager import DBManager
from pos_app.gui.main_window import MainWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")
        self.db = DBManager()

        tk.Label(root, text="Username").pack(pady=5)
        self.username = tk.Entry(root)
        self.username.pack()

        tk.Label(root, text="Password").pack(pady=5)
        self.password = tk.Entry(root, show="*")
        self.password.pack()

        tk.Button(root, text="Login", command=self.login).pack(pady=10)

    def login(self):
        user = self.username.get()
        pwd = self.password.get()

        if self.db.validate_admin(user, pwd):
            self.root.destroy()
            main_root = tk.Tk()
            MainWindow(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")
