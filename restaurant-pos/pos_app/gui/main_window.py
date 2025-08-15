import tkinter as tk
from pos_app.utils.constants import APP_TITLE, WINDOW_SIZE

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)

        tk.Label(root, text="POS Main Window", font=("Arial", 18)).pack(pady=20)
        tk.Button(root, text="Exit", command=root.quit).pack(pady=10)
