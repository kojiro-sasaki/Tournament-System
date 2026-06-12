import customtkinter as ctk
import datetime
import tkinter as tk

from database.tournament_repository import TournamentRepository
from services.tournament_service import TournamentService
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
        self.tournament_service = TournamentService(TournamentRepository())
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
        start_date = self.t_date_entry.get().strip()

        self.t_error_lbl.configure(text="")

        if not name:
            self.t_error_lbl.configure(text="Please enter a tournament name!")
            return

        try:
            import datetime
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            self.t_error_lbl.configure(text="Invalid date format! Use YYYY-MM-DD")
            return

        game_id = 1 if game == "Counter-Strike 2" else 2

        try:
            tournament = self.tournament_service.create_tournament(
                name=name,
                description="",
                game_id=game_id,
                max_teams=max_teams,
                start_date=start_date,
                end_date=start_date
            )

            if tournament:
                self.tournaments.append({
                    "id": tournament["id"],
                    "name": tournament["name"],
                    "game": game,
                    "max_teams": max_teams,
                    "status": "Draft",
                    "registered_teams": 0,
                    "date": start_date,
                    "teams": [],
                })
                self.activities.append(f"Tournament '{name}' created successfully as 'Draft'")
                self.t_name_entry.delete(0, "end")
                self.refresh_tournaments_list()
            else:
                self.t_error_lbl.configure(text="Failed to create tournament!")

        except Exception as e:
            self.t_error_lbl.configure(text="Database error. Try again.")
            print(f"Tournament creation error: {e}")
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

    # ------------------------------------------------------------------
    # Matches tab
    # ------------------------------------------------------------------
    def show_matches_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        top_row = ctk.CTkFrame(tab_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))

        label(top_row, "Manage Matches for:", size=16, bold=True).pack(side="left", padx=(0, 10))

        t_options = {t["name"]: t["id"] for t in self.tournaments}
        t_names = list(t_options.keys())
        current_name = next((k for k, v in t_options.items() if v == self.selected_tournament_id),
                             "Dota 2 Champions Cup")

        t_selector = option_menu(top_row, t_names, width=250,
                                  command=lambda val: self.select_matches_tournament(t_options[val]))
        t_selector.set(current_name)
        t_selector.pack(side="left")

        matches_panel = card(tab_frame)
        matches_panel.pack(fill="both", expand=True)

        self.matches_scroll = ctk.CTkScrollableFrame(matches_panel, fg_color="transparent")
        self.matches_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        self.refresh_matches_list()

    def select_matches_tournament(self, tournament_id):
        self.selected_tournament_id = tournament_id
        self.refresh_matches_list()

    def refresh_matches_list(self):
        clear(self.matches_scroll)

        t_matches = [m for m in self.matches if m["tournament_id"] == self.selected_tournament_id]

        if not t_matches:
            label(self.matches_scroll, "No matches generated for this tournament.",
                  size=14, color=TEXT_MUTED).pack(pady=30)
            return

        for m in t_matches:
            row = row_frame(self.matches_scroll)
            row.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", padx=15, pady=12)
            label(info_frame, m["round"], size=12, bold=True, color=COLOR_PRIMARY, anchor="w").pack(fill="x")
            label(info_frame, f"Time: {m['time']}", size=11, color=TEXT_MUTED, anchor="w").pack(fill="x")

            teams_frame = ctk.CTkFrame(row, fg_color="transparent")
            teams_frame.pack(side="left", expand=True, fill="both", padx=10)
            teams_frame.grid_columnconfigure(0, weight=1)
            teams_frame.grid_columnconfigure(1, weight=0)
            teams_frame.grid_columnconfigure(2, weight=1)
            teams_frame.grid_rowconfigure(0, weight=1)

            label(teams_frame, m["team1"], size=13, bold=True, anchor="e").grid(row=0, column=0, sticky="ew", padx=10)

            vs_text = f" {m['score1']} - {m['score2']} " if m["status"] in ("Finished", "In Progress") else "   VS   "
            label(teams_frame, vs_text, size=14, bold=True, color=COLOR_PRIMARY).grid(row=0, column=1)

            label(teams_frame, m["team2"], size=13, bold=True, anchor="w").grid(row=0, column=2, sticky="ew", padx=10)

            right_frame = ctk.CTkFrame(row, fg_color="transparent")
            right_frame.pack(side="right", padx=15, pady=12)

            badge(right_frame, m["status"], status_color(m["status"])).pack(side="left", padx=15)
            button(right_frame, "Edit Score", lambda match_obj=m: self.open_score_dialog(match_obj),
                   color="#34495E", hover="#2C3E50", height=28, width=85, corner_radius=6).pack(side="left")

    def open_score_dialog(self, match):
        self.dialog_overlay = ctk.CTkFrame(self.content_frame, fg_color="#0A0A0F")
        self.dialog_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        dialog = ctk.CTkFrame(self.dialog_overlay, fg_color=BG_CARD, corner_radius=12, border_width=1,
                               border_color="#3E3E52", width=400, height=280)
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)

        label(dialog, f"Update Score - {match['round']}", size=16, bold=True).pack(pady=(15, 10))

        body = ctk.CTkFrame(dialog, fg_color="transparent")
        body.pack(fill="x", padx=30, pady=10)
        body.grid_columnconfigure((0, 2), weight=4)
        body.grid_columnconfigure(1, weight=2)

        label(body, match["team1"], size=12, bold=True, wraplength=120).grid(row=0, column=0, pady=(0, 5))
        self.s1_entry = ctk.CTkEntry(body, placeholder_text="0", width=60, height=35, justify="center")
        self.s1_entry.insert(0, str(match["score1"]))
        self.s1_entry.grid(row=1, column=0)

        label(body, ":", size=24, bold=True, color=TEXT_MUTED).grid(row=1, column=1)

        label(body, match["team2"], size=12, bold=True, wraplength=120).grid(row=0, column=2, pady=(0, 5))
        self.s2_entry = ctk.CTkEntry(body, placeholder_text="0", width=60, height=35, justify="center")
        self.s2_entry.insert(0, str(match["score2"]))
        self.s2_entry.grid(row=1, column=2)

        status_row = ctk.CTkFrame(dialog, fg_color="transparent")
        status_row.pack(fill="x", padx=30, pady=(10, 15))
        label(status_row, "Match Status: ", size=12, color=TEXT_MUTED).pack(side="left")

        self.m_status_menu = option_menu(status_row, ["Scheduled", "In Progress", "Finished"], height=28)
        self.m_status_menu.set(match["status"])
        self.m_status_menu.pack(side="left", fill="x", expand=True, padx=(5, 0))

        footer = ctk.CTkFrame(dialog, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=15, padx=30)

        ctk.CTkButton(footer, text="Cancel", fg_color="transparent", border_width=1, border_color="#555566",
                       hover_color="#2C2C35", height=32, corner_radius=6,
                       command=self.close_score_dialog).pack(side="left", fill="x", expand=True, padx=(0, 5))

        button(footer, "Save Results", lambda m_obj=match: self.save_score_event(m_obj),
               hover="#2E6299", height=32).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def close_score_dialog(self):
        if hasattr(self, "dialog_overlay") and self.dialog_overlay:
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
            team_key = "team1" if m_idx % 2 == 0 else "team2"
            # TODO: UPDATE matches SET {team_key} = winner WHERE id = t_matches[next_idx]['id']
            t_matches[next_idx][team_key] = winner

    # ------------------------------------------------------------------
    # Bracket tab
    # ------------------------------------------------------------------
    def show_bracket_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        label(tab_frame, "Interactive Playoff Bracket (Single Elimination)", size=16, bold=True).pack(anchor="w", pady=(0, 15))

        t_options = {t["name"]: t["id"] for t in self.tournaments}
        t_names = list(t_options.keys())
        current_name = next((k for k, v in t_options.items() if v == self.selected_tournament_id),
                             t_names[0] if t_names else "")

        sel_row = ctk.CTkFrame(tab_frame, fg_color="transparent")
        sel_row.pack(fill="x", pady=(0, 10))

        t_selector = option_menu(sel_row, t_names, width=220, height=30,
                                  command=lambda val: self.select_bracket_tournament(t_options[val]))
        t_selector.set(current_name)
        t_selector.pack(side="left")

        canvas_container = card(tab_frame)
        canvas_container.pack(fill="both", expand=True)

        h_scroll = tk.Scrollbar(canvas_container, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")
        v_scroll = tk.Scrollbar(canvas_container, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        self.bracket_canvas = tk.Canvas(
            canvas_container, bg=BG_CARD, highlightthickness=0,
            xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set
        )
        self.bracket_canvas.pack(side="left", fill="both", expand=True)

        h_scroll.config(command=self.bracket_canvas.xview)
        v_scroll.config(command=self.bracket_canvas.yview)

        self.bracket_canvas.bind("<MouseWheel>", lambda e: self.bracket_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.bracket_canvas.bind("<Shift-MouseWheel>", lambda e: self.bracket_canvas.xview_scroll(int(-1 * (e.delta / 120)), "units"))

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

        self.bracket_canvas.delete("all")

        t_matches = [m for m in self.matches if m["tournament_id"] == self.selected_tournament_id]

        if not t_matches or len(t_matches) not in (7, 15):
            self.bracket_canvas.create_text(
                300, 80,
                text="A standard bracket requires 7 (8-team) or 15 (16-team) matches.",
                fill=TEXT_MUTED, font=("Roboto", 13)
            )
            self.bracket_canvas.configure(scrollregion=(0, 0, 600, 160))
            return

        num_teams = 16 if len(t_matches) == 15 else 8

        PAD_X, PAD_Y = 30, 30
        CARD_W, CARD_H = 220, 100
        COL_GAP, ROW_GAP = 60, 20

        num_rounds = 5 if num_teams == 16 else 4
        col_x = [PAD_X + i * (CARD_W + COL_GAP) for i in range(num_rounds)]

        positions = {}

        if num_teams == 16:
            ro16_y_step = CARD_H + ROW_GAP
            ro16_ys = [PAD_Y + i * ro16_y_step for i in range(8)]
            for i in range(8):
                positions[f"ro16_{i}"] = (col_x[0], ro16_ys[i])

            qf_ys = [(ro16_ys[i * 2] + ro16_ys[i * 2 + 1]) / 2 for i in range(4)]
            for i in range(4):
                positions[f"qf{i}"] = (col_x[1], qf_ys[i])

            sf_ys = [(qf_ys[0] + qf_ys[1]) / 2, (qf_ys[2] + qf_ys[3]) / 2]
            positions["sf0"] = (col_x[2], sf_ys[0])
            positions["sf1"] = (col_x[2], sf_ys[1])

            final_y = (sf_ys[0] + sf_ys[1]) / 2
            positions["final"] = (col_x[3], final_y)
            positions["champion"] = (col_x[4], final_y)
        else:
            qf_y_step = CARD_H + ROW_GAP * 4
            qf_ys = [PAD_Y + i * qf_y_step for i in range(4)]
            for i in range(4):
                positions[f"qf{i}"] = (col_x[0], qf_ys[i])

            sf_ys = [(qf_ys[0] + qf_ys[1]) / 2, (qf_ys[2] + qf_ys[3]) / 2]
            positions["sf0"] = (col_x[1], sf_ys[0])
            positions["sf1"] = (col_x[1], sf_ys[1])

            final_y = (sf_ys[0] + sf_ys[1]) / 2
            positions["final"] = (col_x[2], final_y)
            positions["champion"] = (col_x[3], final_y)

        self._draw_bracket_lines(self.bracket_canvas, positions, CARD_W, CARD_H, num_teams)

        def place_card(match, pos_name):
            px, py = positions[pos_name]
            frame = self._make_canvas_match_card(match, CARD_W, CARD_H)
            self.bracket_canvas.create_window(px, py, window=frame, anchor="nw")

        if num_teams == 16:
            for i in range(8):
                place_card(t_matches[i], f"ro16_{i}")
            for i in range(4):
                place_card(t_matches[8 + i], f"qf{i}")
            for i in range(2):
                place_card(t_matches[12 + i], f"sf{i}")
            place_card(t_matches[14], "final")
            finals = t_matches[14]
        else:
            for i in range(4):
                place_card(t_matches[i], f"qf{i}")
            for i in range(2):
                place_card(t_matches[4 + i], f"sf{i}")
            place_card(t_matches[6], "final")
            finals = t_matches[6]

        winner_name = "TBD"
        if finals["status"] == "Finished":
            winner_name = finals["team1"] if finals["score1"] > finals["score2"] else finals["team2"]
        champ_frame = self._make_champion_card(winner_name, CARD_W, CARD_H)
        cx, cy = positions["champion"]
        self.bracket_canvas.create_window(cx, cy, window=champ_frame, anchor="nw")

        total_w = cx + CARD_W + PAD_X
        if num_teams == 16:
            total_h = max(ro16_ys[7] + CARD_H, cy + CARD_H) + PAD_Y
        else:
            total_h = max(qf_ys[3] + CARD_H, cy + CARD_H) + PAD_Y
        self.bracket_canvas.configure(scrollregion=(0, 0, total_w, total_h))

    def set_winner(self, match, winner_index):
        if winner_index == 1:
            match["score1"], match["score2"] = 1, 0
        else:
            match["score1"], match["score2"] = 0, 1

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
            current = t_matches.index(match)
        except ValueError:
            self.refresh_bracket_view()
            return

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

    def _make_canvas_match_card(self, match, w, h):
        """Build a match card widget to be placed on the canvas via create_window."""
        finished = match["status"] == "Finished"
        border_color = COLOR_SUCCESS if finished else "#5A2E8A"

        card_frame = ctk.CTkFrame(
            self.bracket_canvas, fg_color="#13131A", corner_radius=6,
            border_width=2, border_color=border_color, width=w, height=h
        )
        card_frame.pack_propagate(False)
        card_frame.grid_propagate(False)

        label(card_frame, match["round"], size=9, color=TEXT_MUTED).pack(anchor="w", padx=8, pady=(4, 0))

        teams_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        teams_frame.pack(fill="both", expand=True, padx=6, pady=(0, 4))

        def team_row(parent, team_key, score_key, opponent_score_key, allow_reset):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=1)

            if finished:
                is_winner = match[score_key] > match[opponent_score_key]
                color = TEXT_PRIMARY if is_winner else TEXT_MUTED
                prefix = "✓ " if is_winner else "   "
                label(row, prefix + match[team_key], size=11, bold=is_winner, color=color, anchor="w").pack(
                    side="left", fill="x", expand=True)

                if allow_reset:
                    ctk.CTkButton(
                        row, text="↺", width=22, height=22, font=F(13),
                        fg_color="transparent", border_width=1, border_color="#555566",
                        text_color=TEXT_MUTED, hover_color="#2A2A38", corner_radius=4,
                        command=lambda m=match: self.reset_match(m)
                    ).pack(side="right")
                return None, None
            else:
                var = ctk.StringVar(value="off")
                cb = ctk.CTkCheckBox(
                    row, text=match[team_key], variable=var, onvalue="on", offvalue="off",
                    fg_color=COLOR_PRIMARY, font=F(11), text_color=TEXT_PRIMARY, width=16, height=16
                )
                cb.pack(anchor="w")
                return var, cb

        if finished:
            team_row(teams_frame, "team1", "score1", "score2", allow_reset=False)
            team_row(teams_frame, "team2", "score2", "score1", allow_reset=True)
        else:
            cb1_var, cb1 = team_row(teams_frame, "team1", "score1", "score2", allow_reset=False)
            cb2_var, cb2 = team_row(teams_frame, "team2", "score2", "score1", allow_reset=False)

            def on_cb1():
                if cb1_var.get() == "on":
                    cb2_var.set("off")
                    self.set_winner(match, 1)

            def on_cb2():
                if cb2_var.get() == "on":
                    cb1_var.set("off")
                    self.set_winner(match, 2)

            cb1.configure(command=on_cb1)
            cb2.configure(command=on_cb2)

        return card_frame

    def _make_champion_card(self, team_name, w, h):
        frame = ctk.CTkFrame(
            self.bracket_canvas, fg_color="#241B00", corner_radius=8,
            width=w, height=h, border_width=2, border_color="#FFD700"
        )
        frame.pack_propagate(False)

        label(frame, "🏆 CHAMPION", size=10, bold=True, color="#FFD700").pack(pady=(8, 0))
        label(frame, team_name, size=12, bold=True, wraplength=w - 20).pack(pady=(2, 8))

        return frame

    # ------------------------------------------------------------------
    # Teams tab
    # ------------------------------------------------------------------
    def show_teams_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        list_panel = card(tab_frame)
        list_panel.pack(fill="both", expand=True, padx=20, pady=20)

        self.teams_scroll = scroll_list(list_panel, "Registered Teams Database")
        self.refresh_teams_list()

    def refresh_teams_list(self):
        clear(self.teams_scroll)

        for t in self.teams:
            c = row_frame(self.teams_scroll)
            c.pack(fill="x", pady=5, padx=5)

            info = ctk.CTkFrame(c, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=10)

            title_row = ctk.CTkFrame(info, fg_color="transparent")
            title_row.pack(fill="x")
            label(title_row, t["name"], size=13, bold=True).pack(side="left")
            label(title_row, f" [{t['tag']}]", size=11, bold=True, color=COLOR_PRIMARY).pack(side="left")

            label(info, f"Region: {t['region']} • Description: {t['desc']}", size=11, color=TEXT_MUTED,
                  anchor="w", wraplength=350, justify="left").pack(fill="x", pady=(2, 0))

            act_frame = ctk.CTkFrame(c, fg_color="transparent")
            act_frame.pack(side="right", padx=15, pady=10)

            outline_button(act_frame, "Remove", lambda name=t["name"]: self.remove_team(name)).pack()



    def remove_team(self, team_name):
        for t in self.teams:
            if t["name"] == team_name:
                # TODO: INSERT INTO activities (message) VALUES (...)
                self.activities.append(f"Team '{t['name']}' was removed from the database")
                # TODO: DELETE FROM teams WHERE name = team_name
                self.teams.remove(t)
                break
        self.refresh_teams_list()