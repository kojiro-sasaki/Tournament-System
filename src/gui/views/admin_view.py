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

    def delete_tournament(self, tournament_id):
        for t in self.tournaments:
            if t["id"] == tournament_id:
                # TODO: INSERT INTO activities (message) VALUES (...)
                self.activities.append(f"Tournament '{t['name']}' was deleted")
                # TODO: DELETE FROM tournaments WHERE id = tournament_id
                self.tournaments.remove(t)
                break
        self.refresh_tournaments_list()

    def show_matches_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        top_row = ctk.CTkFrame(tab_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))

        lbl = ctk.CTkLabel(top_row, text="Manage Matches for:", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        lbl.pack(side="left", padx=(0, 10))

        t_options = {t["name"]: t["id"] for t in self.tournaments}
        t_names = list(t_options.keys())
        
        current_name = "Dota 2 Champions Cup"
        for k, v in t_options.items():
            if v == self.selected_tournament_id:
                current_name = k
                break

        t_selector = ctk.CTkOptionMenu(
            top_row, 
            values=t_names, 
            width=250, 
            height=35,
            fg_color="#2A2A38", 
            button_color="#3A3A4D",
            command=lambda val: self.select_matches_tournament(t_options[val])
        )
        t_selector.set(current_name)
        t_selector.pack(side="left")

        matches_panel = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        matches_panel.pack(fill="both", expand=True)

        self.matches_scroll = ctk.CTkScrollableFrame(matches_panel, fg_color="transparent")
        self.matches_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        self.refresh_matches_list()

    def select_matches_tournament(self, tournament_id):
        self.selected_tournament_id = tournament_id
        self.refresh_matches_list()

    def refresh_matches_list(self):
        for widget in self.matches_scroll.winfo_children():
            widget.destroy()

        t_matches = [m for m in self.matches if m["tournament_id"] == self.selected_tournament_id]

        if not t_matches:
            no_lbl = ctk.CTkLabel(self.matches_scroll, text="No matches generated for this tournament.", font=("Roboto", 14), text_color=TEXT_MUTED)
            no_lbl.pack(pady=30)
            return

        for m in t_matches:
            row = ctk.CTkFrame(self.matches_scroll, fg_color="#181820", corner_radius=8, border_width=1, border_color="#2A2A35")
            row.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=12)

            round_lbl = ctk.CTkLabel(info_frame, text=m["round"], font=("Roboto", 12, "bold"), text_color=COLOR_PRIMARY, anchor="w")
            round_lbl.pack(fill="x")

            time_lbl = ctk.CTkLabel(info_frame, text=f"Time: {m['time']}", font=("Roboto", 11), text_color=TEXT_MUTED, anchor="w")
            time_lbl.pack(fill="x")

            teams_frame = ctk.CTkFrame(row, fg_color="transparent")
            teams_frame.pack(side="left", expand=True, fill="both", padx=10)

            teams_frame.grid_columnconfigure(0, weight=1)
            teams_frame.grid_columnconfigure(1, weight=0)
            teams_frame.grid_columnconfigure(2, weight=1)
            teams_frame.grid_rowconfigure(0, weight=1)

            t1_lbl = ctk.CTkLabel(teams_frame, text=m["team1"], font=("Roboto", 13, "bold"), text_color=TEXT_PRIMARY, anchor="e")
            t1_lbl.grid(row=0, column=0, sticky="ew", padx=10)

            vs_text = f" {m['score1']} - {m['score2']} " if m["status"] in ["Finished", "In Progress"] else "   VS   "
            vs_lbl = ctk.CTkLabel(teams_frame, text=vs_text, font=("Roboto", 14, "bold"), text_color=COLOR_PRIMARY)
            vs_lbl.grid(row=0, column=1)

            t2_lbl = ctk.CTkLabel(teams_frame, text=m["team2"], font=("Roboto", 13, "bold"), text_color=TEXT_PRIMARY, anchor="w")
            t2_lbl.grid(row=0, column=2, sticky="ew", padx=10)

            right_frame = ctk.CTkFrame(row, fg_color="transparent")
            right_frame.pack(side="right", padx=15, pady=12)

            status_color = COLOR_SUCCESS if m["status"] == "Finished" else (COLOR_PRIMARY if m["status"] == "In Progress" else TEXT_MUTED)
            status_badge = ctk.CTkLabel(
                right_frame, 
                text=f"  {m['status'].upper()}  ", 
                font=("Roboto", 10, "bold"), 
                text_color=TEXT_PRIMARY,
                fg_color=status_color,
                corner_radius=6,
                height=22
            )
            status_badge.pack(side="left", padx=15)

            edit_btn = ctk.CTkButton(
                right_frame, 
                text="Edit Score", 
                font=("Roboto", 11), 
                height=28, 
                width=85, 
                fg_color="#34495E", 
                hover_color="#2C3E50", 
                corner_radius=6,
                command=lambda match_obj=m: self.open_score_dialog(match_obj)
            )
            edit_btn.pack(side="left")

    def open_score_dialog(self, match):
        self.dialog_overlay = ctk.CTkFrame(self.content_frame, fg_color="#0A0A0F")
        self.dialog_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        dialog = ctk.CTkFrame(self.dialog_overlay, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color="#3E3E52", width=400, height=280)
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)

        title_lbl = ctk.CTkLabel(dialog, text=f"Update Score - {match['round']}", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        title_lbl.pack(pady=(15, 10))

        body = ctk.CTkFrame(dialog, fg_color="transparent")
        body.pack(fill="x", padx=30, pady=10)
        body.grid_columnconfigure((0, 2), weight=4)
        body.grid_columnconfigure(1, weight=2)

        t1_lbl = ctk.CTkLabel(body, text=match["team1"], font=("Roboto", 12, "bold"), text_color=TEXT_PRIMARY, wraplength=120)
        t1_lbl.grid(row=0, column=0, pady=(0, 5))
        self.s1_entry = ctk.CTkEntry(body, placeholder_text="0", width=60, height=35, justify="center")
        self.s1_entry.insert(0, str(match["score1"]))
        self.s1_entry.grid(row=1, column=0)

        vs_lbl = ctk.CTkLabel(body, text=":", font=("Roboto", 24, "bold"), text_color=TEXT_MUTED)
        vs_lbl.grid(row=1, column=1)

        t2_lbl = ctk.CTkLabel(body, text=match["team2"], font=("Roboto", 12, "bold"), text_color=TEXT_PRIMARY, wraplength=120)
        t2_lbl.grid(row=0, column=2, pady=(0, 5))
        self.s2_entry = ctk.CTkEntry(body, placeholder_text="0", width=60, height=35, justify="center")
        self.s2_entry.insert(0, str(match["score2"]))
        self.s2_entry.grid(row=1, column=2)

        status_row = ctk.CTkFrame(dialog, fg_color="transparent")
        status_row.pack(fill="x", padx=30, pady=(10, 15))
        
        status_lbl = ctk.CTkLabel(status_row, text="Match Status: ", font=("Roboto", 12), text_color=TEXT_MUTED)
        status_lbl.pack(side="left")

        self.m_status_menu = ctk.CTkOptionMenu(
            status_row, 
            values=["Scheduled", "In Progress", "Finished"], 
            height=28,
            fg_color="#2A2A38", 
            button_color="#3A3A4D"
        )
        self.m_status_menu.set(match["status"])
        self.m_status_menu.pack(side="left", fill="x", expand=True, padx=(5, 0))

        footer = ctk.CTkFrame(dialog, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=15, padx=30)

        cancel_btn = ctk.CTkButton(footer, text="Cancel", fg_color="transparent", border_width=1, border_color="#555566", hover_color="#2C2C35", height=32, corner_radius=6, command=self.close_score_dialog)
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        save_btn = ctk.CTkButton(footer, text="Save Results", fg_color=COLOR_PRIMARY, hover_color="#2E6299", height=32, corner_radius=6, command=lambda m_obj=match: self.save_score_event(m_obj))
        save_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def close_score_dialog(self):
        if hasattr(self, 'dialog_overlay') and self.dialog_overlay:
            self.dialog_overlay.destroy()
            self.dialog_overlay = None

    def save_score_event(self, match):
        s1_str = self.s1_entry.get().strip()
        s2_str = self.s2_entry.get().strip()
        new_status = self.m_status_menu.get()

        try:
            score1 = int(s1_str) if s1_str else 0
            score2 = int(s2_str) if s2_str else 0
        except ValueError:
            self.s1_entry.configure(border_color=COLOR_DANGER)
            self.s2_entry.configure(border_color=COLOR_DANGER)
            return

        match["score1"] = score1
        match["score2"] = score2
        match["status"] = new_status

        if new_status == "Finished":
            # TODO: INSERT INTO activities (message) VALUES (...)
            self.activities.append(f"Match {match['team1']} vs {match['team2']} finished with score {score1}:{score2}")
            self.update_bracket_flow(match)
        else:
            # TODO: INSERT INTO activities (message) VALUES (...)
            self.activities.append(f"Match {match['team1']} vs {match['team2']} updated to '{new_status}'")
            
        # TODO: UPDATE matches SET score1 = score1, score2 = score2, status = new_status WHERE id = match['id']

        self.close_score_dialog()
        
        if self.current_tab == "Matches":
            self.refresh_matches_list()
        elif self.current_tab == "Bracket":
            self.refresh_bracket_view()

    def update_bracket_flow(self, match):
        t_id = match["tournament_id"]
        t_matches = [m for m in self.matches if m["tournament_id"] == t_id]
        if len(t_matches) not in (7, 15):
            return

        winner = match["team1"] if match["score1"] > match["score2"] else match["team2"]
        try:
            m_idx = t_matches.index(match)
        except ValueError:
            return

        next_idx = get_next_match_index(m_idx, len(t_matches))
        if next_idx < len(t_matches):
            if m_idx % 2 == 0:
                # TODO: UPDATE matches SET team1 = winner WHERE id = t_matches[next_idx]['id']
                t_matches[next_idx]["team1"] = winner
            else:
                # TODO: UPDATE matches SET team2 = winner WHERE id = t_matches[next_idx]['id']
                t_matches[next_idx]["team2"] = winner

    def show_bracket_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        header = ctk.CTkLabel(tab_frame, text="Interactive Playoff Bracket (Single Elimination)", font=("Roboto", 16, "bold"), text_color=TEXT_PRIMARY)
        header.pack(anchor="w", pady=(0, 15))

        t_options = {t["name"]: t["id"] for t in self.tournaments}
        t_names = list(t_options.keys())
        current_name = next((k for k, v in t_options.items() if v == self.selected_tournament_id), t_names[0] if t_names else "")

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

        # Outer container with card styling
        canvas_container = ctk.CTkFrame(tab_frame, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#2E2E3A")
        canvas_container.pack(fill="both", expand=True)

        # Scrollbars
        h_scroll = tk.Scrollbar(canvas_container, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        v_scroll = tk.Scrollbar(canvas_container, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        # Main canvas for drawing lines + embedding widgets
        self.bracket_canvas = tk.Canvas(
            canvas_container,
            bg=BG_CARD,
            highlightthickness=0,
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set
        )
        self.bracket_canvas.pack(side="left", fill="both", expand=True)

        h_scroll.config(command=self.bracket_canvas.xview)
        v_scroll.config(command=self.bracket_canvas.yview)

        self.bracket_canvas.bind("<MouseWheel>", lambda e: self.bracket_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.bracket_canvas.bind("<Shift-MouseWheel>", lambda e: self.bracket_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))

        self.refresh_bracket_view()

    def select_bracket_tournament(self, tournament_id):
        self.selected_tournament_id = tournament_id
        self.refresh_bracket_view()

    def _draw_bracket_lines(self, canvas, positions, card_w, card_h, num_teams):
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
                rx0, ry0 = mid_right(*positions[f"ro16_{i*2}"])
                rx1, ry1 = mid_right(*positions[f"ro16_{i*2+1}"])
                lx_qf, ly_qf = mid_left(*positions[f"qf{i}"])
                draw_connector(rx0, ry0, lx_qf, ly_qf)

        rx0, ry0 = mid_right(*positions["qf0"])
        rx1, ry1 = mid_right(*positions["qf1"])
        lx4, ly4 = mid_left(*positions["sf0"])
        draw_connector(rx0, ry0, lx4, ly4)
        draw_connector(rx1, ry1, lx4, ly4)

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

        # Clear everything on the canvas
        self.bracket_canvas.delete("all")

        t_matches = [m for m in self.matches if m["tournament_id"] == self.selected_tournament_id]

        if not t_matches or len(t_matches) not in (7, 15):
            self.bracket_canvas.create_text(
                300, 80,
                text="A standard bracket requires 7 (8-team) or 15 (16-team) matches.",
                fill=TEXT_MUTED,
                font=("Roboto", 13)
            )
            self.bracket_canvas.configure(scrollregion=(0, 0, 600, 160))
            return
            
        num_teams = 16 if len(t_matches) == 15 else 8

        # Layout constants
        PAD_X = 30
        PAD_Y = 30
        CARD_W = 220
        CARD_H = 100
        COL_GAP = 60
        ROW_GAP = 20

        # Build column X positions dynamically based on rounds
        num_rounds = 5 if num_teams == 16 else 4
        col_x = [PAD_X + i * (CARD_W + COL_GAP) for i in range(num_rounds)]
        
        positions = {}
        
        if num_teams == 16:
            # Ro16
            ro16_y_step = CARD_H + ROW_GAP
            ro16_ys = [PAD_Y + i * ro16_y_step for i in range(8)]
            for i in range(8):
                positions[f"ro16_{i}"] = (col_x[0], ro16_ys[i])
            
            # QF
            qf_ys = [(ro16_ys[i*2] + ro16_ys[i*2+1]) / 2 for i in range(4)]
            for i in range(4):
                positions[f"qf{i}"] = (col_x[1], qf_ys[i])
                
            # SF
            sf_ys = [(qf_ys[0] + qf_ys[1]) / 2, (qf_ys[2] + qf_ys[3]) / 2]
            positions["sf0"] = (col_x[2], sf_ys[0])
            positions["sf1"] = (col_x[2], sf_ys[1])
            
            # Final
            final_y = (sf_ys[0] + sf_ys[1]) / 2
            positions["final"] = (col_x[3], final_y)
            positions["champion"] = (col_x[4], final_y)
            
        else:
            # QF rows: 4 cards evenly spaced
            qf_y_step = CARD_H + ROW_GAP * 4
            qf_ys = [PAD_Y + i * qf_y_step for i in range(4)]
            for i in range(4):
                positions[f"qf{i}"] = (col_x[0], qf_ys[i])
                
            # SF
            sf_ys = [(qf_ys[0] + qf_ys[1]) / 2, (qf_ys[2] + qf_ys[3]) / 2]
            positions["sf0"] = (col_x[1], sf_ys[0])
            positions["sf1"] = (col_x[1], sf_ys[1])
            
            # Final
            final_y = (sf_ys[0] + sf_ys[1]) / 2
            positions["final"] = (col_x[2], final_y)
            positions["champion"] = (col_x[3], final_y)

        # Draw connector lines FIRST
        self._draw_bracket_lines(self.bracket_canvas, positions, CARD_W, CARD_H, num_teams)

        # Embed match card widgets
        def place_card(match, pos_name):
            px, py = positions[pos_name]
            frame = self._make_canvas_match_card(match, CARD_W, CARD_H)
            self.bracket_canvas.create_window(px, py, window=frame, anchor="nw")

        if num_teams == 16:
            for i in range(8): place_card(t_matches[i], f"ro16_{i}")
            for i in range(4): place_card(t_matches[8+i], f"qf{i}")
            for i in range(2): place_card(t_matches[12+i], f"sf{i}")
            place_card(t_matches[14], "final")
            finals = t_matches[14]
        else:
            for i in range(4): place_card(t_matches[i], f"qf{i}")
            for i in range(2): place_card(t_matches[4+i], f"sf{i}")
            place_card(t_matches[6], "final")
            finals = t_matches[6]

        # Champion card
        winner_name = "TBD"
        if finals["status"] == "Finished":
            winner_name = finals["team1"] if finals["score1"] > finals["score2"] else finals["team2"]
        champ_frame = self._make_champion_card(winner_name, CARD_W, CARD_H)
        cx, cy = positions["champion"]
        self.bracket_canvas.create_window(cx, cy, window=champ_frame, anchor="nw")

        # Update scroll region
        total_w = cx + CARD_W + PAD_X
        if num_teams == 16:
            total_h = max(ro16_ys[7] + CARD_H, cy + CARD_H) + PAD_Y
        else:
            total_h = max(qf_ys[3] + CARD_H, cy + CARD_H) + PAD_Y
        self.bracket_canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def set_winner(self, match, winner_index, cb1=None, cb2=None):
        if winner_index == 1:
            match["score1"] = 1
            match["score2"] = 0
        else:
            match["score1"] = 0
            match["score2"] = 1
            
        # TODO: UPDATE matches SET score1 = match['score1'], score2 = match['score2'], status = 'Finished' WHERE id = match['id']
        match["status"] = "Finished"
        self.update_bracket_flow(match)
        self.refresh_bracket_view()

    def reset_match(self, match):
        """Reset a finished match back to Scheduled so the winner can be changed."""
        # TODO: UPDATE matches SET score1 = 0, score2 = 0, status = 'Scheduled' WHERE id = match['id']
        match["score1"] = 0
        match["score2"] = 0
        match["status"] = "Scheduled"
        
        t_matches = [m for m in self.matches if m["tournament_id"] == match["tournament_id"]]
        if len(t_matches) not in (7, 15):
            self.refresh_bracket_view()
            return
            
        try:
            m_idx = t_matches.index(match)
        except ValueError:
            self.refresh_bracket_view()
            return
            
        current = m_idx
        while True:
            next_idx = get_next_match_index(current, len(t_matches))
            if next_idx >= len(t_matches):
                break
            team_key = "team1" if current % 2 == 0 else "team2"
            score_key = "score1" if current % 2 == 0 else "score2"
            # TODO: UPDATE matches SET {team_key} = 'TBD', {score_key} = 0, status = 'Scheduled' WHERE id = t_matches[next_idx]['id']
            t_matches[next_idx][team_key] = "TBD"
            t_matches[next_idx][score_key] = 0
            t_matches[next_idx]["status"] = "Scheduled"
            current = next_idx

        self.refresh_bracket_view()

