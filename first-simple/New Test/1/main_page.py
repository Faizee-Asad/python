import tkinter as tk
import os

# Placeholder constants
BACKGROUND_FRAME_COLOR = "#dddddd"
BUTTON_AND_LABEL_COLOR = "#ffffff"
FONT = ("Arial", 12)
discount_added = []

# Placeholder functions
def update_all_transaction_df():
    print("Updating all transaction DataFrame...")

def update_inventory_df():
    print("Updating inventory DataFrame...")

def update_excel_files():
    print("Updating Excel files...")

# Placeholder pages
class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Inventory Page", font=FONT).pack()

class TransactionPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Transaction Page", font=FONT).pack()

class AnalysisPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Analysis Page", font=FONT).pack()

# Main Page view
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Canvas
        canvas = tk.Canvas(self, height=700, width=800)
        canvas.pack()

        # Background Label (image in background)
        try:
            self.bgImg = tk.PhotoImage(file='background.png')
            bg_label = tk.Label(self, image=self.bgImg)
            bg_label.place(relheight=1, relwidth=1, anchor='nw')
        except Exception:
            self.bgImg = None
            self.config(bg="lightblue")

        # Middle Frame
        frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        frame.place(relx=0.125, rely=0.2, relheight=0.5, relwidth=0.75)

        # Inventory Button
        try:
            self.inventory_btn_image = tk.PhotoImage(file='supplier.png')
        except Exception:
            self.inventory_btn_image = None
        inventory_btn = tk.Button(frame, padx=24, image=self.inventory_btn_image,
                                  text="Access/Update\nInventory", compound="top",
                                  bg=BUTTON_AND_LABEL_COLOR, font=FONT,
                                  command=lambda: controller.show_frame(InventoryPage))
        inventory_btn.place(relx=0.02, rely=0.05, relheight=0.9, relwidth=0.4)

        # Transaction Button
        try:
            self.transaction_btn_image = tk.PhotoImage(file='card-machine.png')
        except Exception:
            self.transaction_btn_image = None
        transaction_btn = tk.Button(frame, image=self.transaction_btn_image, compound="top",
                                    bg=BUTTON_AND_LABEL_COLOR,
                                    command=lambda: [controller.show_frame(TransactionPage),
                                                     discount_added.clear()])
        transaction_btn.place(relx=0.58, rely=0.05, relheight=0.9, relwidth=0.4)

        # See all transactions button
        try:
            self.see_trans_img = tk.PhotoImage(file='transactions_file.png')
        except Exception:
            self.see_trans_img = None
        see_trans_btn = tk.Button(self, image=self.see_trans_img, bg='#a2f78b', compound="top",
                                  text="Transactions", command=lambda: os.startfile('Transactions.xlsx'))
        see_trans_btn.place(relx=0.9, rely=0.25, relheight=0.1, relwidth=0.1)

        # See all inventory button
        try:
            self.see_inv_img = tk.PhotoImage(file='inventory_pic.png')
        except Exception:
            self.see_inv_img = None
        see_inv_btn = tk.Button(self, image=self.see_inv_img, bg='#bdd6ff', compound="top",
                                text="Inventory", command=lambda: os.startfile('Inventory.xlsx'))
        see_inv_btn.place(relx=0.9, rely=0.35, relheight=0.1, relwidth=0.1)

        # Analysis button
        analysis_frame = tk.Frame(self, bg=BACKGROUND_FRAME_COLOR)
        analysis_frame.place(relx=0.25, rely=0.7, relheight=0.15, relwidth=0.5)
        analysis_btn = tk.Button(analysis_frame, text='Show Analysis', bg=BUTTON_AND_LABEL_COLOR,
                                 font=FONT, command=lambda: [update_all_transaction_df(),
                                                             update_inventory_df(),
                                                             update_excel_files(),
                                                             controller.show_frame(AnalysisPage)])
        analysis_btn.place(relx=0.25, rely=0.2, relheight=0.5, relwidth=0.5)

    def post_update(self):
        pass
