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


