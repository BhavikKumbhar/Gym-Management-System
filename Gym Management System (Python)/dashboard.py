import tkinter as tk
from ui_theme import apply_theme
from db import get_connection
from datetime import datetime

from members import members_page
from trainers import trainers_page
from attendance import attendance_page
from payments import payments_page
from reports import reports_page


def start_dashboard():
    root = tk.Tk()
    root.title("Gym Management System | Admin Panel")
    root.geometry("1280x720")
    root.configure(bg="#0b0f14")

    apply_theme(root)

    # ================= SIDEBAR =================
    sidebar = tk.Frame(root, bg="#020617", width=260)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar, text="GYM ADMIN",
        bg="#020617", fg="#22c55e",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(30, 5))

    tk.Label(
        sidebar, text="Enterprise Control Panel",
        bg="#020617", fg="#9ca3af",
        font=("Segoe UI", 10)
    ).pack(pady=(0, 30))

    # ================= MAIN =================
    main = tk.Frame(root, bg="#0b0f14")
    main.pack(side="right", expand=True, fill="both")

    pages = {}

    def show_page(name):
        for p in pages.values():
            p.pack_forget()
        pages[name].pack(fill="both", expand=True)

    # ================= DASHBOARD =================
    dashboard = tk.Frame(main, bg="#0b0f14")
    pages["dashboard"] = dashboard

    # ================= HEADER =================
    header_row = tk.Frame(dashboard, bg="#0b0f14")
    header_row.pack(fill="x", padx=40, pady=(30, 10))

    title_box = tk.Frame(header_row, bg="#0b0f14")
    title_box.pack(side="left")

    tk.Label(
        title_box,
        text="Health And Fitness Dashboard Overview",
        bg="#0b0f14",
        fg="#e5e7eb",
        font=("Segoe UI", 30, "bold")
    ).pack(anchor="w")

    tk.Label(
        title_box,
        text="Live operational statistics & system health",
        bg="#0b0f14",
        fg="#9ca3af",
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(4, 0))

    # ================= CLOCK =================
    clock_label = tk.Label(
        header_row,
        bg="#0b0f14",
        fg="#9ca3af",
        font=("Segoe UI", 12, "bold")
    )
    clock_label.pack(side="right")

    def update_clock():
        if not dashboard.winfo_exists():
            return
        now = datetime.now().strftime("%A, %d %B %Y  |  %I:%M:%S %p")
        clock_label.config(text=now)
        dashboard.after(1000, update_clock)

    update_clock()

    # ================= CARD ROWS =================
    row1 = tk.Frame(dashboard, bg="#0b0f14")
    row1.pack(anchor="w", padx=40, pady=(20, 0))

    row2 = tk.Frame(dashboard, bg="#0b0f14")
    row2.pack(anchor="w", padx=40, pady=(25, 0))

    CARD_W = 250
    CARD_H = 130

    def card(parent, title, value, color):
        c = tk.Frame(
            parent,
            bg="#020617",
            width=CARD_W,
            height=CARD_H,
            highlightbackground=color,
            highlightthickness=2
        )
        c.pack(side="left", padx=18)
        c.pack_propagate(False)

        tk.Label(
            c, text=title,
            bg="#020617",
            fg="#9ca3af",
            font=("Segoe UI", 11)
        ).pack(pady=(28, 6))

        tk.Label(
            c, text=value,
            bg="#020617",
            fg=color,
            font=("Segoe UI", 28, "bold")
        ).pack()

    # ================= LOAD STATS =================
    def load_stats():
        if not dashboard.winfo_exists():
            return

        for f in (row1, row2):
            for w in f.winfo_children():
                w.destroy()

        conn = get_connection()
        cur = conn.cursor()

        # ---- MAIN ----
        cur.execute("SELECT COUNT(*) FROM members")
        total = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM members
            WHERE DATE_ADD(join_date, INTERVAL
                CASE
                    WHEN plan='1 Month' THEN 1
                    WHEN plan='3 Months' THEN 3
                    WHEN plan='6 Months' THEN 6
                    WHEN plan='12 Months' THEN 12
                    ELSE 1
                END MONTH
            ) < CURDATE()
        """)
        expired = cur.fetchone()[0]

        active = total - expired

        cur.execute("SELECT IFNULL(SUM(amount),0) FROM payments")
        revenue = cur.fetchone()[0]

        # ---- TODAY ----
        cur.execute("SELECT COUNT(*) FROM attendance WHERE date = CURDATE()")
        present_today = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM members
            WHERE join_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
        new_members = cur.fetchone()[0]

        cur.execute("""
            SELECT IFNULL(SUM(amount),0)
            FROM payments
            WHERE payment_date = CURDATE()
        """)
        payments_today = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM members
            WHERE DATE_ADD(join_date, INTERVAL
                CASE
                    WHEN plan='1 Month' THEN 1
                    WHEN plan='3 Months' THEN 3
                    WHEN plan='6 Months' THEN 6
                    WHEN plan='12 Months' THEN 12
                    ELSE 1
                END MONTH
            ) BETWEEN CURDATE()
            AND DATE_ADD(CURDATE(), INTERVAL 5 DAY)
        """)
        expiring_soon = cur.fetchone()[0]

        conn.close()

        # ---- ROW 1 ----
        card(row1, "Total Members", total, "#22c55e")
        card(row1, "Active Members", active, "#16a34a")
        card(row1, "Expired Members", expired, "#ef4444")
        card(row1, "Revenue (₹)", f"{revenue:.0f}", "#f59e0b")

        # ---- ROW 2 ----
        card(row2, "Present Today", present_today, "#22c55e")
        card(row2, "New Members (7 Days)", new_members, "#3b82f6")
        card(row2, "Payments Today", f"₹{payments_today:.0f}", "#f59e0b")
        card(row2, "Expiring in 5 Days", expiring_soon, "#ef4444")

    # ================= AUTO REFRESH =================
    def auto_refresh():
        load_stats()
        if dashboard.winfo_exists():
            dashboard.after(30000, auto_refresh)

    load_stats()
    auto_refresh()

    # ================= PAGES =================
    pages["members"] = members_page(main)
    pages["trainers"] = trainers_page(main)
    pages["attendance"] = attendance_page(main)
    pages["payments"] = payments_page(main)
    pages["reports"] = reports_page(main)

    # ================= NAV =================
    def nav(text, page):
        tk.Button(
            sidebar,
            text=text,
            bg="#020617",
            fg="#e5e7eb",
            activebackground="#1f2937",
            activeforeground="#22c55e",
            font=("Segoe UI", 13),
            bd=0,
            padx=30,
            anchor="w",
            cursor="hand2",
            command=lambda: show_page(page)
        ).pack(fill="x", pady=6)

    nav("📊 Dashboard", "dashboard")
    nav("👥 Members", "members")
    nav("🧑‍🏫 Trainers", "trainers")
    nav("🗓 Attendance", "attendance")
    nav("💳 Payments", "payments")
    nav("📑 Reports", "reports")

    tk.Button(
        sidebar,
        text="Logout",
        bg="#ef4444",
        fg="white",
        font=("Segoe UI", 13, "bold"),
        bd=0,
        pady=14,
        cursor="hand2",
        command=root.destroy
    ).pack(fill="x", pady=30)

    # IMPORTANT → force dashboard visible
    show_page("dashboard")

    # small delay ensures widgets draw
    root.after(100, load_stats)

    root.mainloop()
