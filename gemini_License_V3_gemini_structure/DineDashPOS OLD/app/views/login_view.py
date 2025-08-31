import customtkinter as ctk
from app.utils.style import Style

class LoginScreen(ctk.CTkFrame):
    """The view for user profile selection and login."""
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Style.BACKGROUND)
        self.controller = controller
        self.db = controller.get_db()
        
        main_frame = ctk.CTkFrame(self, fg_color=Style.FRAME_BG, corner_radius=25)
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.7)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(pady=(40, 30), padx=40, fill="x")
        
        ctk.CTkLabel(header_frame, text="Welcome to Iqbal Zaika", 
                     font=Style.TITLE_FONT, text_color=Style.ACCENT).pack()
        ctk.CTkLabel(header_frame, text="Select your profile to continue", 
                     font=Style.BODY_FONT, text_color=Style.TEXT_MUTED).pack(pady=(10, 0))
        
        users_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        users_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        users = self.db.get_users()
        for user in users:
            color = Style.ADMIN if user['role'] == "Admin" else Style.ACCENT
            hover_color = "#a855f7" if user['role'] == "Admin" else Style.ACCENT_HOVER
            
            user_card = ctk.CTkFrame(users_frame, fg_color=Style.CARD_BG, corner_radius=15)
            user_card.pack(pady=10, fill="x", ipady=20)
            
            icon = "👑" if user['role'] == "Admin" else "👨‍🍳"
            
            user_btn = ctk.CTkButton(user_card, 
                                     text=f"{icon} {user['username']}\n{user['role']}", 
                                     font=Style.BUTTON_FONT, fg_color=color,
                                     hover_color=hover_color, height=60,
                                     command=lambda u=user: self.login(u))
            user_btn.pack(expand=True, fill="x", padx=20, pady=10)

    def login(self, user):
        """Sets the current user in the controller and switches to the table view."""
        self.controller.current_user = user
        self.controller.show_frame("TableScreen")

    def refresh(self):
        # This can be used to reload users if they are managed dynamically in the future
        pass
