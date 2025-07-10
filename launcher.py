import tkinter as tk
from tkinter import ttk
import os
import subprocess
import sys

FONT_FAMILY = "Berlin Sans FB Demi"
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_BUTTON = (FONT_FAMILY, 14, "bold")
FONT_CREDIT = ("Segoe UI", 8)

COLOR_BACKGROUND = "#000F08"
COLOR_FRAME_BG = "#0E1F18"
COLOR_TEXT = "#F0F0F0"
COLOR_ACCENT = "#136F63"
COLOR_ACCENT_ACTIVE = "#1AAE95"
COLOR_ACCENT_TEXT = "#FFFFFF"
COLOR_HOVER_BG = "#FFFFFF"
COLOR_HOVER_TEXT = "#000000"
COLOR_CREDIT_TEXT = "#AAAAAA"


class AppLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Launcher")
        self.geometry("500x400")
        self.minsize(450, 350)
        self.configure(bg=COLOR_BACKGROUND)

        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('.', background=COLOR_BACKGROUND, foreground=COLOR_TEXT, font=FONT_BUTTON)
        style.configure('TFrame', background=COLOR_BACKGROUND)
        style.configure('TLabel', background=COLOR_BACKGROUND, foreground=COLOR_TEXT)
        
        style.configure('Launcher.TButton', 
                        background=COLOR_ACCENT, 
                        foreground=COLOR_ACCENT_TEXT, 
                        font=FONT_BUTTON, 
                        padding=(20, 15), 
                        borderwidth=0, 
                        relief='flat',
                        width=18)
        style.map('Launcher.TButton', 
                  background=[('active', COLOR_ACCENT_ACTIVE)])

        style.configure('Exit.TButton', 
                        background=COLOR_BACKGROUND, 
                        foreground=COLOR_TEXT, 
                        font=(FONT_FAMILY, 9),
                        padding=8,
                        borderwidth=1,
                        relief='solid')
        style.map('Exit.TButton', 
                  foreground=[('active', COLOR_ACCENT_ACTIVE)],
                  bordercolor=[('active', COLOR_ACCENT_ACTIVE)])

    def create_widgets(self):
        exit_frame = ttk.Frame(self, padding=10)
        exit_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        exit_btn = ttk.Button(exit_frame, text="EXIT", command=self.quit, style='Exit.TButton', width=8)
        exit_btn.pack(side=tk.RIGHT)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        credit_label = ttk.Label(main_frame, text="Created by - Nima Ghaffari", font=FONT_CREDIT, foreground=COLOR_CREDIT_TEXT)
        credit_label.pack(pady=(10, 0))

        title_label = ttk.Label(main_frame, text="Launcher", font=FONT_TITLE, foreground=COLOR_ACCENT_ACTIVE)
        title_label.pack(pady=(5, 30))

        server_btn = ttk.Button(main_frame, text="🚀  Launch Server", style='Launcher.TButton', command=self.run_server)
        server_btn.pack(pady=10)

        client_btn = ttk.Button(main_frame, text="💻  Launch Client", style='Launcher.TButton', command=self.run_client)
        client_btn.pack(pady=10)
        
    def run_app(self, script_name):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, script_name)

        self.destroy()
        try:
            subprocess.run([sys.executable, script_path], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to launch {script_path}: {e}")
            app = AppLauncher()
            app.mainloop()


    def run_server(self):
        self.run_app("server.py")

    def run_client(self):
        self.run_app("client.py")

if __name__ == "__main__":
    app = AppLauncher()
    app.mainloop()