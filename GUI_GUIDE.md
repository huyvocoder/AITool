# 🎯 Hướng Dẫn Sử Dụng Nút "LẤY TOKEN"

## 📱 Giao Diện Mới

App giờ có nút **🔑 LẤY TOKEN** để tự động lấy session token từ Chrome!

### Vị trí
```
[🤖 Model] [🎬 Scenes] [🔑 LẤY TOKEN] [🎬 GEN VIDEO] [✅ Token OK]
```

---

## 🚀 Cách Sử Dụng

### Lần Đầu Tiên:

1. **Mở Chrome** → Truy cập https://labs.google/fx
2. **Đăng nhập** với tài khoản Google Labs
3. **Giữ tab Chrome mở**
4. **Quay lại app** → Nhấn nút **🔑 LẤY TOKEN**
5. Popup sẽ mở và tự động lấy token
6. Xong! Status sẽ hiển thị **✅ Token OK**

### Hàng Ngày (Khi Token Hết Hạn):

Token thường hết hạn sau ~24 giờ. Khi app báo lỗi 401:

1. Nhấn **🔑 LẤY TOKEN**
2. Đợi 2-3 giây
3. Done! Tiếp tục gen video

**Không cần:**
- ❌ Mở DevTools
- ❌ Copy-paste cookie
- ❌ Update Google Sheet
- ❌ Tắt/mở Chrome

---

## 🎨 Popup "Lấy Token"

### Giao Diện:
```
╔══════════════════════════════════════════╗
║   🔑 TỰ ĐỘNG LẤY TOKEN TỪ CHROME        ║
╠══════════════════════════════════════════╣
║                                          ║
║  📌 Yêu cầu:                            ║
║     1. Đã cài Google Chrome             ║
║     2. Đã đăng nhập labs.google/fx      ║
║     3. Giữ tab Chrome mở                ║
║                                          ║
║  [Quá trình extraction hiển thị ở đây] ║
║                                          ║
║  ✅ Session Token: eyJhbG...            ║
║  ✅ CSRF Token: 5a2b1c3d...             ║
║  ✅ Email: your@gmail.com               ║
║                                          ║
║  🎉 THÀNH CÔNG!                         ║
║  💾 Đã lưu vào: auto_tokens.json        ║
║                                          ║
╠══════════════════════════════════════════╣
║  [🚀 BẮT ĐẦU LẤY TOKEN]  [❌ ĐÓNG]     ║
╚══════════════════════════════════════════╝
```

### Các Trạng Thái:

#### ✅ Thành Công:
```
🎉 THÀNH CÔNG!
💾 Đã lưu vào: auto_tokens.json
✨ App sẽ tự động dùng token này!
📌 Token có thể dùng được ~24 giờ
```

#### ❌ Chưa Đăng Nhập:
```
❌ Không tìm thấy cookies!
💡 Hãy:
   1. Mở Chrome
   2. Truy cập https://labs.google/fx
   3. Đăng nhập
   4. Giữ tab mở và thử lại
```

#### ⚠️ Chrome Đang Chạy:
```
❌ Lỗi: [Errno 13] Permission denied
💡 Nếu Chrome đang mở:
   1. Đóng Chrome hoàn toàn
   2. Thử lại
```

---

## 💡 Tips

### Lấy Token Thành Công 100%:

**Cách 1: Đóng Chrome** (Đề xuất)
1. Đóng Chrome hoàn toàn
2. Mở Chrome → Đăng nhập labs.google/fx
3. Đóng Chrome lại
4. Nhấn nút LẤY TOKEN

**Cách 2: Giữ Chrome Mở** (Có thể bị lỗi trên một số máy)
1. Giữ Chrome mở với tab labs.google/fx
2. Nhấn nút LẤY TOKEN
3. Nếu lỗi → Đóng Chrome và thử lại

### Token Hết Hạn Khi Nào?

Thường sau **~24 giờ**. Bạn sẽ biết khi:
- App báo lỗi 401 Unauthorized
- Không tạo được project
- Không generate được video

→ Chỉ cần nhấn **🔑 LẤY TOKEN** lại!

### Nhiều Tài Khoản?

1. Lấy token account 1 → Rename `auto_tokens.json` → `auto_tokens_acc1.json`
2. Đăng nhập Chrome với account 2 → Lấy token lại
3. Muốn dùng account 1 → Copy `auto_tokens_acc1.json` về `auto_tokens.json`

---

## 🔧 Troubleshooting

### "Chưa cài browser-cookie3"

App sẽ **tự động cài đặt**. Nếu không được:

```bash
pip install browser-cookie3
```

### "Permission denied"

→ **Đóng Chrome hoàn toàn** rồi thử lại

### "Không tìm thấy cookies"

→ **Đăng nhập vào Chrome** với labs.google/fx trước

### Vẫn không work?

Dùng cách cũ:
1. F12 → Application → Cookies → labs.google
2. Copy `__Secure-next-auth.session-token`
3. Paste vào file `auto_tokens.json` thủ công

---

## ✨ So Sánh Cũ vs Mới

| Tính năng | Cách cũ | Cách mới |
|-----------|---------|----------|
| Lấy token | F12 > Copy cookie | Nhấn 1 nút |
| Update | Google Sheet | Không cần |
| Thời gian | ~2 phút | 5 giây |
| Độ phức tạp | Cao | Thấp |
| User-friendly | ❌ | ✅ |

---

**Enjoy! 🚀**
