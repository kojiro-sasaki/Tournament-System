import customtkinter as ctk
import datetime
import tkinter as tk

from database.repositories.tournament_repository import TournamentRepository
from database.repositories.team_repository import TeamRepository
from database.repositories.tournament_registration_repository import TournamentRegistrationRepository
from database.repositories.match_repository import MatchRepository
from logic.bracket_generator import generate_initial_bracket
from database.repositories.match_result_repository import MatchResultRepository

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
    def __init__(self, master, current_user, username="Captain", on_logout=None):

        super().__init__(master, fg_color=BG_MAIN)
        self.username = username
        self.on_logout = on_logout
        self.current_user = current_user

        response = TeamRepository.get_by_captain_id(
            self.current_user["id"]
        )

        self.my_team = response.data[0] if response.data else None
        if self.my_team:
            response = TournamentRegistrationRepository.get_by_team_id(
                self.my_team["id"]
            )

            self.registered_tournaments = {
                row["tournament_id"]
                for row in response.data
            }
        else:
            self.registered_tournaments = set()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # TODO: Fetch team profile belonging to this captain from database

        # TODO: Fetch active tournaments list from database
        response = TournamentRepository.get_all()

        self.tournaments = response.data
        
        # TODO: Fetch registered tournament IDs for this team from database

        try:
            resp = MatchRepository.get_all()
            raw_matches = resp.data or []
        except Exception:
            raw_matches = []

        try:
            teams_resp = TeamRepository.get_all()
            teams_list = teams_resp.data or []
            name_map = {t["id"]: t["name"] for t in teams_list}
        except Exception:
            name_map = {}

        self.matches = []
        for r in raw_matches:
            self.matches.append({
                "id": r.get("id"),
                "tournament_id": r.get("tournament_id"),
                "round": r.get("round_name") or r.get("round"),
                "team1": name_map.get(r.get("team1_id")) or r.get("team1_name") or "TBD",
                "team2": name_map.get(r.get("team2_id")) or r.get("team2_name") or "TBD",
                "score1": r.get("score1", 0),
                "score2": r.get("score2", 0),
                "status": r.get("status", "Scheduled"),
                "time": r.get("match_date") or "TBD",
            })

        self.selected_tournament_id = None
        if self.registered_tournaments:
            for t in self.tournaments:
                if t["id"] in self.registered_tournaments:
                    self.selected_tournament_id = t["id"]
                    break
        if self.selected_tournament_id is None and self.tournaments:
            self.selected_tournament_id = self.tournaments[0]["id"]

        if self.selected_tournament_id is not None:
            self._ensure_bracket_generated(self.selected_tournament_id)
        
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

            name_lbl = ctk.CTkLabel(profile, text=f"{self.my_team['name']} [{self.my_team['tag']}]",font=("Roboto", 18, "bold"), text_color=COLOR_PRIMARY, anchor="w")
            name_lbl.pack(fill="x", padx=20, pady=(5, 2))



            ctk.CTkLabel(profile, text="Description:", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(10, 2))
            desc_lbl = ctk.CTkLabel(profile, text=self.my_team["description"], font=("Roboto", 13), text_color=TEXT_PRIMARY, anchor="w", justify="left", wraplength=400)
            desc_lbl.pack(fill="x", padx=20)

            # TODO: Edit team profile (UPDATE teams)
            edit_btn = ctk.CTkButton(profile, text="Edit Team Info", fg_color="#34495E", hover_color="#2C3E50", height=32, corner_radius=6, command=self.open_edit_team_dialog)
            edit_btn.pack(padx=20, pady=25, anchor="w")

    def create_my_team(self):
        name = self.team_name_entry.get().strip()
        desc = self.team_desc_text.get().strip()

        self.team_error_lbl.configure(text="")

        if not name:
            self.team_error_lbl.configure(
                text="Please enter a team name!"
            )
            return

        try:
            tag = self.team_tag_entry.get().strip()

            response = TeamRepository.create({
                "name": name,
                "tag": tag,
                "captain_id": self.current_user["id"],
                "description": desc
            })

            self.my_team = response.data[0]

            self.current_tab = None
            self.select_tab("My Team")

        except Exception as e:
            self.team_error_lbl.configure(text=str(e))
            print(f"CREATE TEAM ERROR: {e}")

    def open_edit_team_dialog(self):
        self.edit_dialog = ctk.CTkFrame(self.content_frame, fg_color="#121216")
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

        ctk.CTkLabel(dialog, text="Team Tag", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=30,pady=(5, 2))
        self.edit_tag = ctk.CTkEntry(dialog, height=35)
        self.edit_tag.insert(0, self.my_team["tag"])
        self.edit_tag.pack(fill="x", padx=30)

        ctk.CTkLabel(dialog, text="Description", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=30, pady=(5, 2))
        self.edit_desc = ctk.CTkEntry(dialog, height=35)
        self.edit_desc.insert(0, self.my_team["description"])
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
        try:
            TeamRepository.update_by_id(
                self.my_team["id"],
                {
                    "name": self.edit_name.get().strip(),
                    "tag": self.edit_tag.get().strip(),
                    "description": self.edit_desc.get().strip()
                }
            )

            self.my_team["name"] = self.edit_name.get().strip()
            self.my_team["tag"] = self.edit_tag.get().strip()
            self.my_team["description"] = self.edit_desc.get().strip()

            self.close_edit_dialog()

            self.current_tab = None
            self.select_tab("My Team")

        except Exception as e:
            print(f"UPDATE TEAM ERROR: {e}")

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


            game_name = "Counter-Strike 2" if t["game_id"] == 1 else "Dota 2"
            game = ctk.CTkLabel(details,text=f"{game_name} • Date: {t['start_date']}",font=("Roboto", 11),text_color=TEXT_MUTED,anchor="w")
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
        self._ensure_bracket_generated(tournament_id)
        self.refresh_matches_list()

    def _load_matches(self):
        try:
            resp = MatchRepository.get_all()
            raw_matches = resp.data or []
        except Exception:
            raw_matches = []

        try:
            teams_resp = TeamRepository.get_all()
            teams_list = teams_resp.data or []
            name_map = {t["id"]: t["name"] for t in teams_list}
        except Exception:
            name_map = {}

        try:
            results_resp = MatchResultRepository.get_all()
            results_map = {r["match_id"]: r for r in (results_resp.data or [])}
        except Exception:
            results_map = {}

        self.matches = []
        for r in raw_matches:
            result = results_map.get(r.get("id"))
            self.matches.append({
                "id": r.get("id"),
                "tournament_id": r.get("tournament_id"),
                "round": r.get("round_name") or r.get("round"),
                "team1_id": r.get("team1_id"),
                "team2_id": r.get("team2_id"),
                "team1": name_map.get(r.get("team1_id")) or "TBD",
                "team2": name_map.get(r.get("team2_id")) or "TBD",
                "score1": result["score_team1"] if result else 0,
                "score2": result["score_team2"] if result else 0,
                "winner_team_id": result["winner_team_id"] if result else None,
                "status": r.get("status", "Scheduled"),
                "time": r.get("match_date") or "TBD",
            })

    def _ensure_bracket_generated(self, tournament_id):
        try:
            t_resp = TournamentRepository.get_by_id(tournament_id)
            if not (t_resp and hasattr(t_resp, "data") and t_resp.data):
                return

            max_teams = t_resp.data.get("max_teams")
            if max_teams not in (8, 16):
                return

            regs_resp = TournamentRegistrationRepository.get_all()
            regs = [r for r in (regs_resp.data or []) if r.get("tournament_id") == tournament_id]
            if len(regs) != max_teams:
                return

            existing = MatchRepository.get_by_tournament_id(tournament_id)
            if existing and existing.data:
                return

            teams = []
            for reg in regs:
                tr = TeamRepository.get_by_id(reg.get("team_id"))
                if tr and hasattr(tr, "data") and tr.data:
                    teams.append({"id": tr.data.get("id"), "name": tr.data.get("name")})

            if len(teams) != max_teams:
                return

            matches = generate_initial_bracket(tournament_id, teams, max_teams, start_match_id=1)
            for m in matches:
                if m.get("team1_id") is None or m.get("team2_id") is None:
                    continue
                MatchRepository.create({
                    "tournament_id": m["tournament_id"],
                    "team1_id": m.get("team1_id"),
                    "team2_id": m.get("team2_id"),
                    "match_date": None,
                    "status": m.get("status"),
                    "round_name": m.get("round"),
                })

            self._load_matches()
        except Exception as e:
            print(f"Bracket generation error: {e}")

    # TODO: Sign up team for tournament (INSERT INTO tournament_registrations)
    def signup_for_tournament(self, tournament_id):
        if self.my_team is None:
            self.select_tab("My Team")
            return

        try:
            TournamentRegistrationRepository.create({
                "tournament_id": tournament_id,
                "team_id": self.my_team["id"],
                "status": "registered"
            })

            self.registered_tournaments.add(tournament_id)
            self.refresh_tournaments_list()
            self._ensure_bracket_generated(tournament_id)
            if self.selected_tournament_id == tournament_id:
                self.refresh_matches_list()

        except Exception as e:
            print(f"REGISTRATION ERROR: {e}")

    def refresh_matches_list(self):
        for widget in self.m_scroll.winfo_children():
            widget.destroy()

        t_matches = [m for m in self.matches if m["tournament_id"] == self.selected_tournament_id]

        if not t_matches:
            no_lbl = ctk.CTkLabel(self.m_scroll, text="No matches scheduled.", font=("Roboto", 13), text_color=TEXT_MUTED)
            no_lbl.pack(pady=30)
            return

        for m in t_matches:
            row = ctk.CTkFrame(self.m_scroll, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A35")
            row.pack(fill="x", pady=4, padx=5)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(info, text=m["round"], font=("Roboto", 11, "bold"), text_color=COLOR_PRIMARY, anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=m["time"], font=("Roboto", 10), text_color=TEXT_MUTED, anchor="w").pack(fill="x")

            teams = ctk.CTkFrame(row, fg_color="transparent")
            teams.pack(side="left", expand=True, fill="both")
            teams.grid_columnconfigure(0, weight=1)
            teams.grid_columnconfigure(1, weight=0)
            teams.grid_columnconfigure(2, weight=1)
            teams.grid_rowconfigure(0, weight=1)

            ctk.CTkLabel(teams, text=m["team1"], font=("Roboto", 11, "bold"), text_color=TEXT_PRIMARY, anchor="e").grid(row=0, column=0, sticky="ew", padx=5)
            
            score_text = f" {m['score1']} - {m['score2']} " if m["status"] in ["Finished", "In Progress"] else " VS "
            ctk.CTkLabel(teams, text=score_text, font=("Roboto", 12, "bold"), text_color=COLOR_PRIMARY).grid(row=0, column=1)
            
            ctk.CTkLabel(teams, text=m["team2"], font=("Roboto", 11, "bold"), text_color=TEXT_PRIMARY, anchor="w").grid(row=0, column=2, sticky="ew", padx=5)

            status_color = COLOR_SUCCESS if m["status"] == "Finished" else (COLOR_PRIMARY if m["status"] == "In Progress" else TEXT_MUTED)
            status_badge = ctk.CTkLabel(row, text=m["status"].upper(), font=("Roboto", 9, "bold"), text_color=status_color)
            status_badge.pack(side="right", padx=10)

    def show_bracket_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        header = ctk.CTkLabel(tab_frame, text="Tournament Playoff Bracket (Read Only)",
                              font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        header.pack(anchor="w", pady=(0, 10))

        t_options = {t["name"]: t["id"] for t in self.tournaments}
        t_names = list(t_options.keys())
        current_name = next((k for k, v in t_options.items() if v == self.selected_tournament_id),
                            t_names[0] if t_names else "")

        sel_row = ctk.CTkFrame(tab_frame, fg_color="transparent")
        sel_row.pack(fill="x", pady=(0, 10))

        t_selector = ctk.CTkOptionMenu(
            sel_row,
            values=t_names,
            width=220,
            height=30,
            fg_color="#2A2A38",
            button_color="#3A3A4D",
            command=lambda val: self.select_bracket_tournament(t_options[val])
        )
        t_selector.set(current_name)
        t_selector.pack(side="left")

        canvas_container = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10,
                                        border_width=1, border_color="#2E2E3A")
        canvas_container.pack(fill="both", expand=True)

        from tkinter import Scrollbar
        h_scroll = Scrollbar(canvas_container, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        v_scroll = Scrollbar(canvas_container, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        self.bracket_canvas = tk.Canvas(
            canvas_container, bg=BG_CARD, highlightthickness=0,
            xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set
        )
        self.bracket_canvas.pack(side="left", fill="both", expand=True)

        h_scroll.config(command=self.bracket_canvas.xview)
        v_scroll.config(command=self.bracket_canvas.yview)

        self.bracket_canvas.bind("<MouseWheel>",
                                 lambda e: self.bracket_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.bracket_canvas.bind("<Shift-MouseWheel>",
                                 lambda e: self.bracket_canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.refresh_bracket_view()

    def select_bracket_tournament(self, tournament_id):
        self.selected_tournament_id = tournament_id
        self._load_matches()
        self._ensure_bracket_generated(tournament_id)
        self.refresh_bracket_view()

    def _draw_bracket_lines(self, canvas, positions, card_w, card_h, num_teams):
        """Rysuje linie łączące mecze w drabince"""
        LINE_COLOR = "#3A5A7A"
        LINE_WIDTH = 2

        def mid_right(x, y):
            return x + card_w, y + card_h // 2

        def mid_left(x, y):
            return x, y + card_h // 2

        def draw_connector(x1, y1, x2, y2):
            mid_x = (x1 + x2) // 2
            canvas.create_line(x1, y1, mid_x, y1, fill=LINE_COLOR, width=LINE_WIDTH)
            canvas.create_line(mid_x, y1, mid_x, y2, fill=LINE_COLOR, width=LINE_WIDTH)
            canvas.create_line(mid_x, y2, x2, y2, fill=LINE_COLOR, width=LINE_WIDTH)

        if num_teams == 16:
            for i in range(4):
                rx0, ry0 = mid_right(*positions[f"ro16_{i * 2}"])
                rx1, ry1 = mid_right(*positions[f"ro16_{i * 2 + 1}"])
                lx_qf, ly_qf = mid_left(*positions[f"qf{i}"])
                draw_connector(rx0, ry0, lx_qf, ly_qf)
                draw_connector(rx1, ry1, lx_qf, ly_qf)

        rx0, ry0 = mid_right(*positions["qf0"])
        rx1, ry1 = mid_right(*positions["qf1"])
        lx4, ly4 = mid_left(*positions["sf0"])
        draw_connector(rx0, ry0, lx4, ly4)
        draw_connector(rx1, ry1, lx4, ly4)

        if num_teams == 16:
            rx2, ry2 = mid_right(*positions["qf2"])
            rx3, ry3 = mid_right(*positions["qf3"])
            lx5, ly5 = mid_left(*positions["sf1"])
            draw_connector(rx2, ry2, lx5, ly5)
            draw_connector(rx3, ry3, lx5, ly5)
        else:
            rx2, ry2 = mid_right(*positions["qf2"])
            rx3, ry3 = mid_right(*positions["qf3"])
            lx5, ly5 = mid_left(*positions["sf1"])
            draw_connector(rx2, ry2, lx5, ly5)
            draw_connector(rx3, ry3, lx5, ly5)

        rx4, ry4 = mid_right(*positions["sf0"])
        rx5, ry5 = mid_right(*positions["sf1"])
        lx6, ly6 = mid_left(*positions["final"])
        draw_connector(rx4, ry4, lx6, ly6)
        draw_connector(rx5, ry5, lx6, ly6)

        rx6, ry6 = mid_right(*positions["final"])
        lx7, ly7 = mid_left(*positions["champion"])
        draw_connector(rx6, ry6, lx7, ly7)

    def refresh_bracket_view(self):
        if not hasattr(self, "bracket_canvas") or not self.bracket_canvas.winfo_exists():
            return

        self.bracket_canvas.delete("all")

        self._load_matches()
        t_matches = self._get_expanded_bracket_matches_for_bracket(self.selected_tournament_id)

        if not t_matches or len(t_matches) < 4:
            self.bracket_canvas.create_text(300, 80, text="No bracket matches exist for this tournament yet.",
                                            fill=TEXT_MUTED, font=("Roboto", 13))
            self.bracket_canvas.configure(scrollregion=(0, 0, 600, 160))
            return

        num_teams = 16 if len(t_matches) == 15 else 8

        PAD_X, PAD_Y = 30, 30
        CARD_W, CARD_H = 220, 100
        COL_GAP, ROW_GAP = 60, 20

        positions = {}

        if num_teams == 16:
            num_rounds = 5
            col_x = [PAD_X + i * (CARD_W + COL_GAP) for i in range(num_rounds)]

            # Round of 16
            ro16_y_step = CARD_H + ROW_GAP
            ro16_ys = [PAD_Y + i * ro16_y_step for i in range(8)]
            for i in range(8):
                self._draw_match_on_canvas(t_matches[i], self.bracket_canvas, col_x[0], ro16_ys[i], CARD_W, CARD_H)
                positions[f"ro16_{i}"] = (col_x[0], ro16_ys[i])

            # Quarterfinals
            qf_ys = [(ro16_ys[i * 2] + ro16_ys[i * 2 + 1]) / 2 for i in range(4)]
            for i in range(4):
                self._draw_match_on_canvas(t_matches[8 + i], self.bracket_canvas, col_x[1], qf_ys[i], CARD_W, CARD_H)
                positions[f"qf{i}"] = (col_x[1], qf_ys[i])

            # Semifinals
            sf_ys = [(qf_ys[0] + qf_ys[1]) / 2, (qf_ys[2] + qf_ys[3]) / 2]
            self._draw_match_on_canvas(t_matches[12], self.bracket_canvas, col_x[2], sf_ys[0], CARD_W, CARD_H)
            positions["sf0"] = (col_x[2], sf_ys[0])
            self._draw_match_on_canvas(t_matches[13], self.bracket_canvas, col_x[2], sf_ys[1], CARD_W, CARD_H)
            positions["sf1"] = (col_x[2], sf_ys[1])

            # Finals
            final_y = (sf_ys[0] + sf_ys[1]) / 2
            self._draw_match_on_canvas(t_matches[14], self.bracket_canvas, col_x[3], final_y, CARD_W, CARD_H)
            positions["final"] = (col_x[3], final_y)

            # Champion
            self._draw_champion_on_canvas(t_matches[14], self.bracket_canvas, col_x[4], final_y, CARD_W, CARD_H)
            positions["champion"] = (col_x[4], final_y)

            self._draw_bracket_lines(self.bracket_canvas, positions, CARD_W, CARD_H, num_teams)

            total_w = col_x[4] + CARD_W + PAD_X
            total_h = max(ro16_ys[7] + CARD_H, final_y + CARD_H) + PAD_Y

        else:
            num_rounds = 4
            col_x = [PAD_X + i * (CARD_W + COL_GAP) for i in range(num_rounds)]

            # Quarterfinals
            qf_y_step = CARD_H + ROW_GAP * 4
            qf_ys = [PAD_Y + i * qf_y_step for i in range(4)]
            for i in range(4):
                self._draw_match_on_canvas(t_matches[i], self.bracket_canvas, col_x[0], qf_ys[i], CARD_W, CARD_H)
                positions[f"qf{i}"] = (col_x[0], qf_ys[i])

            # Semifinals
            sf_ys = [(qf_ys[0] + qf_ys[1]) / 2, (qf_ys[2] + qf_ys[3]) / 2]
            self._draw_match_on_canvas(t_matches[4], self.bracket_canvas, col_x[1], sf_ys[0], CARD_W, CARD_H)
            positions["sf0"] = (col_x[1], sf_ys[0])
            self._draw_match_on_canvas(t_matches[5], self.bracket_canvas, col_x[1], sf_ys[1], CARD_W, CARD_H)
            positions["sf1"] = (col_x[1], sf_ys[1])

            # Finals
            final_y = (sf_ys[0] + sf_ys[1]) / 2
            self._draw_match_on_canvas(t_matches[6], self.bracket_canvas, col_x[2], final_y, CARD_W, CARD_H)
            positions["final"] = (col_x[2], final_y)

            # Champion
            self._draw_champion_on_canvas(t_matches[6], self.bracket_canvas, col_x[3], final_y, CARD_W, CARD_H)
            positions["champion"] = (col_x[3], final_y)

            self._draw_bracket_lines(self.bracket_canvas, positions, CARD_W, CARD_H, num_teams)

            total_w = col_x[3] + CARD_W + PAD_X
            total_h = max(qf_ys[3] + CARD_H, final_y + CARD_H) + PAD_Y

        self.bracket_canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def _draw_match_on_canvas(self, match, canvas, x, y, w, h):
        """Rysuje kartę meczu na canvas (tryb read-only)"""
        finished = match.get("status") == "Finished"
        border_color = "#2E8B57" if finished else "#5A2E8A"

        frame = ctk.CTkFrame(canvas, fg_color="#13131A", corner_radius=6,
                             border_width=2, border_color=border_color, width=w, height=h)
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text=match.get("round", ""), font=("Roboto", 9),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=8, pady=(4, 0))

        row1 = ctk.CTkFrame(frame, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(4, 2))
        t1_bold = "bold" if finished and match.get("score1", 0) > match.get("score2", 0) else "normal"
        ctk.CTkLabel(row1, text=match.get("team1", "TBD"), font=("Roboto", 11, t1_bold),
                     text_color=TEXT_PRIMARY).pack(side="left")
        score1 = str(match.get("score1", 0)) if finished else "-"
        ctk.CTkLabel(row1, text=score1, font=("Roboto", 11, "bold"),
                     text_color=COLOR_PRIMARY).pack(side="right")

        row2 = ctk.CTkFrame(frame, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(2, 4))
        t2_bold = "bold" if finished and match.get("score2", 0) > match.get("score1", 0) else "normal"
        ctk.CTkLabel(row2, text=match.get("team2", "TBD"), font=("Roboto", 11, t2_bold),
                     text_color=TEXT_PRIMARY).pack(side="left")
        score2 = str(match.get("score2", 0)) if finished else "-"
        ctk.CTkLabel(row2, text=score2, font=("Roboto", 11, "bold"),
                     text_color=COLOR_PRIMARY).pack(side="right")

        canvas.create_window(x, y, window=frame, anchor="nw")

    def _draw_champion_on_canvas(self, final_match, canvas, x, y, w, h):
        """Rysuje kartę mistrza na canvas"""
        winner_name = "TBD"
        if final_match.get("status") == "Finished":
            if final_match.get("score1", 0) > final_match.get("score2", 0):
                winner_name = final_match.get("team1", "TBD")
            else:
                winner_name = final_match.get("team2", "TBD")

        frame = ctk.CTkFrame(canvas, fg_color="#241B00", corner_radius=8,
                             width=w, height=h, border_width=2, border_color="#FFD700")
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text="🏆 CHAMPION", font=("Roboto", 10, "bold"),
                     text_color="#FFD700").pack(pady=(8, 0))
        ctk.CTkLabel(frame, text=winner_name, font=("Roboto", 12, "bold"),
                     text_color=TEXT_PRIMARY, wraplength=w - 20).pack(pady=(2, 8))

        canvas.create_window(x, y, window=frame, anchor="nw")

    def _get_expanded_bracket_matches_for_bracket(self, tournament_id):
        """Tworzy pełną listę meczów dla bracket (z placeholderami)"""
        if tournament_id is None:
            return []

        existing_matches = sorted(
            [m for m in self.matches if m["tournament_id"] == tournament_id],
            key=lambda x: x.get("id", 0)
        )

        def get_winner(m):
            if m.get("status") != "Finished":
                return None, "TBD"
            try:
                result = MatchResultRepository.get_by_match_id(m["id"])
                if result.data:
                    winner_id = result.data["winner_team_id"]
                    if winner_id == m.get("team1_id"):
                        return winner_id, m.get("team1", "TBD")
                    elif winner_id == m.get("team2_id"):
                        return winner_id, m.get("team2", "TBD")
            except Exception:
                pass
            return None, "TBD"

        if len(existing_matches) == 4:
            semis = []
            for i in range(0, 4, 2):
                w1_id, w1_name = get_winner(existing_matches[i])
                w2_id, w2_name = get_winner(existing_matches[i + 1])
                semis.append({
                    "id": None, "tournament_id": tournament_id, "round": "Semifinals",
                    "team1": w1_name, "team2": w2_name,
                    "team1_id": w1_id, "team2_id": w2_id,
                    "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                })

            finals = [{
                "id": None, "tournament_id": tournament_id, "round": "Finals",
                "team1": "TBD", "team2": "TBD",
                "team1_id": None, "team2_id": None,
                "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
            }]

            return existing_matches + semis + finals

        if len(existing_matches) == 8:
            quarterfinals = []
            for i in range(0, 8, 2):
                w1_id, w1_name = get_winner(existing_matches[i])
                w2_id, w2_name = get_winner(existing_matches[i + 1])
                quarterfinals.append({
                    "id": None, "tournament_id": tournament_id, "round": "Quarterfinals",
                    "team1": w1_name, "team2": w2_name,
                    "team1_id": w1_id, "team2_id": w2_id,
                    "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                })

            semis = [{
                "id": None, "tournament_id": tournament_id, "round": "Semifinals",
                "team1": "TBD", "team2": "TBD",
                "team1_id": None, "team2_id": None,
                "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
            } for _ in range(2)]

            finals = [{
                "id": None, "tournament_id": tournament_id, "round": "Finals",
                "team1": "TBD", "team2": "TBD",
                "team1_id": None, "team2_id": None,
                "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
            }]

            return existing_matches + quarterfinals + semis + finals

        return existing_matches
