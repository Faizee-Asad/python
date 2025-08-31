import customtkinter as ctk
from tkinter import messagebox
from app.utils.style import Style
from app.utils.image_manager import ImageManager
from datetime import datetime

try:
    from escpos.printer import Usb
except (ImportError, ModuleNotFoundError):
    Usb = None
import os

class OrderScreen(ctk.CTkFrame):
    """
    The main screen for taking and managing customer orders.
    It displays the menu, the current order details, and handles payment.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        self.current_category = None
        self.current_order_details = {}
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Menu
        menu_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0)
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.grid_rowconfigure(2, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)
        
        # Menu header
        menu_header = ctk.CTkFrame(menu_frame, fg_color="transparent", height=60)
        menu_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        menu_header.pack_propagate(False)
        
        ctk.CTkButton(
            menu_header, text="← Back to Tables", font=Style.BUTTON_FONT, 
            fg_color=Style.SECONDARY,
            command=lambda: controller.show_frame("TableScreen")
        ).pack(side="left")
        
        self.table_label = ctk.CTkLabel(menu_header, text="", font=Style.HEADER_FONT, text_color=Style.ACCENT)
        self.table_label.pack(side="right")
        
        # Category tabs
        self.category_frame = ctk.CTkScrollableFrame(
            menu_frame, fg_color="transparent", 
            orientation="horizontal", height=60
        )
        self.category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Menu items grid
        self.menu_items_frame = ctk.CTkScrollableFrame(menu_frame, fg_color=Style.BACKGROUND)
        self.menu_items_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Right panel - Order
        order_frame = ctk.CTkFrame(self, fg_color=Style.CARD_BG, corner_radius=0)
        order_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        order_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)
        
        # Order header
        order_header = ctk.CTkFrame(order_frame, fg_color="transparent", height=60)
        order_header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        order_header.pack_propagate(False)
        
        ctk.CTkLabel(
            order_header, text="🛒 Current Order", font=Style.HEADER_FONT, 
            text_color=Style.TEXT
        ).pack()
        
        # Order items
        self.order_items_frame = ctk.CTkScrollableFrame(order_frame, fg_color=Style.FRAME_BG)
        self.order_items_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        # Totals and actions
        self.totals_frame = ctk.CTkFrame(order_frame, fg_color="transparent")
        self.totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.totals_frame.grid_columnconfigure(1, weight=1)
        
        self.subtotal_label = self.create_total_row(self.totals_frame, 0, "Subtotal")
        self.tax_label = self.create_total_row(self.totals_frame, 1, "Tax (10%)")
        self.total_label = self.create_total_row(self.totals_frame, 2, "💰 Total", Style.HEADER_FONT)
        
        # Action buttons
        self.settle_button = ctk.CTkButton(
            self.totals_frame, text="💳 Settle & Pay", font=Style.BUTTON_FONT, 
            fg_color=Style.SUCCESS, height=50, command=self.settle_order
        )
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        
        self.print_button = ctk.CTkButton(
            self.totals_frame, text="🖨️ Print Receipt", font=Style.BUTTON_FONT, 
            fg_color=Style.ACCENT, height=50, command=self.print_receipt
        )

    def create_total_row(self, parent, row, text, font=Style.BODY_FONT):
        ctk.CTkLabel(
            parent, text=text, font=font, text_color=Style.TEXT
        ).grid(row=row, column=0, sticky="w", pady=5)
        label = ctk.CTkLabel(parent, text="$0.00", font=font, text_color=Style.TEXT)
        label.grid(row=row, column=1, sticky="e", pady=5)
        return label

    def refresh(self):
        """Refreshes the entire order screen when it becomes visible."""
        if not self.controller.selected_table_id:
            return
        
        self.table_label.configure(text=f"🍽️ {self.controller.selected_table_name}")
        
        # --- UPDATED LOGIC ---
        order = self.db.orders.get_open_order_for_table(self.controller.selected_table_id)
        if order:
            self.controller.current_order_id = order['id']
        else:
            self.controller.current_order_id = self.db.orders.create_order(
                self.controller.selected_table_id, self.controller.current_user['id']
            )
        
        self._set_pre_payment_state()
        self.load_categories()
        self.load_order_items()

    def load_categories(self, is_enabled=True):
        """Loads and displays product category tabs."""
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        # --- UPDATED LINE ---
        categories = self.db.crud.get_product_categories()
        if not categories:
            return
            
        self.current_category = categories[0]
        
        icons = {"Appetizers": "🥗", "Mains": "🍽️", "Desserts": "🍰", "Drinks": "🥤"}
        for category in categories:
            icon = icons.get(category, "🍴")
            
            btn = ctk.CTkButton(
                self.category_frame, text=f"{icon} {category}", font=Style.BUTTON_FONT,
                fg_color=Style.ACCENT if category == self.current_category else Style.FRAME_BG,
                command=lambda c=category: self.set_category(c)
            )
            btn.pack(side="left", padx=8, pady=5)
            
            if not is_enabled:
                btn.configure(state="disabled")
        
        self.load_menu_items(is_enabled=is_enabled)

    def set_category(self, category):
        """Handles category tab selection."""
        self.current_category = category
        self.load_categories()
        self.load_menu_items()

    def load_menu_items(self, is_enabled=True):
        """Loads and displays menu items for the selected category."""
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        # --- UPDATED LINE ---
        all_products = self.db.crud.get_products()
        products = [p for p in all_products if p['category'] == self.current_category]
        num_columns = 3
        
        for i, product in enumerate(products):
            row, col = divmod(i, num_columns)
            
            product_card = ctk.CTkFrame(self.menu_items_frame, fg_color=Style.CARD_BG, corner_radius=15)
            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipadx=5, ipady=10)
            
            try:
                product_image = ImageManager.get_product_image(product.get('image'), (120, 120))
                if product_image:
                    image_label = ctk.CTkLabel(product_card, image=product_image, text="")
                    image_label.pack(pady=(10, 5))
                    image_label.image = product_image
            except Exception:
                pass
            
            ctk.CTkLabel(
                product_card, text=product['name'], font=Style.BUTTON_FONT, 
                text_color=Style.TEXT
            ).pack(pady=(5, 2))
            ctk.CTkLabel(
                product_card, text=f"${product['price']:.2f}", font=Style.HEADER_FONT,
                text_color=Style.ACCENT
            ).pack(pady=(0, 10))
            
            add_btn = ctk.CTkButton(
                product_card, text="+ Add to Order", fg_color=Style.SUCCESS, 
                hover_color=Style.ACCENT_HOVER,
                command=lambda p=product: self.add_to_order(p)
            )
            add_btn.pack(pady=(0, 10), padx=10, fill="x")
            if not is_enabled:
                add_btn.configure(state="disabled")
        
        for i in range(num_columns):
            self.menu_items_frame.grid_columnconfigure(i, weight=1)

    def add_to_order(self, product):
        """Adds a product to the current order."""
        if not self.controller.current_order_id:
            return
        
        # --- UPDATED LINE ---
        self.db.orders.add_order_item(
            self.controller.current_order_id, product['id'], 1, product['price']
        )
        self.load_order_items()

    def load_order_items(self, is_editable=True):
        """Loads and displays items for the current order."""
        for widget in self.order_items_frame.winfo_children():
            widget.destroy()
        
        if not self.controller.current_order_id:
            return
        
        # --- UPDATED LINE ---
        order_items = self.db.orders.get_order_items(self.controller.current_order_id)
        
        if not order_items:
            ctk.CTkLabel(
                self.order_items_frame, text="No items in order", font=Style.BODY_FONT,
                text_color=Style.TEXT_MUTED
            ).pack(pady=50)
        
        subtotal = 0
        for item in order_items:
            item_frame = ctk.CTkFrame(self.order_items_frame, fg_color=Style.BACKGROUND, corner_radius=10)
            item_frame.pack(fill="x", pady=5, padx=5)
            
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(details_frame, text=item['product_name'], font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(
                details_frame, text=f"${item['price_at_time']:.2f} × {item['quantity']} = ${item['price_at_time'] * item['quantity']:.2f}",
                font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED
            ).pack(anchor="w")
            
            if is_editable:
                controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                controls_frame.pack(side="right", padx=10)
                
                ctk.CTkButton(controls_frame, text="-", width=30, height=30, fg_color=Style.DANGER, hover_color="#c92a2a",
                              command=lambda i=item: self.update_quantity(i, -1)).pack(side="left", padx=2)
                ctk.CTkLabel(controls_frame, text=str(item['quantity']), font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(side="left", padx=10)
                ctk.CTkButton(controls_frame, text="+", width=30, height=30, fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
                              command=lambda i=item: self.update_quantity(i, 1)).pack(side="left", padx=2)
            
            subtotal += item['price_at_time'] * item['quantity']
        
        tax = subtotal * 0.10
        total = subtotal + tax
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.tax_label.configure(text=f"${tax:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        
        self.current_order_details = {"items": order_items, "subtotal": subtotal, "tax": tax, "total": total}

    def update_quantity(self, item, delta):
        """Updates the quantity of an item in the order."""
        # --- UPDATED LINE ---
        self.db.orders.update_order_item_quantity(item['id'], delta)
        self.load_order_items()

    def settle_order(self):
        """Finalizes and closes the current order."""
        if not self.controller.current_order_id:
            return
        
        if not self.current_order_details.get("items"):
            messagebox.showwarning("⚠️ Empty Order", "Cannot settle an empty order.")
            return
        
        if messagebox.askyesno("💳 Confirm Payment", "Has the customer paid for this order?"):
            # --- UPDATED LINE ---
            self.db.orders.close_order(self.controller.current_order_id)
            self._set_post_payment_state()
            messagebox.showinfo("✅ Success", "Order settled successfully!")

    def _set_pre_payment_state(self):
        """Sets the UI to the state before an order is paid."""
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        self.print_button.grid_forget()

    def _set_post_payment_state(self):
        """Sets the UI to the state after an order is paid, allowing for reprints."""
        self.settle_button.grid_forget()
        self.print_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        self.load_categories(is_enabled=False)
        self.load_order_items(is_editable=False)

    def print_receipt(self):
        """Prints the receipt for the just-settled order."""
        receipt_details = self.current_order_details.copy()
        receipt_details["table_name"] = self.controller.selected_table_name
        receipt_details["user_name"] = self.controller.current_user['username']
        receipt_details["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._print_receipt_logic(receipt_details)

    def _print_receipt_logic(self, receipt_details, is_reprint=False):
        """Formats and prints a receipt, with a fallback to saving as a text file."""
        receipt_text = self._format_receipt(receipt_details, is_reprint)
        
        # Try to print to a connected USB thermal printer
        if Usb:
            try:
                # You may need to change these vendor and product IDs for your specific printer
                printer = Usb(0x04b8, 0x0202) 
                printer.text(receipt_text)
                printer.cut()
                if not is_reprint:
                    messagebox.showinfo("🖨️ Success", "Receipt sent to printer!")
                return
            except Exception:
                pass # Fallback to saving file if printer not found
        
        # Fallback: Save to a text file
        try:
            receipts_dir = os.path.join(os.path.expanduser("~"), "DineDashPOS", "receipts")
            os.makedirs(receipts_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{timestamp}.txt"
            filepath = os.path.join(receipts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            
            messagebox.showinfo("🖨️ Receipt Saved", f"No printer found.\nReceipt saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("❌ Print Error", f"Failed to print or save receipt: {str(e)}")

    def _format_receipt(self, details, is_reprint=False):
        """Formats the receipt details into a string for printing."""
        lines = []
        center = lambda s, w=40: s.center(w)
        
        lines.append(center("=" * 10))
        lines.append(center("DINEDASH RESTAURANT"))
        lines.append(center("Premium Dining Experience"))
        lines.append(center("=" * 10))
        lines.append("")
        
        if is_reprint:
            lines.append(center("*** REPRINT ***"))
            lines.append("")
        
        lines.append(f"Date: {details['timestamp']}")
        lines.append(f"Table: {details['table_name']}")
        lines.append(f"Server: {details['user_name']}")
        lines.append("-" * 40)
        
        for item in details['items']:
            name = item['product_name'][:18]
            qty_price = f"{item['quantity']}x ${item['price_at_time']:.2f}"
            total = f"${item['quantity'] * item['price_at_time']:.2f}"
            lines.append(f"{name:<18} {qty_price:>10} {total:>10}")
            
        lines.append("-" * 40)
        lines.append(f"{'Subtotal:':<30}{f'${details['subtotal']:.2f}':>10}")
        lines.append(f"{'Tax (10%):':<30}{f'${details['tax']:.2f}':>10}")
        lines.append("=" * 40)
        lines.append(f"{'TOTAL:':<30}{f'${details['total']:.2f}':>10}")
        lines.append("=" * 40)
        lines.append("")
        lines.append(center("Thank you for dining with us!"))
        lines.append(center("Visit us again soon!"))
        lines.append("\n\n")
        
        return "\n".join(lines)

