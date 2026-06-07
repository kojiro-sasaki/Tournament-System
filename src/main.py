import customtkinter as ctk
from gui.views.login_view import LoginWindow
from gui.views.register_view import RegisterWindow

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

    def show_register_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.register_frame = RegisterWindow(
            self,
            on_register_success=self.handle_register_success,
            on_back_to_login=self.show_login_screen
        )

    def handle_login_success(self, username):
        print(f"Zalogowano pomyślnie użytkownika: {username}")

    def handle_register_success(self, username):
        print(f"Zarejestrowano pomyślnie użytkownika: {username}")
        self.show_login_screen()

if __name__ == "__main__":
    app = App()
    app.mainloop()