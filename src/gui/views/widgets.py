import customtkinter as ctk

BG_SIDEBAR = "#1A1A24"
BG_MAIN = "#121216"
BG_CARD = "#21212B"
BG_ROW = "#181820"
BORDER = "#2E2E3A"
ROW_BORDER = "#2A2A35"
COLOR_PRIMARY = "#3A7EBF"
COLOR_SUCCESS = "#2E7D32"
COLOR_DANGER = "#C62828"
COLOR_WARNING = "#E65100"
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED = "#8E9297"
TEXT_DANGER = "#FF4C4C"

FONT = "Roboto"


def F(size, bold=False):
    return (FONT, size, "bold") if bold else (FONT, size)


def label(parent, text, size=12, bold=False, color=TEXT_PRIMARY, **kw):
    return ctk.CTkLabel(parent, text=text, font=F(size, bold), text_color=color, **kw)


def card(parent, **kw):
    kw.setdefault("fg_color", BG_CARD)
    kw.setdefault("corner_radius", 10)
    kw.setdefault("border_width", 1)
    kw.setdefault("border_color", BORDER)
    return ctk.CTkFrame(parent, **kw)


def row_frame(parent, **kw):
    """A list-item row with the darker background used in scrollable lists."""
    kw.setdefault("fg_color", BG_ROW)
    kw.setdefault("corner_radius", 8)
    kw.setdefault("border_width", 1)
    kw.setdefault("border_color", ROW_BORDER)
    return ctk.CTkFrame(parent, **kw)


def button(parent, text, command, color=COLOR_PRIMARY, hover=None, height=32,
           corner_radius=8, **kw):
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color=color,
        hover_color=hover or color, height=height, corner_radius=corner_radius,
        font=F(11), **kw
    )


def outline_button(parent, text, command, border_color=COLOR_DANGER,
                    text_color=TEXT_DANGER, hover=None, **kw):
    kw.setdefault("height", 25)
    kw.setdefault("width", 60)
    kw.setdefault("corner_radius", 6)
    return ctk.CTkButton(
        parent, text=text, command=command, fg_color="transparent",
        border_width=1, border_color=border_color, text_color=text_color,
        hover_color=hover or "#3A1C1C", font=F(10), **kw
    )


def badge(parent, text, color, **kw):
    return ctk.CTkLabel(
        parent, text=f"  {text.upper()}  ", font=F(10, bold=True),
        text_color=TEXT_PRIMARY, fg_color=color, corner_radius=6, height=22, **kw
    )


def option_menu(parent, values, **kw):
    kw.setdefault("height", 35)
    kw.setdefault("fg_color", "#2A2A38")
    kw.setdefault("button_color", "#3A3A4D")
    return ctk.CTkOptionMenu(parent, values=values, **kw)


def form_field(parent, text, placeholder, height=35):
    """Label + Entry pair used in 'add new item' forms. Returns the Entry."""
    label(parent, text, size=12, color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(5, 2))
    entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=height)
    entry.pack(fill="x", padx=20, pady=(0, 10))
    return entry


def panel_title(parent, text, **pad):
    pad.setdefault("padx", 20)
    pad.setdefault("pady", (20, 15))
    label(parent, text, size=16, bold=True).pack(anchor="w", **pad)


