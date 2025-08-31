import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import os
from app.utils.style import Style
from app.utils.image_manager import ImageManager

# The printing library is optional and handled with a try-except block
try:
    from escpos.printer import Usb
except (ImportError, ModuleNotFoundError):
    Usb = None

class OrderScreen(ctk.CTkFrame):
    """The view for creating, managing, and finalizing a customer's order."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        self.current_category = None
        self.current_order_details = {}
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left Panel: Menu
        menu_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=0)
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.grid_rowconfigure(2, weight=1)
        menu_frame.grid_columnconfigure(0, weight=1)
        
        self._create_menu_widgets(menu_frame)
        
        # Right Panel: Order Summary
        order_frame = ctk.CTkFrame(self, fg_color=Style.CARD_BG, corner_radius=0)
        order_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        order_frame.grid_rowconfigure(1, weight=1)
        order_frame.grid_columnconfigure(0, weight=1)

        self._create_order_widgets(order_frame)

    def _create_menu_widgets(self, parent):
        """Initializes all widgets for the menu panel."""
        menu_header = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        menu_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        menu_header.pack_propagate(False)
        
        ctk.CTkButton(menu_header, text="← Back to Tables", 
                      font=Style.BUTTON_FONT, fg_color=Style.SECONDARY,
                      command=lambda: self.controller.show_frame("TableScreen")).pack(side="left")
        
        self.table_label = ctk.CTkLabel(menu_header, text="", font=Style.HEADER_FONT, text_color=Style.ACCENT)
        self.table_label.pack(side="right")
        
        self.category_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", 
                                                     orientation="horizontal", height=60)
        self.category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.menu_items_frame = ctk.CTkScrollableFrame(parent, fg_color=Style.BACKGROUND)
        self.menu_items_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    def _create_order_widgets(self, parent):
        """Initializes all widgets for the order summary panel."""
        order_header = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        order_header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        order_header.pack_propagate(False)
        
        ctk.CTkLabel(order_header, text="🛒 Current Order", font=Style.HEADER_FONT, 
                     text_color=Style.TEXT).pack()
        
        self.order_items_frame = ctk.CTkScrollableFrame(parent, fg_color=Style.FRAME_BG)
        self.order_items_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        
        self.totals_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.totals_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.totals_frame.grid_columnconfigure(1, weight=1)
        
        self.subtotal_label = self._create_total_row(self.totals_frame, 0, "Subtotal")
        self.tax_label = self._create_total_row(self.totals_frame, 1, "Tax (10%)")
        self.total_label = self._create_total_row(self.totals_frame, 2, "💰 Total", Style.HEADER_FONT)
        
        self.settle_button = ctk.CTkButton(self.totals_frame, text="💳 Settle & Pay", 
                                           font=Style.BUTTON_FONT, fg_color=Style.SUCCESS,
                                           height=50, command=self.settle_order)
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        
        self.print_button = ctk.CTkButton(self.totals_frame, text="🖨️ Print Receipt", 
                                          font=Style.BUTTON_FONT, fg_color=Style.ACCENT,
                                          height=50, command=self.print_receipt)

    def _create_total_row(self, parent, row, text, font=Style.BODY_FONT):
        ctk.CTkLabel(parent, text=text, font=font, text_color=Style.TEXT).grid(
            row=row, column=0, sticky="w", pady=5)
        label = ctk.CTkLabel(parent, text="$0.00", font=font, text_color=Style.TEXT)
        label.grid(row=row, column=1, sticky="e", pady=5)
        return label

    def refresh(self):
        if not self.controller.selected_table_id:
            return
        
        self.table_label.configure(text=f"🍽️ {self.controller.selected_table_name}")
        
        order = self.db.get_open_order_for_table(self.controller.selected_table_id)
        if order:
            self.controller.current_order_id = order['id']
        else:
            self.controller.current_order_id = self.db.create_order(
                self.controller.selected_table_id, self.controller.current_user['id'])
        
        self._set_pre_payment_state()
        self.load_categories()
        self.load_order_items(is_editable=True)

    def load_categories(self, is_enabled=True):
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        categories = self.db.get_product_categories()
        if not categories:
            return

        if self.current_category not in categories:
            self.current_category = categories[0]
            
        icons = {"Appetizers": "🥗", "Mains": "🍽️", "Desserts": "🍰", "Drinks": "🥤"}
        for category in categories:
            icon = icons.get(category, "🍴")
            
            fg_color = Style.ACCENT if category == self.current_category else Style.FRAME_BG
            btn = ctk.CTkButton(self.category_frame, text=f"{icon} {category}",
                                font=Style.BUTTON_FONT, fg_color=fg_color,
                                command=lambda c=category: self.set_category(c))
            btn.pack(side="left", padx=8, pady=5)
            
            if not is_enabled:
                btn.configure(state="disabled")
        
        self.load_menu_items(is_enabled=is_enabled)

    def set_category(self, category):
        self.current_category = category
        self.load_categories()

    def load_menu_items(self, is_enabled=True):
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        products = [p for p in self.db.get_products() if p['category'] == self.current_category]
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
            
            ctk.CTkLabel(product_card, text=product['name'], font=Style.BUTTON_FONT, 
                         text_color=Style.TEXT).pack(pady=(5, 2))
            ctk.CTkLabel(product_card, text=f"${product['price']:.2f}", 
                         font=Style.HEADER_FONT, text_color=Style.ACCENT).pack(pady=(0, 10))
            
            add_btn = ctk.CTkButton(product_card, text="+ Add to Order",
                                    fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
                                    command=lambda p=product: self.add_to_order(p))
            add_btn.pack(pady=(0, 10), padx=10, fill="x")
            if not is_enabled:
                add_btn.configure(state="disabled")
        
        for i in range(num_columns):
            self.menu_items_frame.grid_columnconfigure(i, weight=1)

    def add_to_order(self, product):
        if not self.controller.current_order_id:
            return
        
        self.db.add_item_to_order(self.controller.current_order_id, product['id'], 1, product['price'])
        self.load_order_items(is_editable=True)

    def load_order_items(self, is_editable=True):
        for widget in self.order_items_frame.winfo_children():
            widget.destroy()
        
        if not self.controller.current_order_id:
            return
        
        order_items = self.db.get_order_items(self.controller.current_order_id)
        
        if not order_items:
            ctk.CTkLabel(self.order_items_frame, text="No items in order", 
                         font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=50)
        
        subtotal = 0
        for item in order_items:
            item_frame = ctk.CTkFrame(self.order_items_frame, fg_color=Style.BACKGROUND, corner_radius=10)
            item_frame.pack(fill="x", pady=5, padx=5)
            
            details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            details_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(details_frame, text=item['product_name'], 
                         font=Style.BUTTON_FONT, text_color=Style.TEXT).pack(anchor="w")
            ctk.CTkLabel(details_frame, text=f"${item['price_at_time']:.2f} × {item['quantity']} = ${item['price_at_time'] * item['quantity']:.2f}", 
                         font=Style.SMALL_FONT, text_color=Style.TEXT_MUTED).pack(anchor="w")
            
            if is_editable:
                controls_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                controls_frame.pack(side="right", padx=10)
                
                ctk.CTkButton(controls_frame, text="-", width=30, height=30,
                              fg_color=Style.DANGER, hover_color="#c92a2a",
                              command=lambda i=item['id'], q=item['quantity']: self.update_quantity(i, q - 1)).pack(side="left", padx=2)
                
                qty_label = ctk.CTkLabel(controls_frame, text=str(item['quantity']), 
                                         font=Style.BUTTON_FONT, text_color=Style.TEXT)
                qty_label.pack(side="left", padx=10)
                
                ctk.CTkButton(controls_frame, text="+", width=30, height=30,
                              fg_color=Style.SUCCESS, hover_color=Style.ACCENT_HOVER,
                              command=lambda i=item['id'], q=item['quantity']: self.update_quantity(i, q + 1)).pack(side="left", padx=2)
            
            subtotal += item['price_at_time'] * item['quantity']
        
        tax = subtotal * 0.10
        total = subtotal + tax
        
        self.subtotal_label.configure(text=f"${subtotal:.2f}")
        self.tax_label.configure(text=f"${tax:.2f}")
        self.total_label.configure(text=f"${total:.2f}")
        
        self.current_order_details = {"items": order_items, "subtotal": subtotal, "tax": tax, "total": total}

    def update_quantity(self, item_id, new_quantity):
        self.db.update_order_item_quantity(item_id, new_quantity)
        self.load_order_items(is_editable=True)

    def settle_order(self):
        if not self.controller.current_order_id or not self.current_order_details.get("items"):
            messagebox.showwarning("⚠️ Empty Order", "Cannot settle an empty order.")
            return
        
        if messagebox.askyesno("💳 Confirm Payment", f"Settle order for ${self.current_order_details['total']:.2f}?"):
            self.db.close_order(self.controller.current_order_id)
            self._set_post_payment_state()
            messagebox.showinfo("✅ Success", "Order settled successfully! You can now print the receipt.")

    def _set_pre_payment_state(self):
        self.settle_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        self.print_button.grid_forget()

    def _set_post_payment_state(self):
        self.settle_button.grid_forget()
        self.print_button.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=10, pady=(15,0))
        self.load_categories(is_enabled=False)
        self.load_order_items(is_editable=False)

    def print_receipt(self):
        receipt_details = self.current_order_details.copy()
        receipt_details["table_name"] = self.controller.selected_table_name
        receipt_details["user_name"] = self.controller.current_user['username']
        receipt_details["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._print_receipt_logic(receipt_details)

    def _print_receipt_logic(self, receipt_details, is_reprint=False):
        receipt_text = self._format_receipt(receipt_details, is_reprint)
        
        if Usb:
            try:
                printer = Usb(0x04b8, 0x0202) # Common Epson TM series
                printer.text(receipt_text)
                printer.cut()
                messagebox.showinfo("✅ Success", "Receipt sent to printer.")
                return
            except Exception as e:
                print(f"Printer error: {e}") # Log error for debugging
        
        try:
            receipts_dir = os.path.join(os.path.expanduser("~"), "DineDashPOS", "receipts")
            os.makedirs(receipts_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{timestamp}.txt"
            filepath = os.path.join(receipts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            
            messagebox.showinfo("🖨️ Receipt Saved", f"No printer found. Receipt saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("❌ Save Error", f"Failed to save receipt: {str(e)}")

    def _format_receipt(self, details, is_reprint=False):
        lines = []
        lines.append("=" * 40)
        lines.append("          DINEDASH RESTAURANT")
        lines.append("       Premium Dining Experience")
        lines.append("=" * 40)
        
        if is_reprint:
            lines.append("           *** REPRINT ***")
            lines.append("")
        
        lines.append(f"Date: {details['timestamp']}")
        lines.append(f"Table: {details['table_name']}")
        lines.pappend(f"Server: {details['user_name']}")
        lines.append("-" * 40)
        
        for item in details['items']:
            name = item['product_name'][:20].ljust(20)
            qty = str(item['quantity']).rjust(3)
            price = f"${item['price_at_time']:.2f}".rjust(7)
            total = f"${item['price_at_time'] * item['quantity']:.2f}".rjust(8)
            lines.append(f"{name} {qty} {price} {total}")
        
        lines.append("-" * 40)
        lines.append(f"Subtotal: ${details['subtotal']:.2f}".rjust(40))
        lines.append(f"Tax (10%): ${details['tax']:.2f}".rjust(40))
        lines.append("=" * 40)
        lines.append(f"TOTAL: ${details['total']:.2f}".rjust(40))
        lines.append("=" * 40)
        lines.append("")
        lines.append("      Thank you for dining with us!")
        lines.append("         Visit us again soon!")
        lines.append("\n\n")
        
        return "\n".join(lines)
