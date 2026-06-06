import customtkinter as ctk

class LoginWindow(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        
        self.on_login_success = on_login_success
        
        self.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = ctk.CTkLabel(master=self, text="Log in", font=("Roboto", 24, "bold"))
        self.label.pack(pady=12, padx=10)

        self.entry_username = ctk.CTkEntry(master=self, placeholder_text="Username")
        self.entry_username.pack(pady=12, padx=10)
        self.entry_password = ctk.CTkEntry(master=self, placeholder_text="Password", show="*")
        self.entry_password.pack(pady=12, padx=10)

        self.button_login = ctk.CTkButton(master=self, text="Log in", command=self.login_event)
        self.button_login.pack(pady=12, padx=10)




    def login_event(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        
        print(f"Attempt login: {username}")
        
        if username != "" and password != "":
            self.on_login_success(username)
        else:
            print("Please enter username and password!")