import customtkinter as ctk
import datetime
import tkinter as tk

from database.repositories.tournament_repository import TournamentRepository
from services.tournament_service import TournamentService
from logic.tournament_logic import generate_matches, get_next_match_index
from database.repositories.match_repository import MatchRepository
from database.repositories.team_repository import TeamRepository
from gui.views.widgets import (
    BG_SIDEBAR, BG_MAIN, BG_CARD, BG_ROW, BORDER, ROW_BORDER,
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    TEXT_PRIMARY, TEXT_MUTED, TEXT_DANGER, F,
    label, card, row_frame, button, outline_button, badge, option_menu,
    form_field, panel_title, error_label, two_column_layout, scroll_list,
    clear, status_color,
)

from src.database.repositories.match_result_repository import MatchResultRepository
from src.database.repositories.tournament_registration_repository import TournamentRegistrationRepository


class AdminWindow(ctk.CTkFrame):
    def __init__(self, master, on_logout=None):
        super().__init__(master, fg_color=BG_MAIN)
        self.on_logout = on_logout
        self.tournament_service = TournamentService(TournamentRepository())
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        results = MatchResultRepository.get_all().data or []

        results_map = {
            r["match_id"]: r
            for r in results
        }
        # TODO: SELECT * FROM tournaments
        self.tournaments = []
        response = TournamentRepository.get_all()
        self.tournaments = response.data
        # Load teams
        try:
            t_resp = TeamRepository.get_all()
            self.teams = t_resp.data or []
        except Exception:
            self.teams = []

        # Load matches (normalize for UI)
        try:
            m_resp = MatchRepository.get_all()
            raw_matches = m_resp.data or []
        except Exception:
            raw_matches = []

        name_map = {t["id"]: t["name"] for t in self.teams}
        self.matches = []
        for r in raw_matches:
            result = results_map.get(r["id"])

            self.matches.append({
                "id": r.get("id"),
                "tournament_id": r.get("tournament_id"),
                "round": r.get("round_name") or r.get("round"),
                "team1_id": r.get("team1_id"),
                "team2_id": r.get("team2_id"),

                "team1": name_map.get(r.get("team1_id")) or r.get("team1_name") or "TBD",
                "team2": name_map.get(r.get("team2_id")) or r.get("team2_name") or "TBD",

                "score1": result["score_team1"] if result else 0,
                "score2": result["score_team2"] if result else 0,

                "winner_team_id": result["winner_team_id"] if result else None,

                "status": r.get("status", "Scheduled"),
                "time": r.get("match_date") or "TBD",
            })
        # TODO: SELECT * FROM activities ORDER BY created_at DESC
        self.activities = []
        self.current_bracket_matches = None

        self.selected_tournament_id = self.tournaments[0]["id"] if self.tournaments else None

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
        sidebar.grid_rowconfigure(8, weight=1)

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
            ("Ranking", "🥇  Ranking"),
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
        logout_btn.grid(row=9, column=0, padx=10, pady=25, sticky="ew")

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
            "Ranking": self.show_ranking_tab,
        }[tab_name]()

    def show_ranking_tab(self):
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tab_frame.pack(fill="both", expand=True)

        label(tab_frame, "Team Rankings", size=24, bold=True).pack(anchor="w", pady=(0, 20))

        list_panel = card(tab_frame)
        list_panel.pack(fill="both", expand=True)

        panel_title(list_panel, "Tournament Winners Leaderboard")

        scroll = ctk.CTkScrollableFrame(list_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        sorted_teams = sorted(
            [t for t in self.teams if (t.get("tournament_wins") or 0) > 0],
            key=lambda t: t.get("tournament_wins", 0) or 0,
            reverse=True
        )

        if not sorted_teams:
            label(scroll, "No teams have won a tournament yet.", size=14, color=TEXT_MUTED).pack(pady=30)
            return

        medals = ["🥇", "🥈", "🥉"]

        for idx, t in enumerate(sorted_teams):
            c = row_frame(scroll)
            c.pack(fill="x", pady=5, padx=5)

            medal = medals[idx] if idx < 3 else f"#{idx + 1}"

            rank_lbl = label(c, medal, size=20, bold=True)
            rank_lbl.pack(side="left", padx=15, pady=10)

            info = ctk.CTkFrame(c, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, pady=10)

            name_row = ctk.CTkFrame(info, fg_color="transparent")
            name_row.pack(fill="x")
            label(name_row, t["name"], size=13, bold=True).pack(side="left")
            label(name_row, f" [{t['tag']}]", size=11, color=COLOR_PRIMARY).pack(side="left")

            wins = t.get("tournament_wins", 0) or 0
            label(c, f"🏆 {wins} win{'s' if wins != 1 else ''}", size=13, bold=True, color="#FFD700").pack(side="right",
                                                                                                          padx=20)
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

        finished_matches = sum(1 for m in self.matches if m["status"] == "Finished")
        expected_matches = sum((t.get("max_teams", 0) - 1) for t in self.tournaments if t.get("max_teams") in (8, 16))
        active_matches_count = max(expected_matches - finished_matches, 0)

        for col, (title, value, icon) in enumerate([
            ("Total Tournaments", str(len(self.tournaments)), "🏆"),
            ("Remaining Matches", str(active_matches_count), "⚔️"),
            ("Registered Teams", str(len(self.teams)), "👥"),
        ]):
            self.create_stat_card(stats_frame, col, title, value, icon)


        label(tab_frame, "Tournaments Overview", size=18, bold=True).pack(anchor="w", pady=(20, 15))

        stats_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        finished_tournaments = sum(1 for t in self.tournaments if t.get("status") == "Finished")
        in_progress = sum(1 for t in self.tournaments if t.get("status") == "In Progress")
        draft = sum(1 for t in self.tournaments if t.get("status") == "Draft")

        registration_open = 0
        full_registration = 0
        for t in self.tournaments:
            if t.get("status") == "Registration Open":
                registration_open += 1
                try:
                    regs_resp = TournamentRegistrationRepository.get_all()
                    regs = [r for r in (regs_resp.data or []) if r.get("tournament_id") == t["id"]]
                    registered_count = len(regs)
                    max_teams = t.get("max_teams", 8)
                    if registered_count >= max_teams:
                        full_registration += 1
                except Exception:
                    pass

        statuses = [
            ("Finished", finished_tournaments),
            ("In Progress", in_progress),
            ("Registration Open", f"{full_registration} full  /  {registration_open}"),
            ("Draft", draft),
        ]

        for title, value in statuses:
            c = card(stats_frame, height=65)
            c.pack(fill="x", pady=5, padx=0)
            c.pack_propagate(False)

            label(c, title, size=15, bold=True, color=TEXT_PRIMARY, anchor="w").pack(side="left", padx=20)

            label(c, str(value), size=18, bold=True, color=TEXT_PRIMARY, anchor="e").pack(side="right", padx=20)

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

            top_row = ctk.CTkFrame(c, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(10, 0))

            label(top_row, t["name"], size=14, bold=True, anchor="w").pack(side="left", fill="x", expand=True)

            try:
                regs_resp = TournamentRegistrationRepository.get_all()
                regs = [r for r in (regs_resp.data or []) if r.get("tournament_id") == t["id"]]
                registered_count = len(regs)
            except Exception:
                registered_count = 0

            max_teams = t.get("max_teams", 8)

            teams_label = f"{registered_count}/{max_teams}"
            if registered_count == 0:
                color = TEXT_MUTED
            elif registered_count >= max_teams:
                color = COLOR_DANGER
            else:
                color = COLOR_SUCCESS
            label(top_row, teams_label, size=13, bold=True, color=color, anchor="e").pack(side="right")

            details = ctk.CTkFrame(c, fg_color="transparent")
            details.pack(fill="x", padx=15, pady=(2, 5))
            game_name = "Counter-Strike 2" if t["game_id"] == 1 else "Dota 2"
            label(details,
                  f"{game_name} • Max Teams: {max_teams} • Date: {t['start_date']}",
                  size=11, color=TEXT_MUTED, anchor="w").pack(fill="x")

            status_frame = ctk.CTkFrame(c, fg_color="transparent")
            status_frame.pack(fill="x", padx=15, pady=(0, 10))
            badge(status_frame, t["status"], status_color(t["status"])).pack(side="left")

            actions = ctk.CTkFrame(c, fg_color="transparent")
            actions.pack(fill="x", padx=15, pady=(0, 10))

            if t["status"] == "Draft":
                btn = ctk.CTkButton(
                    actions, text="Open Registration",
                    font=F(11), height=25, width=110, corner_radius=6,
                    fg_color="#34495E", hover_color="#2C3E50",
                    command=lambda tid=t["id"]: self.change_tournament_status(tid, "Registration Open")
                )
                btn.pack(side="left", padx=(0, 5))

            elif t["status"] == "Registration Open":
                is_full = registered_count >= max_teams

                btn = ctk.CTkButton(
                    actions, text="Start Tournament",
                    font=F(11), height=25, width=110, corner_radius=6,
                    fg_color=COLOR_SUCCESS if is_full else "#555566",
                    hover_color="#236127" if is_full else "#555566",
                    command=lambda tid=t["id"]: self.change_tournament_status(tid, "In Progress")
                )
                if not is_full:
                    btn.configure(state="disabled")
                btn.pack(side="left", padx=(0, 5))

            elif t["status"] == "In Progress":
                btn = ctk.CTkButton(
                    actions, text="Finish Tournament",
                    font=F(11), height=25, width=110, corner_radius=6,
                    fg_color=COLOR_DANGER, hover_color="#A81D1D",
                    command=lambda tid=t["id"]: self.change_tournament_status(tid, "Finished")
                )
                btn.pack(side="left", padx=(0, 5))

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
                    "game_id": game_id,
                    "max_teams": max_teams,
                    "status": "Draft",
                    "start_date": start_date,
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
        try:
            TournamentRepository.update_by_id(tournament_id, {"status": new_status})
            for t in self.tournaments:
                if t["id"] == tournament_id:
                    t["status"] = new_status
                    self.activities.append(f"Tournament '{t['name']}' status changed to '{new_status}'")
                    break

            if new_status == "Finished":
                self._award_tournament_win(tournament_id)

            self.refresh_tournaments_list()

        except Exception as e:
            print(f"Status update error: {e}")

    def _award_tournament_win(self, tournament_id):
        try:
            finals = next(
                (m for m in self.matches
                 if m["tournament_id"] == tournament_id and m["round"] == "Finals"),
                None
            )
            if not finals:
                print("Finals not found in self.matches")
                return

            winner_id = finals.get("winner_team_id")

            if not winner_id and finals.get("id"):
                result = MatchResultRepository.get_by_match_id(finals["id"])
                if result and result.data:
                    winner_id = result.data.get("winner_team_id")

            if not winner_id:
                print("Winner ID not found")
                return

            team = TeamRepository.get_by_id(winner_id)
            if not team.data:
                return

            current_wins = team.data.get("tournament_wins", 0) or 0
            TeamRepository.update_by_id(winner_id, {"tournament_wins": current_wins + 1})
            print(f"Tournament win awarded to team {winner_id}, total wins: {current_wins + 1}")

        except Exception as e:
            print(f"Award win error: {e}")

    def delete_tournament(self, tournament_id):
        try:
            TournamentRegistrationRepository.delete_by_tournament_id(
                tournament_id
            )

            MatchRepository.delete_by_tournament_id(
                tournament_id
            )

            TournamentRepository.delete_by_id(
                tournament_id
            )

            self.tournaments = [
                t for t in self.tournaments
                if t["id"] != tournament_id
            ]

            self.refresh_tournaments_list()

        except Exception as e:
            print(f"Delete tournament error: {e}")

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

        if match.get("id") is not None:
            MatchRepository.update_by_id(match["id"], {
                "status": new_status
            })

        if new_status == "Finished":

            winner_id = (
                match["team1_id"]
                if score1 > score2
                else match["team2_id"]
            )

            MatchResultRepository.create({
                "match_id": match["id"],
                "winner_team_id": winner_id,
                "score_team1": score1,
                "score_team2": score2
            })

            self.activities.append(
                f"Match {match['team1']} vs {match['team2']} finished with score {score1}:{score2}"
            )

            self.update_bracket_flow(match)

        else:
            self.activities.append(f"Match {match['team1']} vs {match['team2']} updated to '{new_status}'")

        self.close_score_dialog()

        if self.current_tab == "Matches":
            self.refresh_matches_list()
        elif self.current_tab == "Bracket":
            self.refresh_bracket_view()

    def update_bracket_flow(self, match):
        t_id = match["tournament_id"]
        t_matches = None
        if hasattr(self, "current_bracket_matches") and self.current_bracket_matches is not None and match in self.current_bracket_matches:
            t_matches = self.current_bracket_matches
        else:
            t_matches = sorted(
                [m for m in self.matches if m["tournament_id"] == t_id],
                key=lambda x: x.get("id", 0)
            )
            if len(t_matches) == 4:
                t_matches = t_matches + [
                    {"id": None, "tournament_id": t_id, "round": "Semifinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Semifinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Finals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                ]
            elif len(t_matches) == 8:
                t_matches = t_matches + [
                    {"id": None, "tournament_id": t_id, "round": "Quarterfinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Quarterfinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Quarterfinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Quarterfinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Semifinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Semifinals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                    {"id": None, "tournament_id": t_id, "round": "Finals", "team1": "TBD", "team2": "TBD", "score1": 0, "score2": 0, "status": "Scheduled"},
                ]

        if len(t_matches) not in (4, 7, 8, 15):
            return

        winner_name = match["team1"] if match["score1"] > match["score2"] else match["team2"]
        winner_id = match.get("team1_id") if match["score1"] > match["score2"] else match.get("team2_id")
        try:
            m_idx = t_matches.index(match)
        except ValueError:
            return
        print("MATCH INDEX =", m_idx)

        next_idx = get_next_match_index(m_idx, len(t_matches))
        print("NEXT INDEX =", next_idx)
        if next_idx < len(t_matches):
            team_key = "team1" if m_idx % 2 == 0 else "team2"
            team_id_key = f"{team_key}_id"
            t_matches[next_idx][team_key] = winner_name
            t_matches[next_idx][team_id_key] = winner_id
            next_match = t_matches[next_idx]
            print("NEXT MATCH =", next_match)

            if (
                    next_match.get("id") is None
                    and next_match.get("team1_id")
                    and next_match.get("team2_id")
            ):
                created = MatchRepository.create({
                    "tournament_id": t_id,
                    "team1_id": next_match["team1_id"],
                    "team2_id": next_match["team2_id"],
                    "status": "Scheduled",
                    "round_name": next_match["round"]
                })
                if created.data:
                    next_match["id"] = created.data[0]["id"]
                    if not any(m.get("id") == next_match["id"] for m in self.matches):
                        self.matches.append(next_match)

        if hasattr(self, "current_bracket_matches") and self.current_bracket_matches is not None:
            self.current_bracket_matches = t_matches

    def _get_expanded_bracket_matches(self, tournament_id):
        if tournament_id is None:
            return []

        existing_matches = sorted(
            [m for m in self.matches if m["tournament_id"] == tournament_id],
            key=lambda x: x.get("id", 0)
        )
        if not existing_matches:
            return []

        tournament = next((t for t in self.tournaments if t["id"] == tournament_id), None)
        if not tournament:
            return []

        max_teams = tournament.get("max_teams", 8)
        is_16_teams = (max_teams == 16)

        def get_winner_id(m):
            if m.get("status") != "Finished":
                return None
            try:
                result = MatchResultRepository.get_by_match_id(m["id"])
                if result.data and len(result.data) > 0:
                    return result.data[0]["winner_team_id"]  # [0] вместо прямого доступа
            except Exception:
                pass
            return None

        def get_winner_name(m):
            winner_id = get_winner_id(m)
            if winner_id == m.get("team1_id"):
                return m.get("team1", "TBD")
            if winner_id == m.get("team2_id"):
                return m.get("team2", "TBD")
            return "TBD"

        matches_by_id = {m.get("id"): m for m in existing_matches if m.get("id") is not None}

        if not is_16_teams:
            qf_matches = []
            for i in range(4):
                if i < len(existing_matches) and existing_matches[i].get("id") is not None:
                    qf_matches.append(existing_matches[i])
                else:
                    qf_matches.append({
                        "id": None, "tournament_id": tournament_id, "round": "Quarterfinals",
                        "team1": "TBD", "team2": "TBD",
                        "team1_id": None, "team2_id": None,
                        "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                    })

            sf_matches = []
            for i in range(2):
                existing_sf = next((m for m in existing_matches if m.get("round") == "Semifinals" and
                                    ((i == 0 and (m.get("team1") == get_winner_name(qf_matches[0]) or m.get(
                                        "team2") == get_winner_name(qf_matches[1]))) or
                                     (i == 1 and (m.get("team1") == get_winner_name(qf_matches[2]) or m.get(
                                         "team2") == get_winner_name(qf_matches[3]))))), None)

                if existing_sf:
                    sf_matches.append(existing_sf)
                else:
                    team1 = get_winner_name(qf_matches[i * 2]) if get_winner_id(qf_matches[i * 2]) else "TBD"
                    team2 = get_winner_name(qf_matches[i * 2 + 1]) if get_winner_id(qf_matches[i * 2 + 1]) else "TBD"
                    sf_matches.append({
                        "id": None, "tournament_id": tournament_id, "round": "Semifinals",
                        "team1": team1, "team2": team2,
                        "team1_id": get_winner_id(qf_matches[i * 2]), "team2_id": get_winner_id(qf_matches[i * 2 + 1]),
                        "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                    })

            final_match = next((m for m in existing_matches if m.get("round") == "Finals"), None)
            if not final_match:
                team1 = get_winner_name(sf_matches[0]) if get_winner_id(sf_matches[0]) else "TBD"
                team2 = get_winner_name(sf_matches[1]) if get_winner_id(sf_matches[1]) else "TBD"
                final_match = {
                    "id": None, "tournament_id": tournament_id, "round": "Finals",
                    "team1": team1, "team2": team2,
                    "team1_id": get_winner_id(sf_matches[0]), "team2_id": get_winner_id(sf_matches[1]),
                    "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                }

            return qf_matches + sf_matches + [final_match]

        else:
            ro16_matches = []
            for i in range(8):
                if i < len(existing_matches) and existing_matches[i].get("id") is not None:
                    ro16_matches.append(existing_matches[i])
                else:
                    ro16_matches.append({
                        "id": None, "tournament_id": tournament_id, "round": "Round of 16",
                        "team1": "TBD", "team2": "TBD",
                        "team1_id": None, "team2_id": None,
                        "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                    })

            qf_matches = []
            quarterfinals = [
                m for m in existing_matches
                if m.get("round") == "Quarterfinals"
            ]

            for i in range(4):
                existing_qf = (
                    quarterfinals[i]
                    if i < len(quarterfinals)
                    else None
                )

                if existing_qf:
                    qf_matches.append(existing_qf)
                else:
                    team1 = get_winner_name(ro16_matches[i * 2]) \
                        if get_winner_id(ro16_matches[i * 2]) else "TBD"

                    team2 = get_winner_name(ro16_matches[i * 2 + 1]) \
                        if get_winner_id(ro16_matches[i * 2 + 1]) else "TBD"

                    qf_matches.append({
                        "id": None,
                        "tournament_id": tournament_id,
                        "round": "Quarterfinals",
                        "team1": team1,
                        "team2": team2,
                        "team1_id": get_winner_id(ro16_matches[i * 2]),
                        "team2_id": get_winner_id(ro16_matches[i * 2 + 1]),
                        "score1": 0,
                        "score2": 0,
                        "status": "Scheduled",
                        "time": "TBD"
                    })

            sf_matches = []
            semifinals = [
                m for m in existing_matches
                if m.get("round") == "Semifinals"
            ]

            for i in range(2):
                existing_sf = (
                    semifinals[i]
                    if i < len(semifinals)
                    else None
                )

                if existing_sf:
                    sf_matches.append(existing_sf)
                else:
                    team1 = get_winner_name(qf_matches[i * 2]) \
                        if get_winner_id(qf_matches[i * 2]) else "TBD"

                    team2 = get_winner_name(qf_matches[i * 2 + 1]) \
                        if get_winner_id(qf_matches[i * 2 + 1]) else "TBD"

                    sf_matches.append({
                        "id": None,
                        "tournament_id": tournament_id,
                        "round": "Semifinals",
                        "team1": team1,
                        "team2": team2,
                        "team1_id": get_winner_id(qf_matches[i * 2]),
                        "team2_id": get_winner_id(qf_matches[i * 2 + 1]),
                        "score1": 0,
                        "score2": 0,
                        "status": "Scheduled",
                        "time": "TBD"
                    })

            final_match = next((m for m in existing_matches if m.get("round") == "Finals"), None)
            if not final_match:
                team1 = get_winner_name(sf_matches[0]) if get_winner_id(sf_matches[0]) else "TBD"
                team2 = get_winner_name(sf_matches[1]) if get_winner_id(sf_matches[1]) else "TBD"
                final_match = {
                    "id": None, "tournament_id": tournament_id, "round": "Finals",
                    "team1": team1, "team2": team2,
                    "team1_id": get_winner_id(sf_matches[0]), "team2_id": get_winner_id(sf_matches[1]),
                    "score1": 0, "score2": 0, "status": "Scheduled", "time": "TBD"
                }

            return ro16_matches + qf_matches + sf_matches + [final_match]

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

        t_matches = self._get_expanded_bracket_matches(self.selected_tournament_id)

        if not t_matches:
            self.bracket_canvas.create_text(
                300, 80,
                text="Waiting for all teams to register...",
                fill=TEXT_MUTED, font=("Roboto", 13)
            )
            self.bracket_canvas.configure(scrollregion=(0, 0, 600, 160))
            return

        self.current_bracket_matches = t_matches
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
        winner_id = finals.get("winner_team_id")

        if winner_id == finals.get("team1_id"):
            winner_name = finals["team1"]
        elif winner_id == finals.get("team2_id"):
            winner_name = finals["team2"]
        elif finals.get("status") == "Finished":
            if finals.get("score1", 0) > finals.get("score2", 0):
                winner_name = finals["team1"]
            elif finals.get("score2", 0) > finals.get("score1", 0):
                winner_name = finals["team2"]
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
            match["score1"] = 1
            match["score2"] = 0
            winner_id = match["team1_id"]
        else:
            match["score1"] = 0
            match["score2"] = 1
            winner_id = match["team2_id"]

        match["winner_team_id"] = winner_id
        match["status"] = "Finished"

        if match.get("id") is None:
            if match.get("team1_id") and match.get("team2_id"):
                created = MatchRepository.create({
                    "tournament_id": match["tournament_id"],
                    "team1_id": match["team1_id"],
                    "team2_id": match["team2_id"],
                    "status": "Finished",
                    "round_name": match["round"]
                })
                if created.data:
                    match["id"] = created.data[0]["id"]
                    self.matches.append(match)

        if match.get("id") is not None:
            MatchRepository.update_by_id(match["id"], {"status": "Finished"})

            try:
                existing = MatchResultRepository.get_by_match_id(match["id"])
                if existing and existing.data and len(existing.data) > 0:
                    MatchResultRepository.update_by_match_id(match["id"], {
                        "winner_team_id": winner_id,
                        "score_team1": match["score1"],
                        "score_team2": match["score2"]
                    })
                else:
                    MatchResultRepository.create({
                        "match_id": match["id"],
                        "winner_team_id": winner_id,
                        "score_team1": match["score1"],
                        "score_team2": match["score2"]
                    })
            except Exception as e:
                print("MATCH RESULT ERROR:", e)

        self.update_bracket_flow(match)
        self.refresh_bracket_view()

    def reset_match(self, match):
        """Reset a finished match back to Scheduled so the winner can be changed."""
        match["score1"] = 0
        match["score2"] = 0
        match["status"] = "Scheduled"
        if match.get("id") is not None:
            MatchRepository.update_by_id(match["id"], {
                "score1": 0,
                "score2": 0,
                "status": "Scheduled"
            })

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
            team_key = "team1" if current % 2 == 0 else "team2"
            team_id_key = f"{team_key}_id"

            t_matches[next_idx][team_key] = "TBD"
            t_matches[next_idx][team_id_key] = None

            t_matches[next_idx]["score1"] = 0
            t_matches[next_idx]["score2"] = 0
            t_matches[next_idx]["status"] = "Scheduled"
        self.refresh_bracket_view()

    def _make_canvas_match_card(self, match, w, h):
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
            wins = t.get("tournament_wins", 0) or 0
            if wins > 0:
                label(title_row, f" 🏆 {wins}", size=11, bold=True, color="#FFD700").pack(side="left")

            description = t.get("description") or "No description provided."
            label(info, description, size=11, color=TEXT_MUTED,
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