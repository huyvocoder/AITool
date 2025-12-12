"""Settings UI for AITool"""
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
from core.service import config_manager
from core.view import notification

# UI Colors
BG = "#181818"
PANEL = "#1f1f1f"
TEXT = "#e6e6e6"
SUB = "#9aa0a6"
ACCENT = "#00a67e"


def create_settings_frame(parent, show_home_callback):
    """Create settings page frame"""
    frame = tk.Frame(parent, bg=BG)
    
    # Fonts
    header_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
    sub_font = tkfont.Font(family="Segoe UI", size=10)

    container = tk.Frame(frame, bg=BG, padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)

    top = tk.Frame(container, bg=BG)
    top.pack(fill=tk.X)

    title = tk.Label(top, text="Cài đặt", bg=BG, fg=TEXT, font=header_font)
    title.pack(anchor='w')
    subtitle = tk.Label(top, text="Quản lý cấu hình:", bg=BG, fg=SUB, font=sub_font)
    subtitle.pack(anchor='w', pady=(4, 12))

    # Panel
    panel = tk.Frame(container, bg=PANEL, padx=18, pady=18)
    panel.pack(fill=tk.BOTH, expand=True)

    # GEMINI_API_KEY setting
    lbl = tk.Label(panel, text="GEMINI_API_KEY:", bg=PANEL, fg=TEXT, font=("Segoe UI", 10))
    lbl.pack(anchor='w', pady=(0, 6))

    current = config_manager.get_gemini_key()
    entry_var = tk.StringVar(value=current)
    entry = tk.Entry(panel, textvariable=entry_var, width=50, bg="#2b2b2b", fg=TEXT, insertbackground=TEXT)
    entry.pack(anchor='w', pady=(0, 12))

    # Button area
    btn_frame = tk.Frame(panel, bg=PANEL)
    btn_frame.pack(fill=tk.X, pady=(20, 0))

    def save_settings():
        new_key = entry_var.get().strip()
        if not new_key:
            if not messagebox.askyesno("Xác nhận", "Bạn đang lưu một giá trị trống. Tiếp tục?"):
                return
        ok, info = config_manager.update_gemini_key(new_key)
        if ok:
            notification.show_notification(frame, "GEMINI_API_KEY đã được lưu.", type_="success")
        else:
            notification.show_notification(frame, f"Lỗi: {info}", type_="failed")

    save_btn = tk.Button(btn_frame, text="Lưu", command=save_settings, bg=ACCENT, fg=BG, bd=0, relief='flat', font=("Segoe UI", 10, "bold"))
    save_btn.pack(side=tk.RIGHT)

    back_btn = tk.Button(btn_frame, text="Quay lại", command=show_home_callback, bg="#444444", fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 10))
    back_btn.pack(side=tk.RIGHT, padx=(0, 8))

    return frame


def open_settings(parent: tk.Widget = None):
    """Open settings as a popup window (for legacy use)"""
    current = config_manager.get_gemini_key()

    win = tk.Toplevel(master=parent) if parent else tk.Toplevel()
    win.title("Cài đặt — AITool")
    win.configure(bg=BG)
    win.geometry("560x160")
    win.resizable(False, False)

    # Center on screen
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw // 2) - (560 // 2)
    y = (sh // 2) - (160 // 2)
    win.geometry(f"+{x}+{y}")

    lbl = tk.Label(win, text="GEMINI_API_KEY:", bg=BG, fg=TEXT, font=("Segoe UI", 10))
    lbl.pack(anchor='w', padx=16, pady=(18, 6))

    entry_var = tk.StringVar(value=current)
    entry = tk.Entry(win, textvariable=entry_var, width=72, bg="#2b2b2b", fg=TEXT, insertbackground=TEXT)
    entry.pack(padx=16)

    def on_save():
        new_key = entry_var.get().strip()
        if not new_key:
            if not messagebox.askyesno("Xác nhận", "Bạn đang lưu một giá trị trống. Tiếp tục?"):
                return
        ok, info = config_manager.update_gemini_key(new_key)
        if ok:
            notification.show_notification(win, "✓ GEMINI_API_KEY đã được lưu.", type_="success")
            win.after(1500, win.destroy)
        else:
            notification.show_notification(win, f"✗ Lỗi: {info}", type_="failed")

    btn_frame = tk.Frame(win, bg=BG)
    btn_frame.pack(fill=tk.X, padx=16, pady=12)

    save_btn = tk.Button(btn_frame, text="Lưu", command=on_save, bg=ACCENT, fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 10, "bold"))
    save_btn.pack(side=tk.RIGHT)

    cancel_btn = tk.Button(btn_frame, text="Hủy", command=win.destroy, bg="#444444", fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 10))
    cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))

    return win
    """Open settings dialog for editing configuration"""
    current = config_manager.get_gemini_key()

    win = tk.Toplevel(master=parent) if parent else tk.Toplevel()
    win.title("Cài đặt — AITool")
    win.configure(bg=BG)
    win.geometry("560x160")
    win.resizable(False, False)

    # Center on screen
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw // 2) - (560 // 2)
    y = (sh // 2) - (160 // 2)
    win.geometry(f"+{x}+{y}")

    lbl = tk.Label(win, text="GEMINI_API_KEY:", bg=BG, fg=TEXT, font=("Segoe UI", 10))
    lbl.pack(anchor='w', padx=16, pady=(18, 6))

    entry_var = tk.StringVar(value=current)
    entry = tk.Entry(win, textvariable=entry_var, width=72, bg="#2b2b2b", fg=TEXT, insertbackground=TEXT)
    entry.pack(padx=16)

    def on_save():
        new_key = entry_var.get().strip()
        if not new_key:
            if not messagebox.askyesno("Xác nhận", "Bạn đang lưu một giá trị trống. Tiếp tục?"):
                return
        ok, info = config_manager.update_gemini_key(new_key)
        if ok:
            notification.show_notification(win, "✓ GEMINI_API_KEY đã được lưu.", type_="success")
            win.after(1500, win.destroy)
        else:
            notification.show_notification(win, f"✗ Lỗi: {info}", type_="failed")

    btn_frame = tk.Frame(win, bg=BG)
    btn_frame.pack(fill=tk.X, padx=16, pady=12)

    save_btn = tk.Button(btn_frame, text="Lưu", command=on_save, bg=ACCENT, fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 10, "bold"))
    save_btn.pack(side=tk.RIGHT)

    cancel_btn = tk.Button(btn_frame, text="Hủy", command=win.destroy, bg="#444444", fg=TEXT, bd=0, relief='flat', font=("Segoe UI", 10))
    cancel_btn.pack(side=tk.RIGHT, padx=(0, 8))

    return win
