"""Home launcher UI for AITool"""
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
from core.service import config_manager
from core.view import notification
from core.view import setting
from core.view import generate

# UI Colors
BG = "#181818"
PANEL = "#1f1f1f"
TEXT = "#e6e6e6"
SUB = "#9aa0a6"
ACCENT = "#00a67e"


def _make_button(parent, text, command, accent=False):
    """Create a styled button"""
    bg = ACCENT if accent else "#2b2b2b"
    fg_color = BG if accent else TEXT
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg_color,
        bd=0,
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=12,
        pady=10,
        cursor="hand2"
    )
    btn.pack(fill=tk.X, pady=6)
    return btn


def create_home_frame(parent, show_generate_callback, show_settings_callback=None):
    """Create home page frame"""
    frame = tk.Frame(parent, bg=BG)
    
    # Fonts
    header_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
    sub_font = tkfont.Font(family="Segoe UI", size=10)

    container = tk.Frame(frame, bg=BG, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    top = tk.Frame(container, bg=BG)
    top.pack(fill=tk.X)

    title = tk.Label(top, text="AITool", bg=BG, fg=TEXT, font=header_font)
    title.pack(anchor='w')
    subtitle = tk.Label(top, text="Bắt đầu bằng một thao tác:", bg=BG, fg=SUB, font=sub_font)
    subtitle.pack(anchor='w', pady=(4, 12))

    # Panel
    panel = tk.Frame(container, bg=PANEL, padx=18, pady=18)
    panel.pack(fill=tk.BOTH, expand=True)

    # Vertical stack of buttons
    btn_area = tk.Frame(panel, bg=PANEL)
    btn_area.pack(expand=True)

    # Buttons
    _make_button(btn_area, "Gen kịch bản", show_generate_callback, accent=True)
    _make_button(btn_area, "Cài đặt", show_settings_callback, accent=False)

    # Small footer
    footer = tk.Label(container, text="Version: local — © AITool", bg=BG, fg=SUB, font=("Segoe UI", 8))
    footer.pack(side=tk.BOTTOM, pady=(10, 0))

    return frame


def create_main_window():
    """Create main application window with pages"""
    root = tk.Tk()
    root.title("AITool")
    root.configure(bg=BG)
    root.geometry("1100x800")
    root.resizable(True, True)

    # Center window
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw // 2) - (1100 // 2)
    y = (sh // 2) - (800 // 2)
    root.geometry(f"+{x}+{y}")

    # Container to hold all pages
    container = tk.Frame(root, bg=BG)
    container.pack(side="top", fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    frames = {}

    def show_frame(frame_name):
        frame = frames[frame_name]
        frame.tkraise()

    # Create home and settings frames
    home_frame = create_home_frame(
        container, 
        lambda: show_frame("generate"),
        lambda: show_frame("settings")
    )
    generate_frame = generate.create_generate_frame(container, lambda: show_frame("home"))
    settings_frame = setting.create_settings_frame(container, lambda: show_frame("home"))

    frames["home"] = home_frame
    frames["generate"] = generate_frame
    frames["settings"] = settings_frame

    for frame in frames.values():
        frame.grid(row=0, column=0, sticky="nsew")

    # Show home by default
    show_frame("home")

    # Keyboard: Esc to quit
    root.bind('<Escape>', lambda e: root.destroy())

    return root


def run():
    """Launch the application"""
    root = create_main_window()
    root.mainloop()


if __name__ == "__main__":
    run()
