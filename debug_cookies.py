"""
Script debug để kiểm tra Chrome cookies.
Chạy script này để xem cookies có tồn tại không và ở đâu.
"""

import sys
import os


def debug_chrome_cookies():
    """Debug Chrome cookies location and content."""
    
    print("\n" + "="*70)
    print("  CHROME COOKIES DEBUGGER")
    print("="*70)
    
    # 1. Check Chrome installation
    print("\n1️⃣  Kiểm tra Chrome installation...")
    
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    chrome_base = os.path.join(local_app_data, "Google", "Chrome", "User Data")
    
    if os.path.exists(chrome_base):
        print(f"✅ Chrome installed at: {chrome_base}")
    else:
        print(f"❌ Chrome không tìm thấy tại: {chrome_base}")
        return
    
    # 2. List all profiles
    print("\n2️⃣  Tìm profiles...")
    profiles = []
    
    for item in os.listdir(chrome_base):
        profile_path = os.path.join(chrome_base, item)
        if os.path.isdir(profile_path):
            # Check if has Cookies or Network/Cookies
            cookies_old = os.path.join(profile_path, "Cookies")
            cookies_new = os.path.join(profile_path, "Network", "Cookies")
            
            if os.path.exists(cookies_old) or os.path.exists(cookies_new):
                profiles.append(item)
                print(f"   ✅ {item}")
                if os.path.exists(cookies_old):
                    print(f"      → Cookies: {cookies_old}")
                if os.path.exists(cookies_new):
                    print(f"      → Network/Cookies: {cookies_new}")
    
    if not profiles:
        print("   ❌ Không tìm thấy profile nào có cookies!")
        return
    
    # 3. Try to read cookies with browser_cookie3
    print("\n3️⃣  Thử đọc cookies với browser_cookie3...")
    
    try:
        import browser_cookie3
        print("   ✅ browser_cookie3 đã cài")
        
        # Try to load cookies
        print("\n   Đang load cookies từ Chrome...")
        
        try:
            cookies = browser_cookie3.chrome(domain_name='google')
            cookie_list = list(cookies)
            print(f"   ✅ Tìm thấy {len(cookie_list)} cookies từ google.com")
            
            # Try labs.google specifically
            labs_cookies = browser_cookie3.chrome(domain_name='labs.google')
            labs_list = list(labs_cookies)
            print(f"   ✅ Tìm thấy {len(labs_list)} cookies từ labs.google")
            
            if labs_list:
                print("\n   📋 Labs cookies:")
                for cookie in labs_list:
                    print(f"      • {cookie.name}: {cookie.value[:30]}...")
                    
                # Check for required cookies
                session_token = None
                csrf_token = None
                
                for cookie in labs_list:
                    if cookie.name == "__Secure-next-auth.session-token":
                        session_token = cookie.value
                    elif cookie.name == "__Host-next-auth.csrf-token":
                        csrf_token = cookie.value
                
                print("\n   🔍 Kiểm tra cookies cần thiết:")
                if session_token:
                    print(f"   ✅ Session Token: {session_token[:40]}...")
                else:
                    print("   ❌ KHÔNG có Session Token!")
                    
                if csrf_token:
                    print(f"   ✅ CSRF Token: {csrf_token[:40]}...")
                else:
                    print("   ❌ KHÔNG có CSRF Token!")
                
                if not session_token or not csrf_token:
                    print("\n   ⚠️  CHƯA ĐĂNG NHẬP vào labs.google/fx!")
                    print("   💡 Hãy:")
                    print("      1. Mở Chrome")
                    print("      2. Truy cập https://labs.google/fx")
                    print("      3. Đăng nhập")
                    print("      4. Đóng Chrome")
                    print("      5. Chạy lại script này")
            else:
                print("\n   ❌ KHÔNG có cookies từ labs.google!")
                print("   💡 Bạn chưa đăng nhập vào labs.google/fx")
                
        except PermissionError as e:
            print(f"\n   ❌ PermissionError: {e}")
            print("   💡 Chrome đang chạy! Hãy ĐÓNG CHROME và thử lại!")
            
        except Exception as e:
            print(f"\n   ❌ Lỗi: {e}")
            print(f"   Type: {type(e).__name__}")
            
    except ImportError:
        print("   ❌ browser_cookie3 chưa cài!")
        print("   💡 Cài đặt: pip install browser-cookie3")
    
    # 4. Alternative: Manual check
    print("\n4️⃣  Kiểm tra thủ công...")
    print("   💡 Nếu auto không work, làm theo:")
    print("      1. Chrome → F12 → Application → Cookies")
    print("      2. Tìm https://labs.google")
    print("      3. Tìm cookie '__Secure-next-auth.session-token'")
    print("      4. Nếu KHÔNG CÓ → Bạn chưa đăng nhập!")
    print("      5. Nếu CÓ → Copy và paste thủ công vào auto_tokens.json")
    
    print("\n" + "="*70)
    print("  KẾT THÚC DEBUG")
    print("="*70)


if __name__ == "__main__":
    debug_chrome_cookies()
    
    print("\n⏸  Nhấn Enter để thoát...")
    input()
