import tkinter as tk
from main_page import MainPage, InventoryPage, TransactionPage, AnalysisPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POS System")
        self.geometry("800x700")

        # Make window responsive
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")

        self.frames = {}
        for F in (MainPage, InventoryPage, TransactionPage, AnalysisPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, page):
        self.frames[page].tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
