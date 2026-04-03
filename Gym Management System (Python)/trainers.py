import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection


def trainers_page(parent):

    frame = tk.Frame(parent, bg="#0b0f14")

    # ================= HEADER =================
    tk.Label(
        frame,
        text="Trainers Management",
        bg="#0b0f14",
        fg="#e5e7eb",
        font=("Segoe UI", 26, "bold")
    ).pack(anchor="w", padx=40, pady=(30, 10))

    # ================= TABLE =================
    table_card = tk.Frame(frame, bg="#111827")
    table_card.pack(fill="both", expand=True, padx=40, pady=(0, 25))

    columns = ("ID", "Name", "Phone", "Specialization")

    tree = ttk.Treeview(
        table_card,
        columns=columns,
        show="headings",
        height=14
    )
    tree.pack(fill="both", expand=True, padx=18, pady=18)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    # ================= LOAD =================
    def load_trainers():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, phone, specialization FROM trainers ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row)

    # ================= ADD TRAINER =================
    def open_add_trainer():
        win = tk.Toplevel(frame)
        win.title("Add Trainer")
        win.geometry("400x350")
        win.configure(bg="#111827")
        win.grab_set()

        def label(t, y):
            tk.Label(win, text=t, bg="#111827", fg="#9ca3af").place(x=40, y=y)

        def entry(y):
            e = tk.Entry(win, bg="#0b0f14", fg="#e5e7eb", width=26)
            e.place(x=40, y=y + 22)
            return e

        label("Name", 30)
        name_e = entry(30)

        label("Phone", 100)
        phone_e = entry(100)

        label("Specialization", 170)
        spec_e = entry(170)

        def save():
            name = name_e.get().strip()
            phone = phone_e.get().strip()
            spec = spec_e.get().strip()

            if not name or not phone or not spec:
                messagebox.showwarning("Validation", "All fields required")
                return

            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO trainers (name, phone, specialization) VALUES (%s,%s,%s)",
                    (name, phone, spec)
                )
                conn.commit()
                conn.close()

                win.destroy()
                load_trainers()
                messagebox.showinfo("Success", "Trainer added")

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="➕ Add Trainer", command=save).place(x=120, y=250)

    # ================= DELETE =================
    def delete_trainer():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Action Required", "Select a trainer")
            return

        trainer_id = tree.item(selected[0])["values"][0]

        if not messagebox.askyesno("Confirm", "Delete trainer and attendance?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM trainer_attendance WHERE trainer_id=%s", (trainer_id,))
            cur.execute("DELETE FROM trainers WHERE id=%s", (trainer_id,))

            conn.commit()
            conn.close()

            load_trainers()
            messagebox.showinfo("Deleted", "Trainer removed")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= ATTENDANCE =================
    def mark_present():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Action Required", "Select a trainer")
            return

        trainer_id = tree.item(selected[0])["values"][0]

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT id FROM trainer_attendance WHERE trainer_id=%s AND date=CURDATE()",
                (trainer_id,)
            )

            if cur.fetchone():
                messagebox.showinfo("Info", "Already marked today")
            else:
                cur.execute(
                    "INSERT INTO trainer_attendance (trainer_id, date) VALUES (%s, CURDATE())",
                    (trainer_id,)
                )
                conn.commit()
                messagebox.showinfo("Success", "Attendance marked")

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= FOOTER =================
    footer = tk.Frame(frame, bg="#0b0f14")
    footer.pack(fill="x", padx=40, pady=(0, 30))

    ttk.Button(footer, text="➕ Add Trainer", command=open_add_trainer).pack(side="left", padx=10)
    ttk.Button(footer, text="🗑 Delete Trainer", command=delete_trainer).pack(side="left", padx=10)
    ttk.Button(footer, text="✔ Mark Present", command=mark_present).pack(side="left", padx=10)
    ttk.Button(footer, text="⟳ Refresh", command=load_trainers).pack(side="left", padx=10)

    load_trainers()
    return frame
