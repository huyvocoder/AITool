import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
import threading
import os
import subprocess
import shutil

from core.mainflowgenVideo.main_flow import run_full_flow
from core.constants.project_constants import MODEL_VIDEO_KEYS, SCENES_PER_BATCH

# Global variables
current_video_data = None  # Store encoded video và metadata
video_player = None


def enable_video_buttons():
    """Enable video control buttons."""
    try:
        play_btn.config(state="normal")
        download_btn.config(state="normal")
    except:
        pass


def play_video_in_app():
    """Hiển thị video player inline trong app."""
    global current_video_data, video_player
    
    if not current_video_data:
        messagebox.showwarning("Không có video", "Chưa có video để xem!")
        return
    
    try:
        import base64
        import tempfile
        
        # Tạo temp file để play video
        encoded_video = current_video_data.get('encoded_video')
        video_data = base64.b64decode(encoded_video)
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(video_data)
        temp_file.close()
        
        # Open with default player
        os.startfile(temp_file.name)
        
        video_display.insert(tk.END, "\n🎬 Video đang phát...\n")
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể phát video:\n{str(e)}")


def download_video():
    """Download video từ encoded string."""
    global current_video_data
    
    if not current_video_data:
        messagebox.showwarning("Không có video", "Chưa có video để download!")
        return
    
    # Mở dialog để chọn nơi save
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"video_{timestamp}.mp4"
    
    save_path = filedialog.asksaveasfilename(
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
        initialfile=default_filename
    )
    
    if save_path:
        try:
            import base64
            
            encoded_video = current_video_data.get('encoded_video')
            video_data = base64.b64decode(encoded_video)
            
            # Save file
            with open(save_path, 'wb') as f:
                f.write(video_data)
            
            file_size = os.path.getsize(save_path) / 1024 / 1024
            messagebox.showinfo("Thành công", f"Video đã được lưu tại:\n{save_path}\n\nKích thước: {file_size:.2f} MB")
            
            video_display.insert(tk.END, f"\n💾 Downloaded: {save_path}\n")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu video:\n{str(e)}")


def start_process():
    selected_model = model_var.get()
    model_key = MODEL_VIDEO_KEYS.get(selected_model, "")
    
    # Lấy số lượng scenes từ input
    try:
        num_scenes = int(scenes_entry.get())
        if num_scenes <= 0:
            messagebox.showerror("Lỗi", "Số lượng scenes phải > 0!")
            return
    except ValueError:
        messagebox.showerror("Lỗi", "Vui lòng nhập số lượng scenes hợp lệ!")
        return
    
    log_box.delete(1.0, tk.END)
    video_display.delete(1.0, tk.END)
    
    log_box.insert(tk.END, f"🚀 Bắt đầu chạy full flow...\n")
    log_box.insert(tk.END, f"🤖 Model: {selected_model}\n")
    log_box.insert(tk.END, f"🔑 Model Key: {model_key}\n")
    log_box.insert(tk.END, f"🎬 Số scenes: {num_scenes}\n")
    log_box.insert(tk.END, f"📦 Batch size: {SCENES_PER_BATCH} scenes/batch\n\n")
    
    start_btn.config(state="disabled", text="ĐANG CHẠY...")

    def run():
        global current_video_data
        try:
            result = run_full_flow(model_key, log_box, num_scenes)
            log_box.insert(tk.END, f"\n✅ HOÀN TẤT!\n")
            
            # Lưu video data (encoded video + metadata)
            if isinstance(result, dict):
                current_video_data = result
                
                # Hiển thị video info
                video_display.delete(1.0, tk.END)
                video_display.insert(tk.END, "=" * 50 + "\n")
                video_display.insert(tk.END, "🎬 VIDEO ĐÃ TẠO THÀNH CÔNG\n")
                video_display.insert(tk.END, "=" * 50 + "\n\n")
                
                # Estimate size
                import base64
                encoded_size = len(current_video_data.get('encoded_video', ''))
                estimated_mb = (encoded_size * 3 / 4) / 1024 / 1024  # Base64 to bytes
                
                video_display.insert(tk.END, f"📊 Kích thước ước tính: {estimated_mb:.2f} MB\n")
                video_display.insert(tk.END, f"🎲 Seed: {current_video_data.get('seed')}\n")
                video_display.insert(tk.END, f"📁 Project ID: {current_video_data.get('project_id', 'N/A')[:20]}...\n\n")
                
                video_display.insert(tk.END, "🎯 Video sẵn sàng!\n\n")
                video_display.insert(tk.END, "Sử dụng các nút bên dưới để:\n")
                video_display.insert(tk.END, "  • ▶️ Xem video\n")
                video_display.insert(tk.END, "  • 💾 Download về máy\n")
                
                # Enable buttons
                root.after(100, lambda: enable_video_buttons())
            else:
                video_display.delete(1.0, tk.END)
                video_display.insert(tk.END, f"❌ Lỗi: {result}\n")
            
        except Exception as e:
            log_box.insert(tk.END, f"\n❌ LỖI: {str(e)}\n")
            video_display.delete(1.0, tk.END)
            video_display.insert(tk.END, f"❌ Có lỗi xảy ra:\n{str(e)}\n")
        finally:
            start_btn.config(state="normal", text="🎬 GEN VIDEO")

    threading.Thread(target=run, daemon=True).start()


