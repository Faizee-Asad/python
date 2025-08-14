import tkinter as tk
from main_page import MainPage, InventoryPage, TransactionPage, AnalysisPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("POS System")
        self.geometry("800x700")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainPage, InventoryPage, TransactionPage, AnalysisPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
