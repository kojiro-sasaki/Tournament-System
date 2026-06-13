import customtkinter as ctk
from auth_backend import register_user
from auth_backend.auth_service import RegistrationError

class RegisterWindow(ctk.CTkFrame):
    def __init__(self, master, on_register_success, on_back_to_login):
        super().__init__(master)
        
        self.on_register_success = on_register_success
        self.on_back_to_login = on_back_to_login
        
        self.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(master=self, text="Create an Account", font=("Roboto", 24, "bold"))
        self.label.pack(pady=12, padx=10)

        self.entry_email = ctk.CTkEntry(master=self, placeholder_text="Email", height=40)
        self.entry_email.pack(pady=(10, 5), padx=40, fill="x")

        self.entry_username = ctk.CTkEntry(master=self, placeholder_text="Username", height=40)
        self.entry_username.pack(pady=5, padx=40, fill="x")
        
        self.entry_password = ctk.CTkEntry(master=self, placeholder_text="Password", show="*", height=40)
        self.entry_password.pack(pady=5, padx=40, fill="x")

        self.entry_confirm_password = ctk.CTkEntry(master=self, placeholder_text="Confirm Password", show="*", height=40)
        self.entry_confirm_password.pack(pady=(5, 15), padx=40, fill="x")

        self.button_register = ctk.CTkButton(master=self, text="Register", command=self.register_event, height=40)
        self.button_register.pack(pady=(15, 10), padx=40, fill="x")
        
        self.button_back = ctk.CTkButton(master=self, text="Back to Login", command=self.on_back_to_login, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), height=40)
        self.button_back.pack(pady=(0, 10), padx=40, fill="x")

        self.error_label = ctk.CTkLabel(master=self, text="", text_color="#ff4c4c", font=("Roboto", 12))
        self.error_label.pack(pady=5)

    def register_event(self):
        email = self.entry_email.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        confirm_password = self.entry_confirm_password.get()
        
        self.error_label.configure(text="")
        
        if not all([email, username, password, confirm_password]):
            self.error_label.configure(text="Please fill all fields!")
            return
            
        if password != confirm_password:
            self.error_label.configure(text="Passwords do not match!")
            return
        
        try:
            register_user(email, username, password)
            self.error_label.configure(text="")
            self.on_register_success(username)
        except RegistrationError as e:
            self.error_label.configure(text=str(e))
