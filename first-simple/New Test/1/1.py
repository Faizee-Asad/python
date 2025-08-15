import tkinter as tk
from tkinter import ttk
from datetime import datetime

# ----------------------
# Main App Window
# ----------------------
root = tk.Tk()
root.title("POS System")
root.geometry("1000x600")
root.configure(bg="black")

# ----------------------
# Top Bar - Waiters & Burgers
# ----------------------
top_frame = tk.Frame(root, bg="gray20", height=50)
top_frame.pack(fill="x")

for i in range(1, 12):
    if i % 2 == 0:
        text = f"S{i}"
    else:
        text = "🍔"
    tk.Button(top_frame, text=text, bg="gray30", fg="white", width=6, height=2).pack(side="left", padx=2, pady=2)

# Date/Time
date_label = tk.Label(top_frame, text=datetime.now().strftime("%d %b %Y %H:%M"), fg="white", bg="gray20", font=("Arial", 12))
date_label.pack(side="right", padx=10)

# ----------------------
# Main Content
# ----------------------
main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

# Left Frame - Order List
left_frame = tk.Frame(main_frame, bg="black", width=400)
left_frame.pack(side="left", fill="y", padx=5, pady=5)

# Table
columns = ("Item", "Price", "Qty")
tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(pady=5)

# Add example items
items = [
    ("Grape Stomping-Kids", 90, 1),
    ("Cheese Cherry Pineapple", 150, 1),
    ("Sula Mango Wine Spritzers", 195, 1),
]
for item in items:
    tree.insert("", "end", values=item)

# Total price
total_label = tk.Label(left_frame, text="529.00", fg="yellow", bg="black", font=("Arial", 24, "bold"))
total_label.pack(pady=10)

# Quantity buttons
qty_frame = tk.Frame(left_frame, bg="black")
qty_frame.pack()
tk.Button(qty_frame, text="-", font=("Arial", 14), width=3, bg="red", fg="white").pack(side="left", padx=5)
tk.Button(qty_frame, text="+", font=("Arial", 14), width=3, bg="green", fg="white").pack(side="left", padx=5)

# ----------------------
# Right Frame - Menu Buttons
# ----------------------
right_frame = tk.Frame(main_frame, bg="black")
right_frame.pack(side="right", fill="both", expand=True)

menu_items = [
    "Assorted Cheese Platter", "Assorted Munchies", "Cheddar Cheese", "Cheese Cherry Pineapple",
    "Cheese, Fruit And Nuts Platter", "Choco-Walnut Brownie", "Dips with Crackers", "Dried fruits and Nuts",
    "Fresh Cut Mango With Ice Cream", "Fruit Juice", "Goat Cheese", "Gouda Cheese",
    "Grape Stomping", "Grape Stomping-Kids", "Green And Black Olives", "Iced Tea",
    "Italian Cold Cut Platter", "Khakra With Chutney", "Lavazza Cappuccino", "Lavazza Espresso Shot"
]

row, col = 0, 0
for name in menu_items:
    tk.Button(right_frame, text=name, width=25, height=2, bg="gray30", fg="white").grid(row=row, column=col, padx=3, pady=3)
    col += 1
    if col > 3:
        col = 0
        row += 1

root.mainloop()
