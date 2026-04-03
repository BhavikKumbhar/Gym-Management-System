import tkinter as tk
from tkinter import ttk
import os
import winsound

def start_splash(next_callback):
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.geometry("600x400+500+250")
    splash.configure(bg="#0b0f14")

    # ===== PLAY SOUND =====
    sound_path = os.path.join(os.path.dirname(__file__), "login.wav")
    if os.path.exists(sound_path):
        winsound.PlaySound(sound_path, winsound.SND_ASYNC)

    # ===== LOAD IMAGE (KEEP REFERENCE!) =====
    img_path = os.path.join(os.path.dirname(__file__), "splash.png")
    splash.logo_img = tk.PhotoImage(file=img_path)  # IMPORTANT
    logo_label = tk.Label(
        splash,
        image=splash.logo_img,
        bg="#0b0f14"
    )
    logo_label.pack(pady=50)

    # ===== TITLE =====
    tk.Label(
        splash,
        text="GYM MANAGEMENT SYSTEM",
        fg="#22c55e",
        bg="#0b0f14",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=10)

    # ===== PROGRESS BAR =====
    progress = ttk.Progressbar(
        splash,
        orient="horizontal",
        length=400,
        mode="determinate"
    )
    progress.pack(pady=30)

    def load():
        for i in range(101):
            progress["value"] = i
            splash.update_idletasks()
            splash.after(20)

        splash.destroy()
        next_callback()

    splash.after(200, load)
    splash.mainloop()
