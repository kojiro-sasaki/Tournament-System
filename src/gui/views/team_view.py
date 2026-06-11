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
