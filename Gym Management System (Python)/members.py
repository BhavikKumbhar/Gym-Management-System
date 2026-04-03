import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from datetime import date


def members_page(parent):

    frame = tk.Frame(parent, bg="#0b0f14")

    # ================= HEADER =================
    tk.Label(
        frame,
        text="Members Management",
        bg="#0b0f14",
        fg="#e5e7eb",
        font=("Segoe UI", 26, "bold")
    ).pack(anchor="w", padx=30, pady=(25, 5))

    tk.Label(
        frame,
        text="Monitor membership status, expiry & renewals",
        bg="#0b0f14",
        fg="#9ca3af",
        font=("Segoe UI", 11)
    ).pack(anchor="w", padx=30, pady=(0, 15))

    # ================= SEARCH =================
    search_frame = tk.Frame(frame, bg="#0b0f14")
    search_frame.pack(fill="x", padx=30, pady=(0, 10))

    tk.Label(search_frame, text="Search:", bg="#0b0f14", fg="#9ca3af").pack(side="left")

    search_var = tk.StringVar()

    search_entry = tk.Entry(
        search_frame,
        textvariable=search_var,
        bg="#111827",
        fg="#e5e7eb",
        insertbackground="white",   # cursor fix
        width=30,
        relief="flat",
        highlightthickness=1,
        highlightbackground="#1f2937",
        highlightcolor="#22c55e"
    )
    search_entry.pack(side="left", padx=10)

    # ================= TABLE =================
    table_card = tk.Frame(frame, bg="#111827")
    table_card.pack(fill="both", expand=True, padx=30, pady=10)

    columns = ("ID", "Name", "Email", "Phone", "Plan", "Join Date", "Status")

    tree = ttk.Treeview(table_card, columns=columns, show="headings", height=13)
    tree.pack(fill="both", expand=True, padx=15, pady=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.tag_configure("Active", background="#123d2a", foreground="#86efac")
    tree.tag_configure("Expiring Soon", background="#3a2f1a", foreground="#fde68a")
    tree.tag_configure("Expired", background="#3f1d1d", foreground="#fecaca")

    # ================= LOAD MEMBERS =================
    def load_members():
        tree.delete(*tree.get_children())

        keyword = search_var.get().strip()

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT id, name, email, phone, plan, join_date,
            CASE
                WHEN DATE_ADD(join_date, INTERVAL
                    CASE
                        WHEN plan='1 Month' THEN 1
                        WHEN plan='3 Months' THEN 3
                        WHEN plan='6 Months' THEN 6
                        WHEN plan='12 Months' THEN 12
                        ELSE 1
                    END MONTH
                ) < CURDATE()
                THEN 'Expired'
                WHEN DATE_ADD(join_date, INTERVAL
                    CASE
                        WHEN plan='1 Month' THEN 1
                        WHEN plan='3 Months' THEN 3
                        WHEN plan='6 Months' THEN 6
                        WHEN plan='12 Months' THEN 12
                        ELSE 1
                    END MONTH
                ) <= DATE_ADD(CURDATE(), INTERVAL 5 DAY)
                THEN 'Expiring Soon'
                ELSE 'Active'
            END AS status
            FROM members
        """

        if keyword:
            query += " WHERE name LIKE %s ORDER BY join_date DESC"
            cur.execute(query, ('%' + keyword + '%',))
        else:
            query += " ORDER BY join_date DESC"
            cur.execute(query)

        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row, tags=(row[6],))

    search_var.trace_add("write", lambda *args: load_members())

    # ================= ENTRY STYLE =================
    def styled_entry(parent, y, value=""):
        e = tk.Entry(
            parent,
            bg="#0b0f14",
            fg="#e5e7eb",
            insertbackground="white",
            width=28,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#1f2937",
            highlightcolor="#22c55e"
        )
        e.insert(0, value)
        e.place(x=40, y=y + 22)
        return e

    # ================= ADD MEMBER =================
    def open_add_member():
        win = tk.Toplevel(frame)
        win.title("Add Member")
        win.geometry("420x430")
        win.configure(bg="#111827")
        win.grab_set()

        tk.Label(win, text="Full Name", bg="#111827", fg="#9ca3af").place(x=40, y=30)
        name_e = styled_entry(win, 30)

        tk.Label(win, text="Email", bg="#111827", fg="#9ca3af").place(x=40, y=90)
        email_e = styled_entry(win, 90)

        tk.Label(win, text="Phone", bg="#111827", fg="#9ca3af").place(x=40, y=150)
        phone_e = styled_entry(win, 150)

        tk.Label(win, text="Plan", bg="#111827", fg="#9ca3af").place(x=40, y=210)
        plan_e = ttk.Combobox(
            win,
            values=["1 Month", "3 Months", "6 Months", "12 Months"],
            state="readonly",
            width=26
        )
        plan_e.place(x=40, y=232)
        plan_e.current(0)

        def save():
            if not name_e.get() or not phone_e.get():
                messagebox.showwarning("Validation", "Name & Phone required")
                return

            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO members (name, email, phone, plan, join_date) VALUES (%s,%s,%s,%s,%s)",
                (name_e.get(), email_e.get(), phone_e.get(), plan_e.get(), date.today())
            )
            conn.commit()
            conn.close()

            win.destroy()
            load_members()

        ttk.Button(win, text="➕ Add Member", command=save).place(x=145, y=330)

    # ================= EDIT MEMBER =================
    def edit_member():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a member")
            return

        values = tree.item(selected[0])["values"]
        member_id = values[0]

        win = tk.Toplevel(frame)
        win.title("Edit Member")
        win.geometry("420x430")
        win.configure(bg="#111827")
        win.grab_set()

        tk.Label(win, text="Full Name", bg="#111827", fg="#9ca3af").place(x=40, y=30)
        name_e = styled_entry(win, 30, values[1])

        tk.Label(win, text="Email", bg="#111827", fg="#9ca3af").place(x=40, y=90)
        email_e = styled_entry(win, 90, values[2])

        tk.Label(win, text="Phone", bg="#111827", fg="#9ca3af").place(x=40, y=150)
        phone_e = styled_entry(win, 150, values[3])

        tk.Label(win, text="Plan", bg="#111827", fg="#9ca3af").place(x=40, y=210)
        plan_e = ttk.Combobox(
            win,
            values=["1 Month", "3 Months", "6 Months", "12 Months"],
            state="readonly",
            width=26
        )
        plan_e.place(x=40, y=232)
        plan_e.set(values[4])

        def update():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE members SET name=%s, email=%s, phone=%s, plan=%s WHERE id=%s",
                (name_e.get(), email_e.get(), phone_e.get(), plan_e.get(), member_id)
            )
            conn.commit()
            conn.close()

            win.destroy()
            load_members()

        ttk.Button(win, text="💾 Update", command=update).place(x=155, y=330)

    # ================= DELETE =================
    def delete_member():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a member")
            return

        member_id = tree.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirm", "Delete member and all records?"):
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM attendance WHERE member_id=%s", (member_id,))
        cur.execute("DELETE FROM payments WHERE member_id=%s", (member_id,))
        cur.execute("DELETE FROM members WHERE id=%s", (member_id,))

        conn.commit()
        conn.close()

        load_members()

    # ================= VIEW PROFILE =================
    def view_profile():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a member")
            return

        values = tree.item(selected[0])["values"]
        member_id = values[0]

        win = tk.Toplevel(frame)
        win.title("Member Profile")
        win.geometry("700x500")
        win.configure(bg="#111827")
        win.grab_set()

        tk.Label(
            win,
            text=f"Profile - {values[1]}",
            bg="#111827",
            fg="#22c55e",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=10)

        for t in [
            f"Email : {values[2]}",
            f"Phone : {values[3]}",
            f"Plan : {values[4]}",
            f"Join Date : {values[5]}",
            f"Status : {values[6]}"
        ]:
            tk.Label(win, text=t, bg="#111827", fg="#e5e7eb").pack(anchor="w", padx=20)

        conn = get_connection()
        cur = conn.cursor()

        tk.Label(win, text="Payment History", bg="#111827", fg="#f59e0b").pack(pady=10)
        pay_tree = ttk.Treeview(win, columns=("Amount", "Method", "Date"), show="headings", height=5)
        pay_tree.pack(fill="x", padx=20)

        for c in ("Amount", "Method", "Date"):
            pay_tree.heading(c, text=c)
            pay_tree.column(c, anchor="center")

        cur.execute(
            "SELECT amount, payment_type, payment_date FROM payments WHERE member_id=%s ORDER BY payment_date DESC",
            (member_id,)
        )
        for row in cur.fetchall():
            pay_tree.insert("", "end", values=row)

        tk.Label(win, text="Attendance History", bg="#111827", fg="#22c55e").pack(pady=10)
        att_tree = ttk.Treeview(win, columns=("Date",), show="headings", height=5)
        att_tree.pack(fill="x", padx=20)
        att_tree.heading("Date", text="Date")

        cur.execute(
            "SELECT date FROM attendance WHERE member_id=%s ORDER BY date DESC",
            (member_id,)
        )
        for row in cur.fetchall():
            att_tree.insert("", "end", values=row)

        conn.close()

    # ================= FOOTER =================
    footer = tk.Frame(frame, bg="#0b0f14")
    footer.pack(fill="x", padx=30, pady=(10, 25))

    ttk.Button(footer, text="➕ Add Member", command=open_add_member).pack(side="left", padx=10)
    ttk.Button(footer, text="✏ Edit Member", command=edit_member).pack(side="left", padx=10)
    ttk.Button(footer, text="🗑 Delete", command=delete_member).pack(side="left", padx=10)
    ttk.Button(footer, text="👁 View Profile", command=view_profile).pack(side="left", padx=10)
    ttk.Button(footer, text="⟳ Refresh", command=load_members).pack(side="left", padx=10)

    load_members()
    return frame
