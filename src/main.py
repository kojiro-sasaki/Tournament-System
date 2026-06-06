import customtkinter as ctk
from gui.views.login_view import LoginWindow

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tournament Management System")
        self.geometry("400x500")

        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")  
        self.show_login_screen()

    def show_login_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginWindow(self, on_login_success=self.handle_login_success)

    def handle_login_success(self, username):
        print(f"Zalogowano pomyślnie użytkownika: {username}")

if __name__ == "__main__":
    app = App()
    app.mainloop()