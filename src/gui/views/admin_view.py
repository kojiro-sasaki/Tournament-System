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

