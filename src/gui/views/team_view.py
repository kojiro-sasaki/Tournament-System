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

    def show_my_team_tab(self):
        tab_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        if self.my_team is None:
            # Show Registration Form
            form_panel = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
            form_panel.pack(pady=20, padx=20, fill="x")

            form_label = ctk.CTkLabel(form_panel, text="Register Your Team", font=("Roboto", 18, "bold"), text_color=TEXT_PRIMARY)
            form_label.pack(anchor="w", padx=20, pady=(20, 15))

            ctk.CTkLabel(form_panel, text="Team Name", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
            self.team_name_entry = ctk.CTkEntry(form_panel, placeholder_text="e.g. Natus Vincere", height=35)
            self.team_name_entry.pack(fill="x", padx=20, pady=(0, 10))

            ctk.CTkLabel(form_panel, text="Team Tag", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
            self.team_tag_entry = ctk.CTkEntry(form_panel, placeholder_text="e.g. NAVI", height=35)
            self.team_tag_entry.pack(fill="x", padx=20, pady=(0, 10))

            ctk.CTkLabel(form_panel, text="Region", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
            self.team_region_entry = ctk.CTkEntry(form_panel, placeholder_text="e.g. Europe", height=35)
            self.team_region_entry.pack(fill="x", padx=20, pady=(0, 10))

            ctk.CTkLabel(form_panel, text="Description", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
            self.team_desc_text = ctk.CTkEntry(form_panel, placeholder_text="Brief details about the team...", height=35)
            self.team_desc_text.pack(fill="x", padx=20, pady=(0, 20))

            self.team_error_lbl = ctk.CTkLabel(form_panel, text="", text_color="#FF4C4C", font=("Roboto", 12))
            self.team_error_lbl.pack(pady=(0, 5))

            # TODO: Create team profile (INSERT INTO teams)
            add_btn = ctk.CTkButton(form_panel, text="Create Team Profile", command=self.create_my_team, fg_color=COLOR_PRIMARY, hover_color="#2E6299", height=40, corner_radius=8)
            add_btn.pack(fill="x", padx=20, pady=(0, 20))
        else:
            # Show Team Info Profile
            profile = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
            profile.pack(pady=20, padx=20, fill="x")

            lbl = ctk.CTkLabel(profile, text="Team Profile", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
            lbl.pack(anchor="w", padx=20, pady=(20, 15))

            name_lbl = ctk.CTkLabel(profile, text=f"{self.my_team['name']} [{self.my_team['tag']}]", font=("Roboto", 18, "bold"), text_color=COLOR_PRIMARY, anchor="w")
            name_lbl.pack(fill="x", padx=20, pady=(5, 2))

            ctk.CTkLabel(profile, text="Region:", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(10, 2))
            reg_lbl = ctk.CTkLabel(profile, text=self.my_team["region"], font=("Roboto", 14), text_color=TEXT_PRIMARY, anchor="w")
            reg_lbl.pack(fill="x", padx=20)

            ctk.CTkLabel(profile, text="Description:", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(10, 2))
            desc_lbl = ctk.CTkLabel(profile, text=self.my_team["desc"], font=("Roboto", 13), text_color=TEXT_PRIMARY, anchor="w", justify="left", wraplength=400)
            desc_lbl.pack(fill="x", padx=20)

            # TODO: Edit team profile (UPDATE teams)
            edit_btn = ctk.CTkButton(profile, text="Edit Team Info", fg_color="#34495E", hover_color="#2C3E50", height=32, corner_radius=6, command=self.open_edit_team_dialog)
            edit_btn.pack(padx=20, pady=25, anchor="w")

    def create_my_team(self):
        name = self.team_name_entry.get().strip()
        tag = self.team_tag_entry.get().strip()
        region = self.team_region_entry.get().strip()
        desc = self.team_desc_text.get().strip()

        self.team_error_lbl.configure(text="")

        if not name or not tag or not region:
            self.team_error_lbl.configure(text="Please fill in Name, Tag, and Region!")
            return

        self.my_team = {
            "name": name,
            "tag": tag,
            "region": region,
            "desc": desc if desc else "No description provided."
        }
        self.current_tab = None
        self.select_tab("My Team")

    def open_edit_team_dialog(self):
        self.edit_dialog = ctk.CTkFrame(self.content_frame, fg_color="rgba(10, 10, 15, 0.8)")
        self.edit_dialog.place(relx=0, rely=0, relwidth=1, relheight=1)

        dialog = ctk.CTkFrame(self.edit_dialog, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color="#3E3E52", width=420, height=380)
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)

        title = ctk.CTkLabel(dialog, text="Edit Team Info", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        title.pack(pady=15)

        ctk.CTkLabel(dialog, text="Team Name", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        self.edit_name = ctk.CTkEntry(dialog, height=35)
        self.edit_name.insert(0, self.my_team["name"])
        self.edit_name.pack(fill="x", padx=30)

        ctk.CTkLabel(dialog, text="Region", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        self.edit_region = ctk.CTkEntry(dialog, height=35)
        self.edit_region.insert(0, self.my_team["region"])
        self.edit_region.pack(fill="x", padx=30)

        ctk.CTkLabel(dialog, text="Description", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        self.edit_desc = ctk.CTkEntry(dialog, height=35)
        self.edit_desc.insert(0, self.my_team["desc"])
        self.edit_desc.pack(fill="x", padx=30, pady=(0, 15))

        footer = ctk.CTkFrame(dialog, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=20, padx=30)

        cancel = ctk.CTkButton(footer, text="Cancel", fg_color="transparent", border_width=1, border_color="#555566", hover_color="#2C2C35", height=32, corner_radius=6, command=self.close_edit_dialog)
        cancel.pack(side="left", fill="x", expand=True, padx=(0, 5))

        save = ctk.CTkButton(footer, text="Save Changes", fg_color=COLOR_PRIMARY, hover_color="#2E6299", height=32, corner_radius=6, command=self.save_team_changes)
        save.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def close_edit_dialog(self):
        if hasattr(self, 'edit_dialog') and self.edit_dialog:
            self.edit_dialog.destroy()
            self.edit_dialog = None

    def save_team_changes(self):
        self.my_team["name"] = self.edit_name.get().strip()
        self.my_team["region"] = self.edit_region.get().strip()
        self.my_team["desc"] = self.edit_desc.get().strip()
        self.close_edit_dialog()
        self.show_my_team_tab()

    def show_tournaments_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        tab_frame.grid_columnconfigure(0, weight=5)
        tab_frame.grid_columnconfigure(1, weight=5)
        tab_frame.grid_rowconfigure(0, weight=1)

        # Left list: Available Tournaments
        left = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        left.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        lbl = ctk.CTkLabel(left, text="Active Tournaments", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        lbl.pack(anchor="w", padx=20, pady=(20, 15))

        self.t_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.t_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Right pane: Matches for chosen tournament
        right = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        right.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        lbl_matches = ctk.CTkLabel(right, text="Tournament Match Schedule", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        lbl_matches.pack(anchor="w", padx=20, pady=(20, 15))

        self.m_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.m_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        self.refresh_tournaments_list()
        self.refresh_matches_list()

    def refresh_tournaments_list(self):
        for widget in self.t_scroll.winfo_children():
            widget.destroy()

        for t in self.tournaments:
            card = ctk.CTkFrame(self.t_scroll, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A35")
            card.pack(fill="x", pady=5, padx=5)

            details = ctk.CTkFrame(card, fg_color="transparent")
            details.pack(fill="x", padx=15, pady=(10, 5))

            # Bind clicking on card to view match schedule
            card.bind("<Button-1>", lambda event, tid=t["id"]: self.select_tournament(tid))
            details.bind("<Button-1>", lambda event, tid=t["id"]: self.select_tournament(tid))

            name = ctk.CTkLabel(details, text=t["name"], font=("Roboto", 13, "bold"), text_color=TEXT_PRIMARY, anchor="w")
            name.pack(fill="x")

            game = ctk.CTkLabel(details, text=f"{t['game']} • Date: {t['date']}", font=("Roboto", 11), text_color=TEXT_MUTED, anchor="w")
            game.pack(fill="x")

            status_color = COLOR_WARNING if t["status"] == "Draft" else (COLOR_PRIMARY if t["status"] == "Registration Open" else (COLOR_SUCCESS if t["status"] == "In Progress" else COLOR_DANGER))
            badge = ctk.CTkLabel(card, text=f"  {t['status'].upper()}  ", font=("Roboto", 9, "bold"), text_color=TEXT_PRIMARY, fg_color=status_color, corner_radius=6, height=18)
            badge.pack(side="left", padx=15, pady=(0, 10))

            # Sign Up Button
            if t["status"] == "Registration Open":
                if t["id"] in self.registered_tournaments:
                    signed_lbl = ctk.CTkLabel(card, text="Registered ✔", font=("Roboto", 11, "bold"), text_color=COLOR_SUCCESS)
                    signed_lbl.pack(side="right", padx=15, pady=(0, 10))
                else:
                    sign_btn = ctk.CTkButton(
                        card, 
                        text="Sign Up", 
                        font=("Roboto", 10, "bold"), 
                        height=22, 
                        width=65, 
                        fg_color=COLOR_PRIMARY, 
                        hover_color="#2E6299", 
                        corner_radius=6,
                        command=lambda tid=t["id"]: self.signup_for_tournament(tid)
                    )
                    sign_btn.pack(side="right", padx=15, pady=(0, 10))

    def select_tournament(self, tournament_id):
        self.selected_tournament_id = tournament_id
        self.refresh_matches_list()

    def signup_for_tournament(self, tournament_id):
        if self.my_team is None:
            # Alert user
            self.select_tab("My Team")
            return
        
        # TODO: Sign up team for tournament (INSERT INTO tournament_registrations)
        self.registered_tournaments.add(tournament_id)
        # Update registered teams count locally
        for t in self.tournaments:
            if t["id"] == tournament_id:
                t["registered_teams"] += 1
                break
        self.refresh_tournaments_list()

