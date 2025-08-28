import customtkinter as ctk
from tkinter import messagebox
from pos_app.database.db_manager import DBManager
from pos_app.gui.main_window import MainWindow
from PIL import Image, ImageTk
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
ICON_PATH = os.path.join(BASE_DIR, "assets", "icon.ico")


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant POS - Admin Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # set window icon (works only on Windows)
        try:
            self.root.iconbitmap(ICON_PATH)
        except:
            pass

        # CustomTkinter appearance
        ctk.set_appearance_mode("dark")  # "light", "dark", "system"
        ctk.set_default_color_theme("green")  # blue, dark-blue, green

        self.db = DBManager()

        # ---------- Frame ----------
        frame = ctk.CTkFrame(root, corner_radius=15)
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        # ---------- Logo ----------
        try:
            img = Image.open(LOGO_PATH).resize((100, 100))
            self.logo = ImageTk.PhotoImage(img)
            logo_label = ctk.CTkLabel(frame, image=self.logo, text="")
            logo_label.pack(pady=15)
        except:
            ctk.CTkLabel(frame, text="🍽️ POS System", font=("Arial", 22, "bold")).pack(pady=20)

        # ---------- Username ----------
        self.username = ctk.CTkEntry(frame, placeholder_text="Username", width=250, height=40)
        self.username.pack(pady=10)

        # ---------- Password ----------
        self.password = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250, height=40)
        self.password.pack(pady=10)

        # ---------- Login Button ----------
        login_btn = ctk.CTkButton(
            frame,
            text="Login",
            width=250,
            height=40,
            fg_color="#27AE60",
            hover_color="#219150",
            command=self.login
        )
        login_btn.pack(pady=20)

    def login(self):
        user = self.username.get()
        pwd = self.password.get()

        if self.db.validate_admin(user, pwd):
            self.root.destroy()
            main_root = ctk.CTk()  # use CTk window instead of tk.Tk
            MainWindow(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")
