import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from db import get_connection
from ui_theme import apply_theme
import csv


def reports_page(parent):

    frame = tk.Frame(parent, bg="#0b0f14")
    apply_theme(parent)

    # ================= HEADER =================
    header = tk.Frame(frame, bg="#0b0f14")
    header.pack(fill="x", padx=40, pady=(25, 10))

    tk.Label(
        header,
        text="Reports & Business Intelligence",
        bg="#0b0f14",
        fg="#e5e7eb",
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Analytics • Revenue • Insights",
        bg="#0b0f14",
        fg="#9ca3af",
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(4, 0))

    # ================= CONTROL BAR =================
    controls = tk.Frame(frame, bg="#111827")
    controls.pack(fill="x", padx=40, pady=15)

    # ================= TABLE =================
    table_card = tk.Frame(frame, bg="#111827")
    table_card.pack(fill="both", expand=True, padx=40, pady=(0, 25))

    tree = ttk.Treeview(table_card, show="headings", height=14)
    tree.pack(fill="both", expand=True, padx=18, pady=18)

    # ================= UTIL =================
    def clear_table():
        tree.delete(*tree.get_children())
        tree["columns"] = ()

    def setup_columns(cols):
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

    # ================= BASIC REPORTS =================
    def members_report():
        clear_table()
        setup_columns(("ID", "Name", "Plan", "Join Date"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, plan, join_date FROM members ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row)

    def payments_report():
        clear_table()
        setup_columns(("ID", "Member", "Amount", "Date"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, IFNULL(m.name,'Unknown'), IFNULL(p.amount,0), p.payment_date
            FROM payments p
            LEFT JOIN members m ON p.member_id = m.id
            ORDER BY p.payment_date DESC
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row)

    # ================= SMART TABLE =================
    def expiring_members():
        clear_table()
        setup_columns(("ID", "Name", "Expiry Date"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name,
            DATE_ADD(join_date, INTERVAL
                CASE
                    WHEN plan='1 Month' THEN 1
                    WHEN plan='3 Months' THEN 3
                    WHEN plan='6 Months' THEN 6
                    WHEN plan='12 Months' THEN 12
                    ELSE 1
                END MONTH
            ) as expiry
            FROM members
            HAVING expiry BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 5 DAY)
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row)

    def top_members():
        clear_table()
        setup_columns(("Member", "Total Paid"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.name, IFNULL(SUM(p.amount),0)
            FROM members m
            LEFT JOIN payments p ON p.member_id = m.id
            GROUP BY m.id, m.name
            ORDER BY IFNULL(SUM(p.amount),0) DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row)

    def retention_report():
        clear_table()
        setup_columns(("Type", "Count"))

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM members")
        total = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM members
            WHERE DATE_ADD(join_date, INTERVAL 1 MONTH) >= CURDATE()
        """)
        active = cur.fetchone()[0]

        expired = total - active
        conn.close()

        tree.insert("", "end", values=("Active", active))
        tree.insert("", "end", values=("Expired", expired))

    # ================= FORECAST =================
    def revenue_forecast():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT IFNULL(AVG(amount),0) FROM payments")
        avg = cur.fetchone()[0]
        conn.close()

        estimate = avg * 30

        messagebox.showinfo(
            "Forecast",
            f"Estimated next 30 days revenue:\n₹ {estimate:,.0f}"
        )

    # ================= HEALTH =================
    def business_health():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM members")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM attendance WHERE date = CURDATE()")
        today = cur.fetchone()[0]

        cur.execute("SELECT IFNULL(SUM(amount),0) FROM payments WHERE payment_date = CURDATE()")
        revenue = cur.fetchone()[0]

        conn.close()

        messagebox.showinfo(
            "Business Health",
            f"Total Members: {total}\nToday's Attendance: {today}\nToday's Revenue: ₹{revenue}\n\nSystem Healthy ✅"
        )

    # ================= EXPORT =================
    def export_csv():
        if not tree["columns"]:
            return

        file = filedialog.asksaveasfilename(defaultextension=".csv")
        if not file:
            return

        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(tree["columns"])
            for item in tree.get_children():
                writer.writerow(tree.item(item)["values"])

        messagebox.showinfo("Done", "CSV Exported Successfully")

    # ================= BUTTON =================
    def btn(text, cmd):
        tk.Button(
            controls,
            text=text,
            bg="#111827",
            fg="#e5e7eb",
            activebackground="#1f2937",
            activeforeground="#22c55e",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=14,
            pady=10,
            cursor="hand2",
            command=cmd
        ).pack(side="left", padx=4)

    # ================= BUTTONS =================
    btn("👥 Members", members_report)
    btn("💳 Payments", payments_report)
    btn("⚠ Expiring", expiring_members)
    btn("🏆 Top", top_members)
    btn("📊 Retention", retention_report)
    btn("🔮 Forecast", revenue_forecast)
    btn("💡 Health", business_health)
    btn("📥 Export", export_csv)

    members_report()

    return frame
