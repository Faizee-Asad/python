import customtkinter as ctk
from utils.styles import COLORS, FONTS

class LoginView:
    def _init_(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color=COLORS['bg_primary'])
        container.pack(fill="both", expand=True)
        
        # Login card
        card = ctk.CTkFrame(container, fg_color=COLORS['bg_tertiary'], corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center", width=600, height=600)
        
        # Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(pady=(40, 30))
        
        title = ctk.CTkLabel(header_frame, text="🍽 Welcome to DineDash",
                            font=('SF Pro Display', 32, 'bold'),
                            text_color=COLORS['accent_green'])
        title.pack()
        
        subtitle = ctk.CTkLabel(header_frame, text="Select your profile to continue",
                               font=FONTS['body'], text_color=COLORS['text_secondary'])
        subtitle.pack(pady=(10, 0))
        
        # User cards container
        users_frame = ctk.CTkFrame(card, fg_color="transparent")
        users_frame.pack(fill="both", expand=True, padx=40)
        
        # Get users from database
        cursor = self.controller.db.cursor
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        for user in users:
            self.create_user_card(users_frame, user)
    
    def create_user_card(self, parent, user):
        # User card
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], 
                           corner_radius=15, height=80)
        card.pack(fill="x", pady=8)
        
        # Special styling for admin
        if user['role'] == 'Administrator':
            card.configure(border_width=2, border_color=COLORS['accent_purple'])
        
        # User button
        user_btn = ctk.CTkButton(card, text=f"{'👑' if user['role'] == 'Administrator' else '👨‍🍳'} {user['username'].title()}\n{user['role']}",
                                font=FONTS['subheading'], fg_color="transparent",
                                hover_color=COLORS['bg_tertiary'], height=70,
                                command=lambda: self.quick_login(user['username']))
        user_btn.pack(fill="both", expand=True, padx=5, pady=5)
    
    def quick_login(self, username):
        # For demo purposes, using default password
        # In production, you'd have proper authentication
        if username == 'admin':
            self.controller.login(username, 'admin123')
        else:
            self.controller.login(username, 'pass123')