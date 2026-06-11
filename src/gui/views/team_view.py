import customtkinter as ctk
import datetime

BG_SIDEBAR = "#1A1A24"
BG_MAIN = "#121216"
BG_CARD = "#21212B"
COLOR_PRIMARY = "#3A7EBF"
COLOR_SUCCESS = "#2E7D32"
COLOR_DANGER = "#C62828"
COLOR_WARNING = "#E65100"
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED = "#8E9297"

class TeamWindow(ctk.CTkFrame):
    def __init__(self, master, username="Captain", on_logout=None):
        super().__init__(master, fg_color=BG_MAIN)
        self.username = username
        self.on_logout = on_logout
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # TODO: Fetch team profile belonging to this captain from database
        self.my_team = None

        # TODO: Fetch active tournaments list from database
        self.tournaments = [
            {"id": 1, "name": "CS2 Summer Masters", "game": "Counter-Strike 2", "max_teams": 16, "status": "Registration Open", "registered_teams": 12, "date": "2026-06-15"},
            {"id": 2, "name": "Dota 2 Champions Cup", "game": "Dota 2", "max_teams": 8, "status": "In Progress", "registered_teams": 8, "date": "2026-06-12"},
            {"id": 3, "name": "CS2 Kyiv Major", "game": "Counter-Strike 2", "max_teams": 8, "status": "Draft", "registered_teams": 4, "date": "2026-07-01"}
        ]
        
        # TODO: Fetch registered tournament IDs for this team from database
        self.registered_tournaments = set()

        # TODO: Fetch matches list from database
        self.matches = [
            {"id": 1, "tournament_id": 2, "round": "Quarterfinals", "team1": "Natus Vincere", "team2": "Virtus.pro", "score1": 2, "score2": 0, "status": "Finished", "time": "14:00"},
            {"id": 2, "tournament_id": 2, "round": "Quarterfinals", "team1": "Team Spirit", "team2": "G2 Esports", "score1": 2, "score2": 1, "status": "Finished", "time": "16:30"},
            {"id": 3, "tournament_id": 2, "round": "Quarterfinals", "team1": "Team Liquid", "team2": "Fnatic", "score1": 1, "score2": 2, "status": "Finished", "time": "19:00"},
            {"id": 4, "tournament_id": 2, "round": "Quarterfinals", "team1": "FaZe Clan", "team2": "Team Vitality", "score1": 0, "score2": 0, "status": "In Progress", "time": "21:30"},
            {"id": 5, "tournament_id": 2, "round": "Semifinals", "team1": "Natus Vincere", "team2": "Team Spirit", "score1": 0, "score2": 0, "status": "Scheduled", "time": "Tomorrow 15:00"},
            {"id": 6, "tournament_id": 2, "round": "Semifinals", "team1": "Fnatic", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled", "time": "Tomorrow 18:00"},
            {"id": 7, "tournament_id": 2, "round": "Finals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled", "time": "June 14, 20:00"}
        ]
        
        self.selected_tournament_id = 2
        
        self.mock_members = ["Player1", "Player2", "Player3", "Player4"]

        self.sidebar_frame = None
        self.sidebar_buttons = {}
        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_tab = None
        self.select_tab("Dashboard")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        brand_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Tournament System", 
            font=("Roboto", 18, "bold"), 
            text_color=TEXT_PRIMARY
        )
        brand_label.grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")

        role_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="TEAM MANAGER PANEL", 
            font=("Roboto", 11, "bold"), 
            text_color=COLOR_PRIMARY
        )
        role_label.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        tabs = [
            ("Dashboard", "🏠  Dashboard"),
            ("My Team", "👥  My Team"),
            ("Tournaments", "🏆  Tournaments"),
            ("Bracket", "📊  Bracket")
        ]

        for idx, (tab_name, display_text) in enumerate(tabs):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=display_text,
                anchor="w",
                font=("Roboto", 13),
                height=40,
                fg_color="transparent",
                text_color=TEXT_PRIMARY,
                hover_color="#272738",
                corner_radius=8,
                command=lambda name=tab_name: self.select_tab(name)
            )
            btn.grid(row=idx + 2, column=0, padx=10, pady=4, sticky="ew")
            self.sidebar_buttons[tab_name] = btn

        logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪  Log Out",
            anchor="w",
            font=("Roboto", 13),
            height=40,
            fg_color="transparent",
            text_color="#FF6B6B",
            hover_color="#3A1C1C",
            corner_radius=8,
            command=self.on_logout
        )
        logout_btn.grid(row=6, column=0, padx=10, pady=25, sticky="ew")

    def select_tab(self, tab_name):
        if self.current_tab == tab_name:
            return

        for name, btn in self.sidebar_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY)
            else:
                btn.configure(fg_color="transparent", hover_color="#272738")

        self.current_tab = tab_name

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tab_name == "Dashboard":
            self.show_dashboard_tab()
        elif tab_name == "My Team":
            self.show_my_team_tab()
        elif tab_name == "Tournaments":
            self.show_tournaments_tab()
        elif tab_name == "Bracket":
            self.show_bracket_tab()

    def show_dashboard_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        header_label = ctk.CTkLabel(tab_frame, text=f"Welcome, {self.username}!", font=("Roboto", 24, "bold"), text_color=TEXT_PRIMARY)
        header_label.pack(anchor="w", pady=(0, 20))

        info_panel = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        info_panel.pack(fill="both", expand=True)

        title = ctk.CTkLabel(info_panel, text="Team Status Overview", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        title.pack(anchor="w", padx=20, pady=(15, 10))

        status_text = "No team registered yet. Go to 'My Team' to create one."
        if self.my_team:
            status_text = f"Your team '{self.my_team['name']} [{self.my_team['tag']}]' is active.\n" \
                          f"You have registered for {len(self.registered_tournaments)} tournament(s)."

        desc_lbl = ctk.CTkLabel(info_panel, text=status_text, font=("Roboto", 14), text_color=TEXT_PRIMARY, justify="left")
        desc_lbl.pack(anchor="w", padx=20, pady=10)

