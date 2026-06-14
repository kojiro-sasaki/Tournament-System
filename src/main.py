import customtkinter as ctk
from gui.views.login_view import LoginWindow
from gui.views.register_view import RegisterWindow
from gui.views.admin_view import AdminWindow
from gui.views.team_view import TeamWindow
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tournament Management System")
        self.geometry("400x500")
        self.resizable(False, False) 
        self.center_window()
        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")  
        self.show_login_screen()

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginWindow(
            self, 
            on_login_success=self.handle_login_success,
            on_go_to_register=self.show_register_screen
        )

    def show_login_screen(self):
        self.geometry("400x500")
        self.center_window()
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginWindow(
            self, 
            on_login_success=self.handle_login_success,
            on_go_to_register=self.show_register_screen
        )


    def handle_login_success(self, user):
        print(f"Zalogowano: {user}")

        self.geometry("1000x600")

        for widget in self.winfo_children():widget.destroy()

        if user["username"].lower() == "aaa":
            self.main_frame = AdminWindow(self,on_logout=self.show_login_screen)
        else:
            self.main_frame = TeamWindow(self,current_user=user,username=user["username"],on_logout=self.show_login_screen)
        self.main_frame.pack(fill="both", expand=True)

    def handle_register_success(self, username):
        print(f"Zarejestrowano pomyślnie użytkownika: {username}")
        self.show_login_screen()

if __name__ == "__main__":
    app = App()
    app.mainloop()
