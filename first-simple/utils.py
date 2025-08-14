import os
from datetime import datetime

def format_currency(amount):
    """Format currency with ₹ symbol."""
    return f"₹{amount:.2f}"

def print_bill(cart, total):
    """Generate and save bill as text file."""
    now = datetime.now()
    bill_no = now.strftime("%Y%m%d%H%M%S")
    filename = f"data/receipts/bill_{bill_no}.txt"

    os.makedirs("data/receipts", exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== Restaurant POS Bill ===\n")
        f.write(f"Bill No: {bill_no}\n")
        f.write(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("---------------------------\n")
        for item in cart:
            f.write(f"{item[1]}  -  {format_currency(item[2])}\n")
        f.write("---------------------------\n")
        f.write(f"TOTAL: {format_currency(total)}\n")
        f.write("===========================\n")
        f.write("Thank you for visiting!\n")

    return os.path.abspath(filename)