# ========== MAIN WINDOW ==========
root = tk.Tk()
root.title("🎬 AI Video Generator - Google Labs Veo3")
root.geometry("1400x800")
root.configure(bg="#1e1e1e")

# ========== TOP FRAME - MODEL SELECTION ==========
top_frame = tk.Frame(root, bg="#2d2d2d", height=80)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
top_frame.pack_propagate(False)

# Model Selection Label
tk.Label(
    top_frame, 
    text="🤖 Chọn Model AI:", 
    bg="#2d2d2d", 
    fg="white",
    font=("Arial", 12, "bold")
).pack(side=tk.LEFT, padx=20, pady=20)

# Model Dropdown
model_var = tk.StringVar(value="veo3")
model_dropdown = ttk.Combobox(
    top_frame,
    textvariable=model_var,
    values=list(MODEL_VIDEO_KEYS.keys()),
    state="readonly",
    width=30,
    font=("Arial", 11)
)
model_dropdown.pack(side=tk.LEFT, padx=10, pady=20)

# Số lượng scenes input
tk.Label(
    top_frame,
    text="🎬 Scenes:",
    bg="#2d2d2d",
    fg="#00a67e",
    font=("Arial", 11, "bold")
).pack(side=tk.LEFT, padx=(20, 5))

scenes_entry = tk.Entry(
    top_frame,
    width=5,
    font=("Arial", 12),
    justify="center"
)
scenes_entry.insert(0, "4")  # Default 4 scenes
scenes_entry.pack(side=tk.LEFT, padx=5)

tk.Label(
    top_frame,
    text=f"({SCENES_PER_BATCH}/batch)",
    bg="#2d2d2d",
    fg="#888888",
    font=("Arial", 9)
).pack(side=tk.LEFT, padx=5)

# Gen Video Button
start_btn = tk.Button(
    top_frame,
    text="🎬 GEN VIDEO",
    command=start_process,
    bg="#00a67e",
    fg="white",
    font=("Arial", 14, "bold"),
    width=15,
    height=2,
    relief=tk.RAISED,
    cursor="hand2"
)
start_btn.pack(side=tk.LEFT, padx=20, pady=10)

# Status Label
status_label = tk.Label(
    top_frame,
    text="⚡ Sẵn sàng",
    bg="#2d2d2d",
    fg="#00ff00",
    font=("Arial", 11, "bold")
)
status_label.pack(side=tk.LEFT, padx=20)

# ========== BOTTOM FRAME - 2 COLUMNS ==========
bottom_frame = tk.Frame(root, bg="#1e1e1e")
bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# ========== LEFT COLUMN - PROCESS LOG ==========
left_frame = tk.Frame(bottom_frame, bg="#2d2d2d")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

tk.Label(
    left_frame,
    text="📊 QUÁ TRÌNH CHẠY",
    bg="#2d2d2d",
    fg="#00a67e",
    font=("Arial", 12, "bold")
).pack(pady=10)

log_box = scrolledtext.ScrolledText(
    left_frame,
    width=60,
    height=35,
    bg="#1e1e1e",
    fg="#00ff00",
    font=("Consolas", 10),
    insertbackground="white",
    wrap=tk.WORD
)
log_box.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

# ========== RIGHT COLUMN - VIDEO OUTPUT ==========
right_frame = tk.Frame(bottom_frame, bg="#2d2d2d")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

tk.Label(
    right_frame,
    text="🎥 VIDEO OUTPUT",
    bg="#2d2d2d",
    fg="#00a67e",
    font=("Arial", 12, "bold")
).pack(pady=10)

video_display = scrolledtext.ScrolledText(
    right_frame,
    width=60,
    height=30,
    bg="#1e1e1e",
    fg="#ffffff",
    font=("Consolas", 10),
    insertbackground="white",
    wrap=tk.WORD
)
video_display.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

# Initial message
video_display.insert(tk.END, "=" * 50 + "\n")
video_display.insert(tk.END, "🎬 CHƯA CÓ VIDEO\n")
video_display.insert(tk.END, "=" * 50 + "\n\n")
video_display.insert(tk.END, "Video sẽ xuất hiện ở đây\n")
video_display.insert(tk.END, "sau khi quá trình gen hoàn tất.\n\n")
video_display.insert(tk.END, "Nhấn 'GEN VIDEO' để bắt đầu!")

# ========== VIDEO CONTROLS ==========
controls_frame = tk.Frame(right_frame, bg="#2d2d2d", height=60)
controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
controls_frame.pack_propagate(False)

# Play Video Button
play_btn = tk.Button(
    controls_frame,
    text="▶️ XEM VIDEO",
    command=play_video_in_app,
    bg="#0066cc",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20,
    height=2,
    state="disabled",
    cursor="hand2"
)
play_btn.pack(side=tk.LEFT, padx=10, pady=10)

# Download Button
download_btn = tk.Button(
    controls_frame,
    text="💾 DOWNLOAD",
    command=download_video,
    bg="#00a67e",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20,
    height=2,
    state="disabled",
    cursor="hand2"
)
download_btn.pack(side=tk.LEFT, padx=10, pady=10)

root.mainloop()
