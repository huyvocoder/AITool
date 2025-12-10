"""
Module để extract cookies từ Chrome browser.
Tách riêng để code app.py gọn hơn, dễ maintain.
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import os
import subprocess
import shutil
import json
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import base64


def get_chrome_encryption_key():
    """Lấy encryption key của Chrome từ Local State."""
    local_state_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), 
                                    "Google", "Chrome", "User Data", "Local State")
    
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.load(f)
    
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  # Remove 'DPAPI' prefix
    
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]


def decrypt_cookie_value(encrypted_value, key):
    """
    Decrypt Chrome cookie value.
    Supports both v10/v11 (AES-GCM) and old DPAPI format.
    """
    try:
        # Chrome v80+ format: v10 or v11 prefix
        if encrypted_value[:3] == b'v10' or encrypted_value[:3] == b'v11':
            nonce = encrypted_value[3:3+12]
            ciphertext = encrypted_value[3+12:-16]
            tag = encrypted_value[-16:]
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode('utf-8')
        else:
            # Old format (DPAPI)
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
    except Exception as e:
        return ""  # Return empty string if decrypt fails


def extract_token_from_chrome(root, status_label):
    """
    Tự động lấy token từ Chrome với giao diện.
    TOÀN BỘ logic UI và extraction đều ở đây.
    """
    
    # Tạo popup window
    popup = tk.Toplevel(root)
    popup.title("🔑 Lấy Token Tự Động")
    popup.geometry("600x500")
    popup.configure(bg="#1e1e1e")
    popup.resizable(False, False)
    
    # Center window
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (600 // 2)
    y = (popup.winfo_screenheight() // 2) - (500 // 2)
    popup.geometry(f"+{x}+{y}")
    
    # Title
    title_frame = tk.Frame(popup, bg="#2d2d2d", height=60)
    title_frame.pack(fill=tk.X)
    title_frame.pack_propagate(False)
    
    tk.Label(
        title_frame,
        text="🔑 TỰ ĐỘNG LẤY TOKEN TỪ CHROME",
        bg="#2d2d2d",
        fg="#00a67e",
        font=("Arial", 16, "bold")
    ).pack(pady=15)
    
    # Log area
    log_frame = tk.Frame(popup, bg="#1e1e1e")
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    log_text = scrolledtext.ScrolledText(
        log_frame,
        bg="#1e1e1e",
        fg="#00ff00",
        font=("Consolas", 10),
        wrap=tk.WORD,
        height=20
    )
    log_text.pack(fill=tk.BOTH, expand=True)
    
    # Initial instructions
    log_text.insert(tk.END, "=" * 60 + "\n")
    log_text.insert(tk.END, "  CHỌN PHƯƠNG PHÁP LẤY TOKEN\n")
    log_text.insert(tk.END, "=" * 60 + "\n\n")
    
    log_text.insert(tk.END, "🎯 PHƯƠNG PHÁP 1: PASTE NHANH (Khuyến nghị!)\n")
    log_text.insert(tk.END, "   ✅ Chrome có thể MỞ\n")
    log_text.insert(tk.END, "   ✅ Copy-paste trực tiếp từ DevTools\n")
    log_text.insert(tk.END, "   ✅ Nhanh nhất, dễ nhất\n")
    log_text.insert(tk.END, "   → Nhấn nút 'PASTE NHANH' bên dưới!\n\n")
    
    log_text.insert(tk.END, "🤖 PHƯƠNG PHÁP 2: TỰ ĐỘNG\n")
    log_text.insert(tk.END, "   ⚠️  Phải ĐÓNG Chrome hoàn toàn\n")
    log_text.insert(tk.END, "   ⚠️  Cookies bị lock khi Chrome chạy\n")
    log_text.insert(tk.END, "   → Nhấn nút 'BẮT ĐẦU LẤY TOKEN'\n\n")
    
    log_text.insert(tk.END, "📝 PHƯƠNG PHÁP 3: THỦ CÔNG\n")
    log_text.insert(tk.END, "   📋 Tạo file auto_tokens.json thủ công\n")
    log_text.insert(tk.END, "   → Nhấn nút 'THỦ CÔNG' để xem hướng dẫn\n\n")
    
    log_text.insert(tk.END, "=" * 60 + "\n\n")
    log_text.insert(tk.END, "💡 ĐỀ XUẤT: Dùng 'PASTE NHANH' - Không cần đóng Chrome!\n\n")
    
    # Button frame
    btn_frame = tk.Frame(popup, bg="#1e1e1e", height=80)
    btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
    btn_frame.pack_propagate(False)
    
    def kill_chrome_and_extract():
        """Kill Chrome và extract - tự động 100%."""
        
        auto_btn.config(state="disabled", text="⏳ ĐANG XỬ LÝ...")
        extract_btn.config(state="disabled")
        close_btn.config(state="disabled")
        
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "=" * 60 + "\n")
        log_text.insert(tk.END, "  TỰ ĐỘNG 100% (Kill Chrome)\n")
        log_text.insert(tk.END, "=" * 60 + "\n\n")
        log_text.see(tk.END)
        popup.update()
        
        def do_auto():
            try:
                import time
                
                # Step 1: Kill Chrome
                log_text.insert(tk.END, "1️⃣ Đang đóng Chrome...\n")
                log_text.see(tk.END)
                popup.update()
                
                try:
                    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                                  capture_output=True, timeout=5)
                    time.sleep(2)
                    log_text.insert(tk.END, "✅ Chrome đã đóng\n\n")
                except:
                    log_text.insert(tk.END, "⚠️  Chrome có thể chưa chạy\n\n")
                
                log_text.see(tk.END)
                popup.update()
                
                # Step 2: Extract
                log_text.insert(tk.END, "2️⃣ Đang extract cookies...\n")
                log_text.see(tk.END)
                popup.update()
                
                # Extract - Quét TẤT CẢ profiles, chỉ lấy cookies labs.google
                session_token = None
                csrf_token = None
                callback_url = None
                
                local_app_data = os.environ.get("LOCALAPPDATA", "")
                chrome_base = os.path.join(local_app_data, "Google", "Chrome", "User Data")
                
                # Quét 10 profiles cố định
                all_profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", 
                               "Profile 5", "Profile 6", "Profile 7", "Profile 8", "Profile 9"]
                
                log_text.insert(tk.END, f"🔍 Sẽ quét {len(all_profiles)} profiles, tìm profile có labs.google cookies...\n\n")
                log_text.see(tk.END)
                popup.update()
                
                for profile_name in all_profiles:
                    cookies_db = os.path.join(chrome_base, profile_name, "Network", "Cookies")
                    
                    # Skip nếu profile không tồn tại
                    if not os.path.exists(cookies_db):
                        log_text.insert(tk.END, f"   {profile_name}... ⚠️ không tồn tại\n")
                        log_text.see(tk.END)
                        popup.update()
                        continue
                    
                    try:
                        log_text.insert(tk.END, f"   {profile_name}... ")
                        log_text.see(tk.END)
                        popup.update()
                        
                        temp_db = "temp_cookies_auto.db"
                        shutil.copy2(cookies_db, temp_db)
                        
                        # Lấy encryption key
                        encryption_key = get_chrome_encryption_key()
                        
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        
                        # Query: lấy cả encrypted_value - dùng LIKE để bắt tất cả biến thể
                        cursor.execute("""
                            SELECT name, value, encrypted_value, host_key
                            FROM cookies
                            WHERE host_key LIKE '%labs.google%'
                        """)
                        
                        rows = cursor.fetchall()
                        
                        if rows:
                            log_text.insert(tk.END, f"✅ {len(rows)} cookies:\n\n")
                            
                            # Dictionary để lưu TẤT CẢ cookies
                            all_cookies = {}
                            cookie_string_parts = []
                            
                            # Parse cookies cần thiết
                            for name, old_value, encrypted_value, host in rows:
                                # Decrypt value
                                if encrypted_value:
                                    value = decrypt_cookie_value(encrypted_value, encryption_key)
                                else:
                                    value = old_value
                                
                                # Lưu vào dict
                                all_cookies[name] = value
                                
                                # Build cookie string: name=value
                                cookie_string_parts.append(f"{name}={value}")
                                
                                # Show FULL value
                                log_text.insert(tk.END, f"      🔹 {name}\n")
                                log_text.insert(tk.END, f"         Host: {host}\n")
                                log_text.insert(tk.END, f"         Value: {value}\n\n")
                                log_text.see(tk.END)
                                popup.update()
                                
                                # Parse các field quan trọng
                                if name == "__Secure-next-auth.session-token":
                                    session_token = value
                                    log_text.insert(tk.END, f"         ✅ Đã lưu session_token!\n\n")
                                elif name == "__Host-next-auth.csrf-token":
                                    csrf_token = value.split("|")[0] if "|" in value else value
                                    log_text.insert(tk.END, f"         ✅ Đã lưu csrf_token!\n\n")
                                elif name == "__Secure-next-auth.callback-url":
                                    callback_url = value
                                    log_text.insert(tk.END, f"         ✅ Đã lưu callback_url!\n\n")
                            
                            # Tạo cookie string
                            cookie_string = "; ".join(cookie_string_parts)
                            
                            log_text.insert(tk.END, f"\n📊 Kết quả parse:\n")
                            log_text.insert(tk.END, f"   session_token: {'✅ CÓ' if session_token else '❌ KHÔNG'}\n")
                            log_text.insert(tk.END, f"   csrf_token: {'✅ CÓ' if csrf_token else '❌ KHÔNG'}\n")
                            log_text.insert(tk.END, f"   callback_url: {'✅ CÓ' if callback_url else '❌ KHÔNG'}\n\n")
                            log_text.see(tk.END)
                            popup.update()
                            
                            conn.close()
                            os.remove(temp_db)
                            
                            # Chỉ BREAK khi có ĐỦ session_token VÀ csrf_token (callback_url optional)
                            if session_token and csrf_token:
                                log_text.insert(tk.END, f"   ✅ Đã có đủ cookies cần thiết ở {profile_name}! Dừng quét.\n\n")
                                log_text.see(tk.END)
                                break
                            else:
                                log_text.insert(tk.END, f"   ⚠️  Chưa đủ cookies, tiếp tục profile tiếp theo...\n\n")
                                log_text.see(tk.END)
                        else:
                            log_text.insert(tk.END, "❌ không có labs.google\n")
                        
                        conn.close()
                        os.remove(temp_db)
                            
                    except Exception as e:
                        log_text.insert(tk.END, f"⚠️\n")
                        if os.path.exists(temp_db):
                            try:
                                os.remove(temp_db)
                            except:
                                pass
                        continue
                
                if session_token and csrf_token:
                    # Save với TẤT CẢ cookies
                    token_data = {
                        "id": "auto_killed_chrome",
                        "sessionToken": session_token,
                        "csrfToken": csrf_token,
                        "callbackUrl": callback_url or "https://labs.google",
                        "cookieString": cookie_string,
                        "allCookies": all_cookies
                    }
                    
                    with open("auto_tokens.json", 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    log_text.insert(tk.END, "\n" + "=" * 60 + "\n")
                    log_text.insert(tk.END, "  🎉 THÀNH CÔNG!\n")
                    log_text.insert(tk.END, "=" * 60 + "\n\n")
                    log_text.insert(tk.END, "💾 Đã lưu vào: auto_tokens.json\n\n")
                    log_text.see(tk.END)
                    
                    status_label.config(text="✅ Token đã cập nhật", fg="#00ff00")
                    
                    # Step 3: Reopen Chrome
                    log_text.insert(tk.END, "3️⃣ Đang mở lại Chrome...\n")
                    log_text.see(tk.END)
                    popup.update()
                    
                    try:
                        chrome_paths = [
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        ]
                        
                        for path in chrome_paths:
                            if os.path.exists(path):
                                subprocess.Popen([path, "https://labs.google/fx"])
                                log_text.insert(tk.END, "✅ Chrome đã mở lại\n\n")
                                break
                    except:
                        log_text.insert(tk.END, "⚠️  Không mở lại được Chrome (bạn có thể mở thủ công)\n\n")
                    
                    log_text.see(tk.END)
                    auto_btn.config(state="normal", text="🤖 TỰ ĐỘNG 100%")
                    close_btn.config(state="normal", text="✅ ĐÓNG")
                    
                    messagebox.showinfo("Thành công", "Token đã được lấy tự động!\n\nChrome đã mở lại labs.google/fx")
                    
                else:
                    log_text.insert(tk.END, "\n❌ Không tìm thấy cookies!\n")
                    log_text.insert(tk.END, "💡 Hãy đăng nhập labs.google/fx trước khi extract\n")
                    log_text.see(tk.END)
                    
                    auto_btn.config(state="normal", text="🔄 THỬ LẠI")
                    extract_btn.config(state="normal")
                    close_btn.config(state="normal")
                    
                    messagebox.showwarning("Lỗi", "Không tìm thấy cookies!\n\nHãy đăng nhập vào Chrome trước.")
                    
            except Exception as e:
                log_text.insert(tk.END, f"\n❌ Lỗi: {str(e)}\n")
                log_text.see(tk.END)
                
                auto_btn.config(state="normal", text="🔄 THỬ LẠI")
                extract_btn.config(state="normal")
                close_btn.config(state="normal")
                
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")
        
        threading.Thread(target=do_auto, daemon=True).start()
    
    def run_extraction():
        """Chạy extraction (không kill Chrome)."""
        extract_btn.config(state="disabled", text="⏳ ĐANG LẤY...")
        auto_btn.config(state="disabled")
        close_btn.config(state="disabled")
        
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "=" * 60 + "\n")
        log_text.insert(tk.END, "  BẮT ĐẦU EXTRACTION (Chrome phải đóng)\n")
        log_text.insert(tk.END, "=" * 60 + "\n\n")
        log_text.see(tk.END)
        
        def extract_direct_sqlite():
            """Đọc trực tiếp từ SQLite database - chính xác hơn."""
            
            log_text.insert(tk.END, "🔍 Đang quét Chrome SQLite database...\n")
            log_text.see(tk.END)
            popup.update()
            
            session_token = None
            csrf_token = None
            email = None
            
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            chrome_base = os.path.join(local_app_data, "Google", "Chrome", "User Data")
            
            profiles_to_check = ["Default", "Profile 1", "Profile 2", "Profile 3", 
                                "Profile 4", "Profile 5", "Profile 6", "Profile 7", "Profile 8"]
            
            for profile_name in profiles_to_check:
                if session_token and csrf_token:
                    break
                
                cookies_db = os.path.join(chrome_base, profile_name, "Network", "Cookies")
                
                if not os.path.exists(cookies_db):
                    continue
                
                try:
                    log_text.insert(tk.END, f"   Checking {profile_name}...\n")
                    log_text.see(tk.END)
                    popup.update()
                    
                    # Copy database to temp (vì bị lock)
                    temp_db = "temp_cookies.db"
                    shutil.copy2(cookies_db, temp_db)
                    
                    # Connect to database
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    
                    # Query cookies cho labs.google
                    cursor.execute("""
                        SELECT name, value, encrypted_value
                        FROM cookies
                        WHERE host_key LIKE '%labs.google%'
                    """)
                    
                    rows = cursor.fetchall()
                    
                    if rows:
                        log_text.insert(tk.END, f"\n✅ Tìm thấy {len(rows)} cookies ở {profile_name}!\n")
                        
                        for name, value, encrypted_value in rows:
                            # Dùng plain value nếu có
                            cookie_value = value if value else ""
                            
                            if "session-token" in name.lower():
                                session_token = cookie_value
                                log_text.insert(tk.END, f"✅ Session Token: {session_token[:40]}...\n")
                            
                            elif "csrf-token" in name.lower():
                                csrf_token = cookie_value.split("|")[0] if "|" in cookie_value else cookie_value
                                log_text.insert(tk.END, f"✅ CSRF Token: {csrf_token[:40]}...\n")
                            
                            elif name.upper() == "EMAIL":
                                email = cookie_value
                                log_text.insert(tk.END, f"✅ Email: {email}\n")
                            
                            log_text.see(tk.END)
                            popup.update()
                    
                    conn.close()
                    os.remove(temp_db)
                    
                    if session_token:
                        break
                        
                except Exception as e:
                    if os.path.exists(temp_db):
                        try:
                            os.remove(temp_db)
                        except:
                            pass
                    continue
            
            return session_token, csrf_token, email
        
        def extract():
            try:
                # Thử phương pháp 1: Đọc trực tiếp SQLite
                log_text.insert(tk.END, "📚 Phương pháp 1: Đọc trực tiếp SQLite database\n\n")
                log_text.see(tk.END)
                popup.update()
                
                session_token, csrf_token, email = extract_direct_sqlite()
                
                if session_token and csrf_token:
                    # Thành công!
                    token_data = {
                        "id": "auto_extracted",
                        "sessionToken": session_token,
                        "csrfToken": csrf_token,
                        "email": email or "user@gmail.com"
                    }
                    
                    with open("auto_tokens.json", 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    log_text.insert(tk.END, "\n" + "=" * 60 + "\n")
                    log_text.insert(tk.END, "  🎉 THÀNH CÔNG!\n")
                    log_text.insert(tk.END, "=" * 60 + "\n\n")
                    log_text.insert(tk.END, "💾 Đã lưu vào: auto_tokens.json\n")
                    log_text.insert(tk.END, "✨ App sẽ tự động dùng token này!\n\n")
                    log_text.see(tk.END)
                    
                    status_label.config(text="✅ Token đã cập nhật", fg="#00ff00")
                    close_btn.config(state="normal", text="✅ ĐÓNG")
                    
                    messagebox.showinfo("Thành công", "Token đã được lấy và lưu thành công!\n\nGiờ bạn có thể gen video!")
                    return
                
                # Nếu không thành công, thử phương pháp 2
                log_text.insert(tk.END, "\n⚠️  Phương pháp 1 không đủ cookies.\n")
                log_text.insert(tk.END, "📚 Phương pháp 2: Dùng browser_cookie3\n\n")
                log_text.see(tk.END)
                popup.update()
                
                import browser_cookie3
                
                log_text.insert(tk.END, "🔍 Đang quét TOÀN BỘ Chrome profiles...\n")
                log_text.see(tk.END)
                popup.update()
                
                session_token = None
                csrf_token = None
                email = None
                
                # Thử tất cả profiles
                local_app_data = os.environ.get("LOCALAPPDATA", "")
                chrome_base = os.path.join(local_app_data, "Google", "Chrome", "User Data")
                
                profiles_to_check = ["Default", "Profile 1", "Profile 2", "Profile 3", 
                                    "Profile 4", "Profile 5", "Profile 6", "Profile 7", "Profile 8"]
                
                found_profile = None
                
                for profile_name in profiles_to_check:
                    if session_token and csrf_token:  # Đã tìm đủ cả 2
                        break
                        
                    try:
                        log_text.insert(tk.END, f"   Checking {profile_name}...\n")
                        log_text.see(tk.END)
                        popup.update()
                        
                        # Load cookies từ profile cụ thể
                        # Lấy TOÀN BỘ cookies rồi filter theo domain thủ công
                        if profile_name == "Default":
                            cookies = browser_cookie3.chrome()
                        else:
                            # Construct profile path
                            cookies = browser_cookie3.chrome(
                                cookie_file=os.path.join(chrome_base, profile_name, "Network", "Cookies")
                            )
                        
                        # Filter chỉ lấy cookies từ labs.google
                        cookie_list = [c for c in cookies if 'labs.google' in c.domain.lower()]
                        
                        if not cookie_list:
                            # Thử filter khác
                            cookie_list = [c for c in cookies if '.google' in c.domain.lower() and 'labs' in str(c)]
                        
                        # Check xem profile này có session token không
                        has_session = any(c.name == "__Secure-next-auth.session-token" for c in cookie_list)
                        
                        if has_session and not session_token:
                            log_text.insert(tk.END, f"\n✅ Tìm thấy ở {profile_name}!\n")
                            found_profile = profile_name
                        
                        # Parse tất cả cookies từ profile này
                        for cookie in cookie_list:
                            cookie_name = cookie.name.lower()
                            
                            # Session token - nhiều biến thể
                            if "session-token" in cookie_name and not session_token:
                                session_token = cookie.value
                                log_text.insert(tk.END, f"✅ Session Token ({cookie.name}): {session_token[:40]}...\n")
                            
                            # CSRF token - nhiều biến thể
                            elif "csrf-token" in cookie_name and not csrf_token:
                                csrf_token = cookie.value.split("|")[0] if "|" in cookie.value else cookie.value
                                log_text.insert(tk.END, f"✅ CSRF Token ({cookie.name}): {csrf_token[:40]}...\n")
                            
                            # Email - nhiều biến thể
                            elif cookie.name.upper() == "EMAIL" and not email:
                                email = cookie.value
                                log_text.insert(tk.END, f"✅ Email: {email}\n")
                            
                            log_text.see(tk.END)
                            popup.update()
                            
                        # Nếu tìm thấy session token ở profile này thì dừng
                        if has_session:
                            break
                            
                    except Exception as e:
                        # log_text.insert(tk.END, f"   ⚠️ {profile_name}: {str(e)[:50]}\n")
                        continue  # Profile không có hoặc bị lỗi, thử profile tiếp
                
                if not session_token:
                    log_text.insert(tk.END, "\n⚠️  Đã quét tất cả profiles nhưng không tìm thấy!\n")
                    log_text.see(tk.END)
                    popup.update()
                elif not csrf_token:
                    log_text.insert(tk.END, "\n⚠️  Tìm thấy Session Token nhưng không có CSRF Token!\n")
                    log_text.insert(tk.END, "💡 Thử dùng nút 'PASTE NHANH' để nhập thủ công.\n")
                    log_text.see(tk.END)
                    popup.update()
                
                if session_token and csrf_token:
                    token_data = {
                        "id": "auto_extracted",
                        "sessionToken": session_token,
                        "csrfToken": csrf_token,
                        "email": email or "user@gmail.com"
                    }
                    
                    # Lưu vào file
                    with open("auto_tokens.json", 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    log_text.insert(tk.END, "\n" + "=" * 60 + "\n")
                    log_text.insert(tk.END, "  🎉 THÀNH CÔNG!\n")
                    log_text.insert(tk.END, "=" * 60 + "\n\n")
                    log_text.insert(tk.END, "💾 Đã lưu vào: auto_tokens.json\n")
                    log_text.insert(tk.END, "✨ App sẽ tự động dùng token này!\n\n")
                    log_text.insert(tk.END, "📌 Token có thể dùng được ~24 giờ\n")
                    log_text.insert(tk.END, "📌 Khi hết hạn, chỉ cần nhấn nút này lại!\n\n")
                    log_text.see(tk.END)
                    
                    # Update status
                    status_label.config(text="✅ Token đã cập nhật", fg="#00ff00")
                    
                    # Enable close button
                    close_btn.config(state="normal", text="✅ ĐÓNG")
                    
                    messagebox.showinfo("Thành công", "Token đã được lấy và lưu thành công!\n\nGiờ bạn có thể gen video!")
                    
                else:
                    log_text.insert(tk.END, "\n❌ THẤT BẠI!\n\n")
                    log_text.insert(tk.END, "Không tìm thấy đủ cookies!\n\n")
                    log_text.insert(tk.END, "💡 Hãy:\n")
                    log_text.insert(tk.END, "   1. Mở Chrome\n")
                    log_text.insert(tk.END, "   2. Truy cập https://labs.google/fx\n")
                    log_text.insert(tk.END, "   3. Đăng nhập\n")
                    log_text.insert(tk.END, "   4. Giữ tab mở và thử lại\n\n")
                    log_text.see(tk.END)
                    
                    extract_btn.config(state="normal", text="🔄 THỬ LẠI")
                    close_btn.config(state="normal")
                    
                    messagebox.showwarning("Lỗi", "Không tìm thấy cookies!\n\nHãy đăng nhập vào Chrome trước.")
                    
            except ImportError:
                log_text.insert(tk.END, "\n❌ Chưa cài browser-cookie3!\n\n")
                log_text.insert(tk.END, "💡 Đang tự động cài đặt...\n")
                log_text.see(tk.END)
                popup.update()
                
                try:
                    subprocess.check_call(["pip", "install", "browser-cookie3"])
                    log_text.insert(tk.END, "✅ Đã cài xong! Thử lại...\n\n")
                    log_text.see(tk.END)
                    extract()  # Retry
                except Exception as e:
                    log_text.insert(tk.END, f"❌ Lỗi cài đặt: {e}\n")
                    log_text.see(tk.END)
                    extract_btn.config(state="normal", text="🔄 THỬ LẠI")
                    close_btn.config(state="normal")
                    
            except Exception as e:
                error_msg = str(e)
                log_text.insert(tk.END, f"\n❌ Lỗi: {error_msg}\n\n")
                
                # Diagnose the error
                if "PermissionError" in error_msg or "Permission denied" in error_msg:
                    log_text.insert(tk.END, "💡 Chrome đang chạy! Hãy:\n")
                    log_text.insert(tk.END, "   1. ĐÓNG CHROME HOÀN TOÀN\n")
                    log_text.insert(tk.END, "   2. Nhấn 'Thử lại'\n\n")
                    log_text.insert(tk.END, "⚠️ Cookies bị lock khi Chrome đang mở!\n\n")
                elif "OperationalError" in error_msg or "database" in error_msg.lower():
                    log_text.insert(tk.END, "💡 Database bị lock! Hãy:\n")
                    log_text.insert(tk.END, "   1. Task Manager → Tắt tất cả Chrome processes\n")
                    log_text.insert(tk.END, "   2. Thử lại\n\n")
                else:
                    log_text.insert(tk.END, "💡 Thử phương pháp thủ công:\n")
                    log_text.insert(tk.END, "   1. Chrome → F12 → Application → Cookies\n")
                    log_text.insert(tk.END, "   2. Tìm labs.google\n")
                    log_text.insert(tk.END, "   3. Copy '__Secure-next-auth.session-token'\n")
                    log_text.insert(tk.END, "   4. Paste vào auto_tokens.json thủ công\n\n")
                
                log_text.see(tk.END)
                
                extract_btn.config(state="normal", text="🔄 THỬ LẠI")
                close_btn.config(state="normal")
                
                messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{error_msg}\n\n{'Đóng Chrome hoàn toàn và thử lại!' if 'Permission' in error_msg else 'Xem hướng dẫn trong popup.'}")
        
        # Run in thread
        threading.Thread(target=extract, daemon=True).start()
    
    # Auto button (Kill Chrome)
    auto_btn = tk.Button(
        btn_frame,
        text="🤖 TỰ ĐỘNG 100%",
        command=kill_chrome_and_extract,
        bg="#ff6600",
        fg="white",
        font=("Arial", 12, "bold"),
        width=20,
        height=2,
        cursor="hand2"
    )
    auto_btn.pack(side=tk.LEFT, padx=10, pady=20)
    
    # Extract button
    extract_btn = tk.Button(
        btn_frame,
        text="🚀 KHÔNG KILL",
        command=run_extraction,
        bg="#00a67e",
        fg="white",
        font=("Arial", 11, "bold"),
        width=18,
        height=2,
        cursor="hand2"
    )
    extract_btn.pack(side=tk.LEFT, padx=10, pady=20)
    
    # Manual method button
    def show_manual_method():
        """Hiển thị hướng dẫn thủ công."""
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, "=" * 60 + "\n")
        log_text.insert(tk.END, "  PHƯƠNG PHÁP THỦ CÔNG\n")
        log_text.insert(tk.END, "=" * 60 + "\n\n")
        log_text.insert(tk.END, "📌 Nếu auto không work, làm theo các bước:\n\n")
        log_text.insert(tk.END, "1️⃣ Mở Chrome → https://labs.google/fx\n\n")
        log_text.insert(tk.END, "2️⃣ Nhấn F12 → Tab 'Application'\n\n")
        log_text.insert(tk.END, "3️⃣ Bên trái: Storage → Cookies → https://labs.google\n\n")
        log_text.insert(tk.END, "4️⃣ Tìm và copy 3 cookies:\n")
        log_text.insert(tk.END, "   • __Secure-next-auth.session-token\n")
        log_text.insert(tk.END, "   • __Host-next-auth.csrf-token\n")
        log_text.insert(tk.END, "   • email\n\n")
        log_text.insert(tk.END, "5️⃣ Tạo file auto_tokens.json:\n")
        log_text.insert(tk.END, "{\n")
        log_text.insert(tk.END, '  "id": "manual",\n')
        log_text.insert(tk.END, '  "sessionToken": "paste session token vào đây",\n')
        log_text.insert(tk.END, '  "csrfToken": "paste csrf token (chỉ phần trước dấu |)",\n')
        log_text.insert(tk.END, '  "email": "your@gmail.com"\n')
        log_text.insert(tk.END, "}\n\n")
        log_text.insert(tk.END, "6️⃣ Lưu file và chạy lại app!\n\n")
        log_text.insert(tk.END, "💡 Hoặc nhấn nút bên dưới để mở folder:\n")
        log_text.see(tk.END)
        
        # Add button to open folder
        def open_folder():
            os.startfile(os.getcwd())
        
        open_folder_btn = tk.Button(
            btn_frame,
            text="📁 MỞ FOLDER",
            command=open_folder,
            bg="#0066cc",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            cursor="hand2"
        )
        if not any(isinstance(w, tk.Button) and w.cget("text") == "📁 MỞ FOLDER" for w in btn_frame.winfo_children()):
            open_folder_btn.pack(side=tk.RIGHT, padx=10, pady=20)
    
    # Quick paste method
    def quick_paste_tokens():
        """Paste tokens nhanh từ clipboard."""
        
        # Create simple input dialog
        input_popup = tk.Toplevel(popup)
        input_popup.title("📋 Paste Tokens Nhanh")
        input_popup.geometry("700x600")
        input_popup.configure(bg="#1e1e1e")
        
        # Center
        input_popup.update_idletasks()
        x = (input_popup.winfo_screenwidth() // 2) - (350)
        y = (input_popup.winfo_screenheight() // 2) - (300)
        input_popup.geometry(f"+{x}+{y}")
        
        tk.Label(
            input_popup,
            text="📋 PASTE TOKENS TỪ CHROME",
            bg="#2d2d2d",
            fg="#00a67e",
            font=("Arial", 14, "bold"),
            pady=15
        ).pack(fill=tk.X)
        
        # Instructions
        inst_frame = tk.Frame(input_popup, bg="#1e1e1e")
        inst_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        inst_text = scrolledtext.ScrolledText(
            inst_frame,
            bg="#1e1e1e",
            fg="#00ff00",
            font=("Consolas", 10),
            height=10
        )
        inst_text.pack(fill=tk.BOTH, expand=True)
        
        inst_text.insert(tk.END, "🔍 CÁCH LẤY TOKENS (Chrome đang mở):\n\n")
        inst_text.insert(tk.END, "1. F12 → Application → Cookies → https://labs.google\n")
        inst_text.insert(tk.END, "2. Click vào '__Secure-next-auth.session-token'\n")
        inst_text.insert(tk.END, "3. Copy giá trị (Ctrl+C) và paste vào ô bên dưới\n")
        inst_text.insert(tk.END, "4. Tương tự với csrf-token và email\n\n")
        inst_text.insert(tk.END, "💡 Hoặc paste JSON từ file có sẵn!\n")
        inst_text.config(state="disabled")
        
        # Input fields
        input_frame = tk.Frame(input_popup, bg="#2d2d2d")
        input_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        tk.Label(input_frame, text="Session Token:", bg="#2d2d2d", fg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5,0))
        session_entry = tk.Entry(input_frame, font=("Consolas", 9), width=80)
        session_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="CSRF Token:", bg="#2d2d2d", fg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5,0))
        csrf_entry = tk.Entry(input_frame, font=("Consolas", 9), width=80)
        csrf_entry.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Email:", bg="#2d2d2d", fg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5,0))
        email_entry = tk.Entry(input_frame, font=("Consolas", 9), width=80)
        email_entry.pack(fill=tk.X, pady=5)
        
        def save_tokens():
            session = session_entry.get().strip()
            csrf = csrf_entry.get().strip()
            email_val = email_entry.get().strip()
            
            if not session or not csrf:
                messagebox.showerror("Lỗi", "Session Token và CSRF Token là bắt buộc!")
                return
            
            # Remove |xxx from csrf if exists
            if "|" in csrf:
                csrf = csrf.split("|")[0]
            
            token_data = {
                "id": "manual_paste",
                "sessionToken": session,
                "csrfToken": csrf,
                "email": email_val or "user@gmail.com"
            }
            
            try:
                with open("auto_tokens.json", 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                log_text.delete(1.0, tk.END)
                log_text.insert(tk.END, "=" * 60 + "\n")
                log_text.insert(tk.END, "  🎉 THÀNH CÔNG!\n")
                log_text.insert(tk.END, "=" * 60 + "\n\n")
                log_text.insert(tk.END, f"✅ Session Token: {session[:40]}...\n")
                log_text.insert(tk.END, f"✅ CSRF Token: {csrf[:40]}...\n")
                log_text.insert(tk.END, f"✅ Email: {email_val}\n\n")
                log_text.insert(tk.END, "💾 Đã lưu vào: auto_tokens.json\n")
                log_text.insert(tk.END, "✨ Giờ có thể gen video!\n")
                
                status_label.config(text="✅ Token đã cập nhật", fg="#00ff00")
                
                input_popup.destroy()
                messagebox.showinfo("Thành công", "Tokens đã được lưu!\n\nGiờ bạn có thể gen video!")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file:\n{str(e)}")
        
        # Buttons
        btn_frame2 = tk.Frame(input_popup, bg="#1e1e1e")
        btn_frame2.pack(pady=20)
        
        tk.Button(
            btn_frame2,
            text="💾 LƯU TOKENS",
            command=save_tokens,
            bg="#00a67e",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame2,
            text="❌ HỦY",
            command=input_popup.destroy,
            bg="#ff4444",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)
    
    # Quick paste button (NEW - Primary method!)
    quick_btn = tk.Button(
        btn_frame,
        text="📋 PASTE NHANH",
        command=quick_paste_tokens,
        bg="#0066cc",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        height=2,
        cursor="hand2"
    )
    quick_btn.pack(side=tk.LEFT, padx=10, pady=20)
    
    manual_btn = tk.Button(
        btn_frame,
        text="📝 THỦ CÔNG",
        command=show_manual_method,
        bg="#6600cc",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        height=2,
        cursor="hand2"
    )
    manual_btn.pack(side=tk.LEFT, padx=10, pady=20)
    
    # Close button
    close_btn = tk.Button(
        btn_frame,
        text="❌ ĐÓNG",
        command=popup.destroy,
        bg="#ff4444",
        fg="white",
        font=("Arial", 12, "bold"),
        width=15,
        height=2,
        cursor="hand2"
    )
    close_btn.pack(side=tk.LEFT, padx=10, pady=20)
