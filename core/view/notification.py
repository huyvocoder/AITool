"""Custom notification/toast system for AITool"""
import tkinter as tk
from typing import Literal

# Colors
COLORS = {
    "success": {"bg": "#22c55e", "fg": "#ffffff", "icon": "✓"},
    "failed": {"bg": "#ef4444", "fg": "#ffffff", "icon": "✗"},
    "information": {"bg": "#eab308", "fg": "#1f2937", "icon": "ℹ"}
}

# Global notification reference
_current_notification = None


def show_notification(container: tk.Widget, message: str, type_: Literal["success", "failed", "information"] = "information", duration: int = 3000):
    """Show a notification in the top-right corner of the container.
    
    Args:
        container: Parent frame/window to show notification in
        message: Message text
        type_: "success", "failed", or "information"
        duration: How long to show in milliseconds (default 3000ms)
    """
    global _current_notification
    
    if type_ not in COLORS:
        type_ = "information"
    
    # Remove previous notification if exists
    if _current_notification and _current_notification.winfo_exists():
        try:
            _current_notification.destroy()
        except:
            pass
    
    colors = COLORS[type_]
    icon = colors["icon"]
    
    # Create notification frame positioned in top-right corner
    notif_frame = tk.Frame(container, bg=colors["bg"], relief="solid", bd=1, highlightthickness=0)
    
    # Add padding with inner frame
    inner = tk.Frame(notif_frame, bg=colors["bg"], padx=12, pady=8)
    inner.pack(fill=tk.BOTH, expand=True)
    
    # Icon + message
    text = tk.Label(
        inner,
        text=f"{icon}  {message}",
        bg=colors["bg"],
        fg=colors["fg"],
        font=("Segoe UI", 10),
        wraplength=300
    )
    text.pack()
    
    # Position in top-right corner using place geometry
    notif_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
    
    _current_notification = notif_frame
    
    # Auto-remove after duration
    def remove_notif():
        global _current_notification
        try:
            if _current_notification == notif_frame and notif_frame.winfo_exists():
                notif_frame.destroy()
                _current_notification = None
        except:
            pass
    
    container.after(duration, remove_notif)
    
    return notif_frame

