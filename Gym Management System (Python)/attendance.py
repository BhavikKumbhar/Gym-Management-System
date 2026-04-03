import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from datetime import date
from ui_theme import apply_theme


def attendance_page(parent):

    frame = tk.Frame(parent, bg="#0b0f14")
    apply_theme(parent)

    # ================= HEADER =================
    tk.Label(
        frame,
        text="Attendance Control Panel",
        bg="#0b0f14",
        fg="#e5e7eb",
        font=("Segoe UI", 26, "bold")
    ).pack(anchor="w", padx=40, pady=(30, 5))

    tk.Label(
        frame,
        text=f"Live Attendance · {date.today().strftime('%d %B %Y')}",
        bg="#0b0f14",
        fg="#9ca3af",
        font=("Segoe UI", 11)
    ).pack(anchor="w", padx=40, pady=(0, 15))

    # ================= TABS =================
    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=40, pady=10)

    member_tab = tk.Frame(notebook, bg="#111827")
    trainer_tab = tk.Frame(notebook, bg="#111827")

    notebook.add(member_tab, text="👥 Members")
    notebook.add(trainer_tab, text="🧑‍🏫 Trainers")

    # ============================================================
    # 👥 MEMBERS ATTENDANCE
    # ============================================================

    mem_cols = ("ID", "Name", "Status")

    mem_tree = ttk.Treeview(member_tab, columns=mem_cols, show="headings")
    mem_tree.pack(fill="both", expand=True, padx=15, pady=15)

    for c in mem_cols:
        mem_tree.heading(c, text=c)
        mem_tree.column(c, anchor="center")

    mem_tree.tag_configure("Present", background="#052e16", foreground="#22c55e")
    mem_tree.tag_configure("Absent", background="#450a0a", foreground="#ef4444")

    def load_members():
        mem_tree.delete(*mem_tree.get_children())

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT m.id, m.name,
                IF(a.id IS NULL, 'Absent', 'Present')
                FROM members m
                LEFT JOIN attendance a
                    ON m.id = a.member_id
                    AND a.date = %s
                ORDER BY m.name
            """, (date.today(),))

            for row in cur.fetchall():
                mem_tree.insert("", "end", values=row, tags=(row[2],))

            conn.close()

        except Exception as e:
            print("Members attendance load error:", e)

    def mark_member_present():
        sel = mem_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a member")
            return

        member_id = mem_tree.item(sel[0])["values"][0]

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT id FROM attendance WHERE member_id=%s AND date=%s",
                (member_id, date.today())
            )

            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO attendance (member_id, date) VALUES (%s,%s)",
                    (member_id, date.today())
                )
                conn.commit()

            conn.close()
            load_members()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    mem_footer = tk.Frame(member_tab, bg="#111827")
    mem_footer.pack(fill="x", pady=10)

    ttk.Button(mem_footer, text="✔ Mark Present", command=mark_member_present).pack(side="left", padx=10)
    ttk.Button(mem_footer, text="⟳ Refresh", command=load_members).pack(side="left")

    # ============================================================
    # 🧑‍🏫 TRAINERS ATTENDANCE
    # ============================================================

    tr_cols = ("ID", "Name", "Status")

    tr_tree = ttk.Treeview(trainer_tab, columns=tr_cols, show="headings")
    tr_tree.pack(fill="both", expand=True, padx=15, pady=15)

    for c in tr_cols:
        tr_tree.heading(c, text=c)
        tr_tree.column(c, anchor="center")

    tr_tree.tag_configure("Present", background="#052e16", foreground="#22c55e")
    tr_tree.tag_configure("Absent", background="#450a0a", foreground="#ef4444")

    def load_trainers():
        tr_tree.delete(*tr_tree.get_children())

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT t.id, t.name,
                IF(a.id IS NULL, 'Absent', 'Present')
                FROM trainers t
                LEFT JOIN trainer_attendance a
                    ON t.id = a.trainer_id
                    AND a.date = %s
                ORDER BY t.name
            """, (date.today(),))

            for row in cur.fetchall():
                tr_tree.insert("", "end", values=row, tags=(row[2],))

            conn.close()

        except Exception as e:
            print("Trainer attendance load error:", e)

    def mark_trainer_present():
        sel = tr_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a trainer")
            return

        trainer_id = tr_tree.item(sel[0])["values"][0]

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT id FROM trainer_attendance WHERE trainer_id=%s AND date=%s",
                (trainer_id, date.today())
            )

            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO trainer_attendance (trainer_id, date) VALUES (%s,%s)",
                    (trainer_id, date.today())
                )
                conn.commit()

            conn.close()
            load_trainers()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tr_footer = tk.Frame(trainer_tab, bg="#111827")
    tr_footer.pack(fill="x", pady=10)

    ttk.Button(tr_footer, text="✔ Mark Present", command=mark_trainer_present).pack(side="left", padx=10)
    ttk.Button(tr_footer, text="⟳ Refresh", command=load_trainers).pack(side="left")

    # ================= INIT LOAD =================
    load_members()
    load_trainers()

    return frame
