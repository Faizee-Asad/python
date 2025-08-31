import customtkinter as ctk
from utils.styles import COLORS, FONTS

class LicenseView:
    def _init_(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color=COLORS['bg_primary'])
        container.pack(fill="both", expand=True)
        
        # Center card
        card = ctk.CTkFrame(container, fg_color=COLORS['bg_tertiary'], corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)
        
        # Logo and title
        title_label = ctk.CTkLabel(card, text="🍽 DineDash", font=('SF Pro Display', 36, 'bold'),
                                  text_color=COLORS['accent_green'])
        title_label.pack(pady=(40, 10))
        
        subtitle = ctk.CTkLabel(card, text="Premium POS System", font=FONTS['body'],
                               text_color=COLORS['text_secondary'])
        subtitle.pack()
        
        # Activation required text
        activation_label = ctk.CTkLabel(card, text="Software Activation Required", 
                                       font=FONTS['heading'], text_color=COLORS['text_primary'])
        activation_label.pack(pady=(30, 10))
        
        info_label = ctk.CTkLabel(card, text="Enter your license key to unlock all features",
                                 font=FONTS['body'], text_color=COLORS['text_secondary'])
        info_label.pack(pady=(0, 20))
        
        # License input
        self.license_entry = ctk.CTkEntry(card, width=350, height=50, 
                                         placeholder_text="Enter license key here...",
                                         font=FONTS['body'])
        self.license_entry.pack(pady=(0, 20))
        
        # Activate button
        activate_btn = ctk.CTkButton(card, text="🔓 Activate License", width=200, height=50,
                                    font=FONTS['subheading'], fg_color=COLORS['accent_green'],
                                    hover_color=COLORS['accent_green_hover'],
                                    command=self.activate_license)
        activate_btn.pack()
        
        # Demo button (for testing)
        demo_btn = ctk.CTkButton(card, text="Continue with Demo", width=150, height=30,
                                font=FONTS['small'], fg_color="transparent",
                                text_color=COLORS['text_secondary'],
                                hover_color=COLORS['bg_secondary'],
                                command=lambda: self.controller.show_login())
        demo_btn.pack(pady=(20, 0))
    
    def activate_license(self):
        license_key = self.license_entry.get()
        if self.controller.activate_license(license_key):
            # Show success message
            pass
        else:
            # Show error message
            pass    