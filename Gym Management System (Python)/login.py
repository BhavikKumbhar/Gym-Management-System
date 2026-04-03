import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import winsound

from PIL import Image, ImageTk, ImageFilter

from db import get_connection
from ui_theme import apply_theme


# ================= SPLASH SCREEN =================
def show_splash(root, next_callback):
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    splash.configure(bg="#020617")

    # ---- center splash ----
    w, h = 820, 460
    x = (splash.winfo_screenwidth() // 2) - (w // 2)
    y = (splash.winfo_screenheight() // 2) - (h // 2)
    splash.geometry(f"{w}x{h}+{x}+{y}")

    # ---- load image safely ----
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "splash.png")

    if not os.path.exists(img_path):
        print("❌ splash.png not found")
        splash.destroy()
        next_callback()
        return

    original_img = Image.open(img_path).convert("RGBA")
    original_img = original_img.resize((700, 360), Image.LANCZOS)

    logo_label = tk.Label(splash, bg="#020617")
    logo_label.pack(pady=30)

    # ---- BLUR → SHARP ANIMATION ----
    blur_level = 14

    def animate_blur():
        nonlocal blur_level
        img = original_img.filter(ImageFilter.GaussianBlur(blur_level))
        logo = ImageTk.PhotoImage(img)
        logo_label.configure(image=logo)
        logo_label.image = logo

        if blur_level > 0:
            blur_level -= 1
            splash.after(70, animate_blur)

    animate_blur()

    # ---- progress bar ----
    bar_bg = tk.Frame(splash, bg="#1f2937", width=520, height=8)
    bar_bg.pack(pady=25)

    bar = tk.Frame(bar_bg, bg="#22c55e", width=0, height=8)
    bar.place(x=0, y=0)

    progress = 0

    def animate_bar():
        nonlocal progress
        if progress < 520:
            progress += 8
            bar.config(width=progress)
            splash.after(18, animate_bar)
        else:
            close_splash()

    def close_splash():
        splash.destroy()
        next_callback()

    animate_bar()


# ================= LOGIN WINDOW =================
def start_login():

    def open_dashboard():
        root.destroy()
        from dashboard import start_dashboard
        start_dashboard()

    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Validation", "Enter username and password")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, hashed_password)
            )
            user = cur.fetchone()
            conn.close()

            if user:
                # 🔊 play sound
                winsound.PlaySound("login.wav", winsound.SND_ASYNC)

                # ⛔ hide login window
                root.withdraw()

                # 🖼 show splash AFTER login
                show_splash(root, open_dashboard)

            else:
                messagebox.showerror("Login Failed", "Invalid credentials")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- LOGIN UI ----------
    root = tk.Tk()
    root.title("Gym Management System")
    root.geometry("520x620")
    root.configure(bg="#0b0f14")
    root.resizable(False, False)

    apply_theme(root)

    header = tk.Frame(root, bg="#020617", height=120)
    header.pack(fill="x")

    tk.Label(
        header,
        text="GYM MANAGEMENT SYSTEM",
        bg="#020617",
        fg="#22c55e",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(32, 4))

    tk.Label(
        header,
        text="Enterprise Fitness Administration",
        bg="#020617",
        fg="#9ca3af",
        font=("Segoe UI", 10)
    ).pack()

    card = tk.Frame(root, bg="#020617")
    card.pack(padx=40, pady=40, fill="x")

    tk.Label(
        card,
        text="Secure Admin Login",
        bg="#020617",
        fg="#e5e7eb",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(28, 10))

    def input_field(text):
        wrapper = tk.Frame(card, bg="#020617")
        wrapper.pack(fill="x", padx=30, pady=10)

        tk.Label(
            wrapper,
            text=text,
            bg="#020617",
            fg="#9ca3af"
        ).pack(anchor="w")

        e = tk.Entry(
            wrapper,
            bg="#0b0f14",
            fg="#e5e7eb",
            insertbackground="white",
            font=("Segoe UI", 12),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#1f2937",
            highlightcolor="#22c55e"
        )
        e.pack(fill="x", ipady=12, pady=(6, 0))
        return e

    username_entry = input_field("Username")
    password_entry = input_field("Password")
    password_entry.config(show="●")

    tk.Frame(card, height=1, bg="#1f2937").pack(fill="x", padx=30, pady=26)

    tk.Button(
        card,
        text="LOGIN",
        bg="#22c55e",
        fg="#020617",
        activebackground="#16a34a",
        font=("Segoe UI", 14, "bold"),
        relief="flat",
        cursor="hand2",
        command=login
    ).pack(fill="x", padx=30, ipady=14, pady=(0, 30))

    root.mainloop()


# ================= ENTRY =================
if __name__ == "__main__":
    start_login()
