def get_token_from_sheet(log):
    """Lấy token từ Google Sheet.
    
    Args:
        log: Widget tkinter để hiển thị log
    """
    import requests
    import os
    from core.constants.project_constants import SPREADSHEET_ID, SHEET_RANGE, API_TIMEOUT
    
    log.insert("end", f"🔹 Đọc Google Sheet ID: {SPREADSHEET_ID}...\n")
    
    # Thử phương pháp 1: Đọc trực tiếp từ Google Sheets (nếu sheet public)
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json&sheet=Trang tính1"
        response = requests.get(url, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            # Parse JSON từ response (Google trả về dạng google.visualization.Query.setResponse(...))
            json_str = response.text.split('(', 1)[1].rsplit(')', 1)[0]
            import json
            data = json.loads(json_str)
            
            rows = data.get('table', {}).get('rows', [])
            if rows and len(rows) > 0:
                cells = rows[0].get('c', [])
                if len(cells) >= 4:
                    log.insert("end", f"✅ Đọc thành công từ Google Sheet (public)\n")
                    return {
                        "id": cells[0].get('v', ''),
                        "sessionToken": cells[1].get('v', ''),
                        "csrfToken": cells[2].get('v', ''),
                        "email": cells[3].get('v', '')
                    }
        log.insert("end", "⚠️ Sheet không public hoặc không truy cập được\n")
    except Exception as e:
        log.insert("end", f"⚠️ Lỗi đọc Sheet public: {str(e)}\n")
    
   
    except Exception as e:
        log.insert("end", f"⚠️ Lỗi Service Account: {str(e)} - dùng mock data\n")
        return {
            "id": "mock_id",
            "sessionToken": "mock_session_token_12345",
            "csrfToken": "mock_csrf_token_67890",
            "email": "test@example.com"
        }