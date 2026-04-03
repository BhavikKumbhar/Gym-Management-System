import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from datetime import date
from email_service import send_payment_email
from ui_theme import apply_theme
import random


def payments_page(parent):

    frame = tk.Frame(parent, bg="#0b0f14")
    apply_theme(parent)

    # ================= HEADER =================
    header = tk.Frame(frame, bg="#0b0f14")
    header.pack(fill="x", padx=40, pady=(30, 10))

    tk.Label(
        header,
        text="Payments & Billing",
        bg="#0b0f14",
        fg="#e5e7eb",
        font=("Segoe UI", 26, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Record payments and automatically issue receipts",
        bg="#0b0f14",
        fg="#9ca3af",
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(4, 0))

    # ================= FORM =================
    form_card = tk.Frame(frame, bg="#111827")
    form_card.pack(fill="x", padx=40, pady=20)

    form = tk.Frame(form_card, bg="#111827")
    form.pack(padx=25, pady=25)

    def label(txt, r, c):
        tk.Label(form, text=txt, bg="#111827", fg="#9ca3af",
                 font=("Segoe UI", 11)).grid(row=r, column=c,
                                             sticky="w", padx=12, pady=(0, 6))

    def entry(r, c):
        e = tk.Entry(form, bg="#0b0f14", fg="#e5e7eb",
                     insertbackground="white", font=("Segoe UI", 12),
                     relief="flat", width=28)
        e.grid(row=r + 1, column=c, padx=12, pady=(0, 16))
        return e

    label("Member ID", 0, 0)
    label("Amount (₹)", 0, 1)
    label("Payment Method", 2, 0)

    member_entry = entry(0, 0)
    amount_entry = entry(0, 1)

    payment_type = ttk.Combobox(
        form,
        values=["Cash", "UPI", "Card", "Net Banking"],
        state="readonly",
        width=26
    )
    payment_type.grid(row=3, column=0, padx=12, pady=(0, 16), sticky="w")
    payment_type.current(0)

    # ================= FULL SCREEN SUCCESS =================
    def show_fullscreen_success(member_name, amount, method, txn_id, email):

        success_frame = tk.Frame(parent, bg="#0f172a")
        success_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        canvas = tk.Canvas(success_frame, bg="#0f172a", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        center_x = parent.winfo_width() // 2
        center_y = parent.winfo_height() // 2 - 80

        circle = canvas.create_oval(center_x, center_y,
                                    center_x, center_y,
                                    fill="#16a34a", outline="")

        def animate(radius=0):
            if radius <= 90:
                canvas.coords(circle,
                              center_x - radius,
                              center_y - radius,
                              center_x + radius,
                              center_y + radius)
                parent.after(6, lambda: animate(radius + 5))
            else:
                canvas.create_text(center_x, center_y,
                                   text="✔",
                                   fill="white",
                                   font=("Segoe UI", 70, "bold"))

        animate()

        # TEXT
        canvas.create_text(center_x, center_y + 140,
                           text="Payment Successful",
                           fill="white",
                           font=("Segoe UI", 28, "bold"))

        canvas.create_text(center_x, center_y + 190,
                           text=f"₹ {amount:,.2f}",
                           fill="#22c55e",
                           font=("Segoe UI", 32, "bold"))

        canvas.create_text(center_x, center_y + 230,
                           text=f"Receipt sent to your email address",
                           fill="#9ca3af",
                           font=("Segoe UI", 14))

        canvas.create_text(center_x, center_y + 260,
                           text=f"{email}",
                           fill="#e5e7eb",
                           font=("Segoe UI", 13))

        canvas.create_text(center_x, center_y + 300,
                           text=f"Transaction ID : {txn_id}",
                           fill="#6b7280",
                           font=("Segoe UI", 12))

        # Auto close and return
        def close_success():
            success_frame.destroy()

        parent.after(4000, close_success)

    # ================= ADD PAYMENT =================
    def add_payment():
        member_id = member_entry.get().strip()
        amount = amount_entry.get().strip()
        method = payment_type.get()

        if not member_id or not amount:
            messagebox.showwarning("Validation", "All fields required")
            return

        try:
            amount = float(amount)
        except:
            messagebox.showerror("Validation", "Amount must be numeric")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO payments (member_id, amount, payment_type, payment_date)
            VALUES (%s, %s, %s, %s)
        """, (member_id, amount, method, date.today()))
        conn.commit()

        cur.execute(
            "SELECT name, email, join_date FROM members WHERE id=%s",
            (member_id,)
        )
        member = cur.fetchone()
        conn.close()

        if not member:
            messagebox.showerror("Error", "Member not found")
            return

        name, email, join_date = member
        txn_id = "TXN" + str(random.randint(10000000, 99999999))

        if email:
            send_payment_email(
                to_email=email,
                member_name=name,
                amount=amount,
                payment_type=method,
                join_date=join_date,
                expiry_date=join_date
            )

        member_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        payment_type.current(0)

        load_payments()

        show_fullscreen_success(name, amount, method, txn_id, email)

    ttk.Button(
        form_card,
        text="💳 Record Payment",
        style="Success.TButton",
        command=add_payment
    ).pack(pady=15)

    # ================= TABLE =================
    table_card = tk.Frame(frame, bg="#111827")
    table_card.pack(fill="both", expand=True, padx=40, pady=(0, 30))

    columns = ("ID", "Member ID", "Amount", "Method", "Date")

    tree = ttk.Treeview(table_card, columns=columns, show="headings")
    tree.pack(fill="both", expand=True, padx=16, pady=16)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    def load_payments():
        tree.delete(*tree.get_children())
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, member_id, amount, payment_type, payment_date
            FROM payments
            ORDER BY payment_date DESC
        """)
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            tree.insert("", "end", values=row)

    load_payments()
    return frame
