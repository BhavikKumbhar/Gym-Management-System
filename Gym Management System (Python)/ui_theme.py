from tkinter import ttk


def apply_theme(root):
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except:
        pass

    # ================= PREMIUM DARK =================
    BG = "#0b0f14"          # app background
    CARD = "#111827"        # cards / tables

    TEXT = "#e5e7eb"
    SUBTLE = "#9ca3af"

    ACCENT = "#22c55e"
    ACCENT_HOVER = "#16a34a"

    SUCCESS = "#22c55e"
    DANGER = "#ef4444"

    BORDER = "#1f2937"

    root.configure(bg=BG)

    # ================= TABLE =================
    style.configure(
        "Treeview",
        background=CARD,
        foreground=TEXT,
        fieldbackground=CARD,
        borderwidth=0,
        rowheight=34,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Treeview.Heading",
        background=BG,
        foreground=SUBTLE,
        font=("Segoe UI", 10, "bold"),
        borderwidth=0
    )

    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "white")]
    )

    # ================= BUTTON =================
    style.configure(
        "Primary.TButton",
        background=ACCENT,
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=10,
        borderwidth=0
    )

    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_HOVER)]
    )

    style.configure(
        "Success.TButton",
        background=SUCCESS,
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=10,
        borderwidth=0
    )

    style.map(
        "Success.TButton",
        background=[("active", "#15803d")]
    )

    style.configure(
        "Danger.TButton",
        background=DANGER,
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=10,
        borderwidth=0
    )

    style.map(
        "Danger.TButton",
        background=[("active", "#b91c1c")]
    )

    # ================= ENTRY =================
    style.configure(
        "TEntry",
        fieldbackground=CARD,
        foreground=TEXT,
        padding=8
    )

    style.configure(
        "TCombobox",
        fieldbackground=CARD,
        background=CARD,
        foreground=TEXT
    )
