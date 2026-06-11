import customtkinter as ctk
import datetime
import tkinter as tk
from src.logic.tournament_logic import generate_matches, get_next_match_index
from src.gui.views.widgets import (
    BG_SIDEBAR, BG_MAIN, BG_CARD, BG_ROW, BORDER, ROW_BORDER,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    TEXT_PRIMARY, TEXT_MUTED, TEXT_DANGER, F,
    label, card, row_frame, button, outline_button, badge, option_menu,
    form_field, panel_title, error_label, two_column_layout, scroll_list,
    clear, status_color,
)


class AdminWindow(ctk.CTkFrame):
    def __init__(self, master, on_logout=None):
        super().__init__(master, fg_color=BG_MAIN)
        self.on_logout = on_logout

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # TODO: SELECT * FROM tournaments
        self.tournaments = []
        # TODO: SELECT * FROM teams
        self.teams = []
        # TODO: SELECT * FROM matches
        self.matches = []
        # TODO: SELECT * FROM activities ORDER BY created_at DESC
        self.activities = []

        self.selected_tournament_id = 1

        self.sidebar_buttons = {}
        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_tab = None
        self.select_tab("Dashboard")

    # ------------------------------------------------------------------
    # Sidebar / tab routing
    # ------------------------------------------------------------------
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)

        label(sidebar, "Tournament System", size=18, bold=True).grid(
            row=0, column=0, padx=20, pady=(25, 5), sticky="w")
        label(sidebar, "ADMIN CONTROL PANEL", size=11, bold=True, color=COLOR_PRIMARY).grid(
            row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        tabs = [
            ("Dashboard", "🏠  Dashboard"),
            ("Tournaments", "🏆  Tournaments"),
            ("Matches", "⚔️  Matches"),
            ("Bracket", "📊  Bracket"),
            ("Teams", "👥  Teams"),
        ]

        for idx, (tab_name, display_text) in enumerate(tabs):
            btn = ctk.CTkButton(
                sidebar, text=display_text, anchor="w", font=F(13), height=40,
                fg_color="transparent", text_color=TEXT_PRIMARY,
                hover_color="#272738", corner_radius=8,
                command=lambda name=tab_name: self.select_tab(name)
            )
            btn.grid(row=idx + 2, column=0, padx=10, pady=4, sticky="ew")
            self.sidebar_buttons[tab_name] = btn

        logout_btn = ctk.CTkButton(
            sidebar, text="🚪  Log Out", anchor="w", font=F(13), height=40,
            fg_color="transparent", text_color="#FF6B6B", hover_color="#3A1C1C",
            corner_radius=8, command=self.on_logout
        )
        logout_btn.grid(row=7, column=0, padx=10, pady=25, sticky="ew")

    def select_tab(self, tab_name):
        if self.current_tab == tab_name:
            return

        for name, btn in self.sidebar_buttons.items():
            active = name == tab_name
            btn.configure(
                fg_color=COLOR_PRIMARY if active else "transparent",
                hover_color=COLOR_PRIMARY if active else "#272738"
            )

        self.current_tab = tab_name
        clear(self.content_frame)

        {
            "Dashboard": self.show_dashboard_tab,
            "Tournaments": self.show_tournaments_tab,
            "Matches": self.show_matches_tab,
            "Bracket": self.show_bracket_tab,
            "Teams": self.show_teams_tab,
        }[tab_name]()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def show_dashboard_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        label(tab_frame, "Welcome, Administrator!", size=24, bold=True).pack(anchor="w", pady=(0, 20))

        stats_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")

        active_matches_count = sum(1 for m in self.matches if m["status"] in ("In Progress", "Scheduled"))
        for col, (title, value, icon) in enumerate([
            ("Total Tournaments", str(len(self.tournaments)), "🏆"),
            ("Remaining Matches", str(active_matches_count), "⚔️"),
            ("Registered Teams", str(len(self.teams)), "👥"),
        ]):
            self.create_stat_card(stats_frame, col, title, value, icon)

        activity_panel = card(tab_frame)
        activity_panel.pack(fill="both", expand=True)
        panel_title(activity_panel, "Recent Activities Log", pady=(15, 10))

        log_frame = ctk.CTkScrollableFrame(activity_panel, fg_color="transparent")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        for activity in reversed(self.activities):
            row = ctk.CTkFrame(log_frame, fg_color=BG_ROW, height=40, corner_radius=6)
            row.pack(fill="x", pady=4, padx=5)
            row.pack_propagate(False)

            label(row, "●", size=12, color=COLOR_PRIMARY).pack(side="left", padx=(15, 10))
            label(row, activity, size=13).pack(side="left", fill="both")
            label(row, "Just now", size=11, color=TEXT_MUTED).pack(side="right", padx=15)

    def create_stat_card(self, parent, column, title, value, icon):
        c = card(parent, height=100)
        c.grid(row=0, column=column, padx=8, sticky="ew")
        c.pack_propagate(False)

        label(c, icon, size=32, color=COLOR_PRIMARY).pack(side="left", padx=20)

        info_frame = ctk.CTkFrame(c, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=15)

        label(info_frame, value, size=24, bold=True, anchor="w").pack(fill="x")
        label(info_frame, title, size=12, color=TEXT_MUTED, anchor="w").pack(fill="x")

    # ------------------------------------------------------------------
    # Tournaments tab
    # ------------------------------------------------------------------
    def show_tournaments_tab(self):
        _, form_panel, list_panel = two_column_layout(self.content_frame)

        panel_title(form_panel, "Create Tournament")

        self.t_name_entry = form_field(form_panel, "Tournament Name", "e.g. CS2 Spring Open")

        label(form_panel, "Game Discipline", size=12, color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_game_menu = option_menu(form_panel, ["Counter-Strike 2", "Dota 2"])
        self.t_game_menu.pack(fill="x", padx=20, pady=(0, 10))

        label(form_panel, "Max Teams", size=12, color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_teams_menu = option_menu(form_panel, ["8", "16"])
        self.t_teams_menu.pack(fill="x", padx=20, pady=(0, 10))

        label(form_panel, "Start Date", size=12, color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        self.t_date_entry = ctk.CTkEntry(form_panel, placeholder_text="YYYY-MM-DD", height=35)
        default_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.t_date_entry.insert(0, default_date)
        self.t_date_entry.pack(fill="x", padx=20, pady=(0, 10))

        label(form_panel, "Select Teams", size=12, color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
        teams_scroll = ctk.CTkScrollableFrame(form_panel, fg_color=BG_ROW, height=120, border_width=1, border_color=BORDER)
        teams_scroll.pack(fill="x", padx=20, pady=(0, 20))

        self.team_checkboxes = {}
        for t in self.teams:
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(teams_scroll, text=t["name"], variable=var, onvalue="on", offvalue="off",
                                  fg_color=COLOR_PRIMARY, text_color=TEXT_PRIMARY, font=F(12))
            cb.pack(anchor="w", pady=4, padx=5)
            self.team_checkboxes[t["name"]] = var

        self.t_error_lbl = error_label(form_panel)
        self.t_error_lbl.pack(pady=(0, 5))

        button(form_panel, "Create Tournament", self.create_tournament_event,
               hover="#2E6299", height=40).pack(fill="x", padx=20, pady=(0, 20))

        self.tournaments_scroll = scroll_list(list_panel, "Active Tournaments")
        self.refresh_tournaments_list()

    def refresh_tournaments_list(self):
        clear(self.tournaments_scroll)

        for t in self.tournaments:
            c = row_frame(self.tournaments_scroll)
            c.pack(fill="x", pady=6, padx=5)

            details = ctk.CTkFrame(c, fg_color="transparent")
            details.pack(fill="x", padx=15, pady=10)

            label(details, t["name"], size=14, bold=True, anchor="w").pack(fill="x")
            label(details, f"{t['game']} • Max Teams: {t['max_teams']} • Date: {t['date']}",
                  size=11, color=TEXT_MUTED, anchor="w").pack(fill="x")

            status_frame = ctk.CTkFrame(c, fg_color="transparent")
            status_frame.pack(fill="x", padx=15, pady=(0, 10))
            badge(status_frame, t["status"], status_color(t["status"])).pack(side="left")

            actions = ctk.CTkFrame(c, fg_color="transparent")
            actions.pack(fill="x", padx=15, pady=(0, 10))

            next_status = {
                "Draft": ("Open Registration", "#34495E", "#2C3E50", "Registration Open"),
                "Registration Open": ("Start Tournament", COLOR_SUCCESS, "#236127", "In Progress"),
                "In Progress": ("Finish Tournament", COLOR_DANGER, "#A81D1D", "Finished"),
            }.get(t["status"])

            if next_status:
                text, color, hover, new_status = next_status
                button(actions, text, lambda tid=t["id"], s=new_status: self.change_tournament_status(tid, s),
                       color=color, hover=hover, height=25, width=110, corner_radius=6).pack(side="left", padx=(0, 5))

            outline_button(actions, "Delete", lambda tid=t["id"]: self.delete_tournament(tid)).pack(side="right")

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

        selected_teams = [name_ for name_, var in self.team_checkboxes.items() if var.get() == "on"]
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
            "teams": selected_teams,
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

