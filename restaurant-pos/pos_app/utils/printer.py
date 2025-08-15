import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# For thermal printing
try:
    from escpos.printer import Usb
except ImportError:
    Usb = None

# Ensure receipts folder exists in /data/receipts relative to project root
BASE_DIR = Path(__file__).resolve().parents[2]  # Go 2 levels up from pos_app/utils
RECEIPTS_DIR = BASE_DIR / "data" / "receipts"
RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)


def print_thermal(items, total, tax, grand_total, shop_name="Restaurant POS"):
    """
    Print receipt to thermal printer via USB.
    items: list of tuples (name, price)
    """
    if Usb is None:
        raise RuntimeError("python-escpos not installed. Run: pip install python-escpos")

    try:
        # Adjust vendor/product IDs to match your printer
        p = Usb(0x0416, 0x5011, 0)  # vendor_id, product_id, interface
    except Exception as e:
        raise RuntimeError(f"Unable to connect to thermal printer: {e}")

    p.set(align="center", font="a", text_type="B")
    p.text(f"{shop_name}\n")
    p.text("=" * 32 + "\n")

    p.set(align="left", font="a")
    for name, price in items:
        p.text(f"{name:<20} {price:>8.2f}\n")

    p.text("=" * 32 + "\n")
    p.text(f"Total:       {total:.2f}\n")
    p.text(f"Tax:         {tax:.2f}\n")
    p.text(f"Grand Total: {grand_total:.2f}\n")
    p.text(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    p.cut()


def generate_pdf_bill(items, total, tax, grand_total, bill_no=None, shop_name="Restaurant POS"):
    """
    Generate a PDF receipt and save to receipts folder.
    items: list of tuples (name, price)
    """
    if bill_no is None:
        bill_no = datetime.now().strftime("%Y%m%d%H%M%S")

    pdf_path = RECEIPTS_DIR / f"bill_{bill_no}.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y, shop_name)
    y -= 40

    c.setFont("Helvetica", 12)
    for name, price in items:
        c.drawString(50, y, name)
        c.drawRightString(500, y, f"{price:.2f}")
        y -= 20
        if y < 100:  # If page is nearly full, start new page
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)

    y -= 20
    c.drawString(50, y, "Total:")
    c.drawRightString(500, y, f"{total:.2f}")
    y -= 20
    c.drawString(50, y, "Tax:")
    c.drawRightString(500, y, f"{tax:.2f}")
    y -= 20
    c.drawString(50, y, "Grand Total:")
    c.drawRightString(500, y, f"{grand_total:.2f}")

    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    c.showPage()
    c.save()

    return pdf_path
