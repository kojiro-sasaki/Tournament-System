import customtkinter as ctk
import datetime
import tkinter as tk
from logic.tournament_logic import generate_matches, get_next_match_index

BG_SIDEBAR = "#1A1A24"
BG_MAIN = "#121216"
BG_CARD = "#21212B"
COLOR_PRIMARY = "#3A7EBF"
COLOR_SUCCESS = "#2E7D32"
COLOR_DANGER = "#C62828"
COLOR_WARNING = "#E65100"
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED = "#8E9297"

class AdminWindow(ctk.CTkFrame):
    def __init__(self, master, on_logout=None):
        super().__init__(master, fg_color=BG_MAIN)
        self.on_logout = on_logout
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Fetch tournaments list from database
        # TODO: SELECT * FROM tournaments
        self.tournaments = []
        
        # Fetch teams list from database
        # TODO: SELECT * FROM teams
        self.teams = []

        # Fetch matches list from database
        # TODO: SELECT * FROM matches
        self.matches = []
        
        # Fetch recent activity log from database
        # TODO: SELECT * FROM activities ORDER BY created_at DESC
        self.activities = []
        
        self.selected_tournament_id = 1

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
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        brand_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Tournament System", 
            font=("Roboto", 18, "bold"), 
            text_color=TEXT_PRIMARY
        )
        brand_label.grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")

        role_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="ADMIN CONTROL PANEL", 
            font=("Roboto", 11, "bold"), 
            text_color=COLOR_PRIMARY
        )
        role_label.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        tabs = [
            ("Dashboard", "🏠  Dashboard"),
            ("Tournaments", "🏆  Tournaments"),
            ("Matches", "⚔️  Matches"),
            ("Bracket", "📊  Bracket"),
            ("Teams", "👥  Teams")
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
        logout_btn.grid(row=7, column=0, padx=10, pady=25, sticky="ew")

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
        elif tab_name == "Tournaments":
            self.show_tournaments_tab()
        elif tab_name == "Matches":
            self.show_matches_tab()
        elif tab_name == "Bracket":
            self.show_bracket_tab()
        elif tab_name == "Teams":
            self.show_teams_tab()

    def show_dashboard_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        header_label = ctk.CTkLabel(tab_frame, text="Welcome, Administrator!", font=("Roboto", 24, "bold"), text_color=TEXT_PRIMARY)
        header_label.pack(anchor="w", pady=(0, 20))

        stats_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        self.create_stat_card(stats_frame, 0, "Total Tournaments", str(len(self.tournaments)), "🏆")
        active_matches_count = sum(1 for m in self.matches if m["status"] in ["In Progress", "Scheduled"])
        self.create_stat_card(stats_frame, 1, "Remaining Matches", str(active_matches_count), "⚔️")
        self.create_stat_card(stats_frame, 2, "Registered Teams", str(len(self.teams)), "👥")

        activity_panel = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        activity_panel.pack(fill="both", expand=True)

        activity_label = ctk.CTkLabel(activity_panel, text="Recent Activities Log", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        activity_label.pack(anchor="w", padx=20, pady=(15, 10))

        log_frame = ctk.CTkScrollableFrame(activity_panel, fg_color="transparent")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        for activity in reversed(self.activities):
            row = ctk.CTkFrame(log_frame, fg_color="#181820", height=40, corner_radius=6)
            row.pack(fill="x", pady=4, padx=5)
            row.pack_propagate(False)

            bullet = ctk.CTkLabel(row, text="●", text_color=COLOR_PRIMARY, font=("Roboto", 12))
            bullet.pack(side="left", padx=(15, 10))

            text_lbl = ctk.CTkLabel(row, text=activity, text_color=TEXT_PRIMARY, font=("Roboto", 13))
            text_lbl.pack(side="left", fill="both")

            time_lbl = ctk.CTkLabel(row, text="Just now", text_color=TEXT_MUTED, font=("Roboto", 11))
            time_lbl.pack(side="right", padx=15)

    def create_stat_card(self, parent, column, title, value, icon):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10, height=100, border_width=1, border_color="#2E2E3A")
        card.grid(row=0, column=column, padx=8, sticky="ew")
        card.pack_propagate(False)

        icon_lbl = ctk.CTkLabel(card, text=icon, font=("Roboto", 32), text_color=COLOR_PRIMARY)
        icon_lbl.pack(side="left", padx=20)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=15)

        val_lbl = ctk.CTkLabel(info_frame, text=value, font=("Roboto", 24, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        val_lbl.pack(fill="x")

        title_lbl = ctk.CTkLabel(info_frame, text=title, font=("Roboto", 12), text_color=TEXT_MUTED, anchor="w")
        title_lbl.pack(fill="x")

    def show_tournaments_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        tab_frame.grid_columnconfigure(0, weight=4)
        tab_frame.grid_columnconfigure(1, weight=6)
        tab_frame.grid_rowconfigure(0, weight=1)

        form_panel = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        form_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        form_label = ctk.CTkLabel(form_panel, text="Create Tournament", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        form_label.pack(anchor="w", padx=20, pady=(20, 15))

        ctk.CTkLabel(form_panel, text="Tournament Name", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_name_entry = ctk.CTkEntry(form_panel, placeholder_text="e.g. CS2 Spring Open", height=35)
        self.t_name_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_panel, text="Game Discipline", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_game_menu = ctk.CTkOptionMenu(form_panel, values=["Counter-Strike 2", "Dota 2"], height=35, fg_color="#2A2A38", button_color="#3A3A4D")
        self.t_game_menu.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_panel, text="Max Teams", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_teams_menu = ctk.CTkOptionMenu(form_panel, values=["8", "16"], height=35, fg_color="#2A2A38", button_color="#3A3A4D")
        self.t_teams_menu.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_panel, text="Start Date", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_date_entry = ctk.CTkEntry(form_panel, placeholder_text="YYYY-MM-DD", height=35)
        default_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.t_date_entry.insert(0, default_date)
        self.t_date_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_panel, text="Select Teams", font=("Roboto", 12), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_teams_scroll = ctk.CTkScrollableFrame(form_panel, fg_color="#181820", height=120, border_width=1, border_color="#2E2E3A")
        self.t_teams_scroll.pack(fill="x", padx=20, pady=(0, 20))
        
        self.team_checkboxes = {}
        for t in self.teams:
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(self.t_teams_scroll, text=t["name"], variable=var, onvalue="on", offvalue="off", fg_color=COLOR_PRIMARY, text_color=TEXT_PRIMARY, font=("Roboto", 12))
            cb.pack(anchor="w", pady=4, padx=5)
            self.team_checkboxes[t["name"]] = var

        self.t_error_lbl = ctk.CTkLabel(form_panel, text="", text_color="#FF4C4C", font=("Roboto", 12))
        self.t_error_lbl.pack(pady=(0, 5))

        create_btn = ctk.CTkButton(form_panel, text="Create Tournament", command=self.create_tournament_event, fg_color=COLOR_PRIMARY, hover_color="#2E6299", height=40, corner_radius=8)
        create_btn.pack(fill="x", padx=20, pady=(0, 20))

        list_panel = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        list_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        list_label = ctk.CTkLabel(list_panel, text="Active Tournaments", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        list_label.pack(anchor="w", padx=20, pady=(20, 15))

        self.tournaments_scroll = ctk.CTkScrollableFrame(list_panel, fg_color="transparent")
        self.tournaments_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        self.refresh_tournaments_list()

    def refresh_tournaments_list(self):
        for widget in self.tournaments_scroll.winfo_children():
            widget.destroy()

        for t in self.tournaments:
            card = ctk.CTkFrame(self.tournaments_scroll, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A35")
            card.pack(fill="x", pady=6, padx=5)

            details = ctk.CTkFrame(card, fg_color="transparent")
            details.pack(fill="x", padx=15, pady=10)

            name_lbl = ctk.CTkLabel(details, text=t["name"], font=("Roboto", 14, "bold"), text_color=TEXT_PRIMARY, anchor="w")
            name_lbl.pack(fill="x")

            sub_lbl = ctk.CTkLabel(
                details, 
                text=f"{t['game']} • Max Teams: {t['max_teams']} • Date: {t['date']}", 
                font=("Roboto", 11), 
                text_color=TEXT_MUTED,
                anchor="w"
            )
            sub_lbl.pack(fill="x")

            status_frame = ctk.CTkFrame(card, fg_color="transparent")
            status_frame.pack(fill="x", padx=15, pady=(0, 10))

            color = COLOR_WARNING if t["status"] == "Draft" else (COLOR_PRIMARY if t["status"] == "Registration Open" else (COLOR_SUCCESS if t["status"] == "In Progress" else COLOR_DANGER))
            badge = ctk.CTkLabel(
                status_frame, 
                text=f"  {t['status'].upper()}  ", 
                font=("Roboto", 10, "bold"), 
                text_color=TEXT_PRIMARY,
                fg_color=color,
                corner_radius=6,
                height=22
            )
            badge.pack(side="left")

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(fill="x", padx=15, pady=(0, 10))

            if t["status"] == "Draft":
                open_reg_btn = ctk.CTkButton(actions, text="Open Registration", font=("Roboto", 11), height=25, width=110, fg_color="#34495E", hover_color="#2C3E50", corner_radius=6, command=lambda tid=t["id"]: self.change_tournament_status(tid, "Registration Open"))
                open_reg_btn.pack(side="left", padx=(0, 5))
            elif t["status"] == "Registration Open":
                start_btn = ctk.CTkButton(actions, text="Start Tournament", font=("Roboto", 11), height=25, width=110, fg_color=COLOR_SUCCESS, hover_color="#236127", corner_radius=6, command=lambda tid=t["id"]: self.change_tournament_status(tid, "In Progress"))
                start_btn.pack(side="left", padx=(0, 5))
            elif t["status"] == "In Progress":
                finish_btn = ctk.CTkButton(actions, text="Finish Tournament", font=("Roboto", 11), height=25, width=110, fg_color=COLOR_DANGER, hover_color="#A81D1D", corner_radius=6, command=lambda tid=t["id"]: self.change_tournament_status(tid, "Finished"))
                finish_btn.pack(side="left", padx=(0, 5))

            delete_btn = ctk.CTkButton(actions, text="Delete", font=("Roboto", 11), height=25, width=60, fg_color="transparent", border_width=1, border_color="#C62828", text_color="#FF4C4C", hover_color="#3A1C1C", corner_radius=6, command=lambda tid=t["id"]: self.delete_tournament(tid))
            delete_btn.pack(side="right")

    def create_tournament_event(self):
        name = self.t_name_entry.get().strip()
        game = self.t_game_menu.get()
        max_teams = int(self.t_teams_menu.get())
        date_str = self.t_date_entry.get().strip()

        self.t_error_lbl.configure(text="")

        if not name:
            self.t_error_lbl.configure(text="Please enter a tournament name!")
            return

        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.t_error_lbl.configure(text="Invalid date format! Use YYYY-MM-DD")
            return

        selected_teams = [t_name for t_name, var in self.team_checkboxes.items() if var.get() == "on"]
        if len(selected_teams) != max_teams:
            self.t_error_lbl.configure(text=f"Please select exactly {max_teams} teams!")
            return

        new_id = max([t["id"] for t in self.tournaments]) + 1 if self.tournaments else 1
        new_t = {
            "id": new_id,
            "name": name,
            "game": game,
            "max_teams": max_teams,
            "status": "Draft",
            "registered_teams": len(selected_teams),
            "date": date_str,
            "teams": selected_teams
        }

        # TODO: INSERT INTO tournaments (id, name, game, max_teams, status, registered_teams, date) VALUES (...)
        self.tournaments.append(new_t)
        # TODO: INSERT INTO activities (message) VALUES (...)
        self.activities.append(f"Tournament '{name}' created successfully as 'Draft'")
        
        if max_teams in (8, 16):
            match_id_start = max([m["id"] for m in self.matches]) + 1 if self.matches else 1
            new_matches = generate_matches(new_id, selected_teams, max_teams, match_id_start)
            # TODO: INSERT INTO matches (id, tournament_id, round, team1, team2) VALUES (...)
            self.matches.extend(new_matches)

        self.t_name_entry.delete(0, "end")
        for var in self.team_checkboxes.values():
            var.set("off")
        
        self.refresh_tournaments_list()

    def change_tournament_status(self, tournament_id, new_status):
        for t in self.tournaments:
            if t["id"] == tournament_id:
                # TODO: UPDATE tournaments SET status = new_status WHERE id = tournament_id
                t["status"] = new_status
                # TODO: INSERT INTO activities (message) VALUES (...)
                self.activities.append(f"Tournament '{t['name']}' status changed to '{new_status}'")
                break
        self.refresh_tournaments_list()

