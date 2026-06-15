import customtkinter as ctk
from services.login_service import LoginService
from database.repositories.repository import AccountRepository


class LoginWindow(ctk.CTkFrame):
    def __init__(self, master, on_login_success=None, on_go_to_register=None):
        super().__init__(master) 

        self.on_login_success = on_login_success
        self.on_go_to_register = on_go_to_register
        self.login_service = LoginService(AccountRepository())

        self.pack(pady=20, padx=20, fill="both", expand=True)

        self.label = ctk.CTkLabel(master=self, text="Log in", font=("Roboto", 24, "bold"))
        self.label.pack(pady=12, padx=10)

        self.entry_username = ctk.CTkEntry(master=self, placeholder_text="Username", height=40)
        self.entry_username.pack(pady=(20, 10), padx=40, fill="x")
        self.entry_username.bind("<Return>", lambda event: self.login_event())

        self.entry_password = ctk.CTkEntry(master=self, placeholder_text="Password", show="*", height=40)
        self.entry_password.pack(pady=10, padx=40, fill="x")
        self.entry_password.bind("<Return>", lambda event: self.login_event())

        self.button_login = ctk.CTkButton(master=self, text="Log in", command=self.login_event, height=40)
        self.button_login.pack(pady=(20, 10), padx=40, fill="x")

        self.button_register = ctk.CTkButton(master=self, text="Don't have an account? Register",
                                             command=self.on_go_to_register, fg_color="transparent", border_width=2,
                                             text_color=("gray10", "#DCE4EE"), height=40)
        self.button_register.pack(pady=(0, 10), padx=40, fill="x")

        self.error_label = ctk.CTkLabel(master=self, text="", text_color="#ff4c4c", font=("Roboto", 12))
        self.error_label.pack(pady=5)

    def login_event(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        self.error_label.configure(text="")

        if username == "" or password == "":
            self.error_label.configure(text="Please enter username and password!")
            return

        try:
            user = self.login_service.login(username, password)

            if user:
                self.on_login_success(user)
            else:
                self.error_label.configure(text="Invalid username or password!")
        except Exception as e:
            self.error_label.configure(text="Connection error. Try again.")
            print(f"Login error: {e}")
