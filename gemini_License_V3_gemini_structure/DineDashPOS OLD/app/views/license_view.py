import customtkinter as ctk
from tkinter import messagebox
from app.utils.style import Style
from app.core.licensing import LicenseManager

class LicenseScreen(ctk.CTkFrame):
    """The view for software license activation."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()

        main_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=20)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.6)

        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(40, 20), padx=40, fill="x")
        
        ctk.CTkLabel(title_frame, text="🍽️ DineDash", font=("SF Pro Display", 36, "bold"), 
                     text_color=Style.ACCENT).pack()
        ctk.CTkLabel(title_frame, text="Premium POS System", font=Style.HEADER_FONT, 
                     text_color=Style.TEXT_MUTED).pack(pady=(5, 0))

        activation_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        activation_frame.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkLabel(activation_frame, text="Software Activation Required", 
                     font=Style.HEADER_FONT, text_color=Style.TEXT).pack(pady=(0, 10))
        ctk.CTkLabel(activation_frame, text="Enter your license key to unlock all features", 
                     font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(0, 30))

        self.key_entry = ctk.CTkEntry(activation_frame, width=350, height=40, font=Style.BODY_FONT,
                                      placeholder_text="Enter license key here...")
        self.key_entry.pack(pady=10)

        activate_btn = ctk.CTkButton(activation_frame, text="🔓 Activate License", 
                                     font=Style.BUTTON_FONT, fg_color=Style.SUCCESS,
                                     hover_color=Style.ACCENT_HOVER, height=45,
                                     command=self.activate_license)
        activate_btn.pack(pady=20)

    def activate_license(self):
        """Validates the entered license key and activates the software."""
        entered_key = self.key_entry.get().strip()
        if LicenseManager.validate_license_key(entered_key):
            self.db.set_setting('license_status', 'licensed')
            messagebox.showinfo("🎉 Success", "Software activated successfully!\nWelcome to DineDash POS!")
            self.controller.show_frame("LoginScreen")
        else:
            messagebox.showerror("❌ Activation Failed", "Invalid license key. Please check and try again.")
