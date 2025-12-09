def create_video(cookie_string, merge_json, log):
    """Concatenate tất cả scenes thành 1 video.
    
    Args:
        cookie_string: Cookie string từ token_setup
        merge_json: JSON body từ merge_video_json
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Operation name để check status
    """
    import requests
    from core.constants.project_constants import CONCATENATE_VIDEOS_URL, API_TIMEOUT, USER_AGENT
    
    log.insert("end", "\n🎥 Đang merge videos...\n")
    
    headers = {
        "Cookie": cookie_string,
        "content-type": "application/json",
        "user-agent": USER_AGENT
    }
    
    body = {"json": merge_json}
    
    try:
        response = requests.post(CONCATENATE_VIDEOS_URL, headers=headers, json=body, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            operation_name = data.get('result', {}).get('data', {}).get('json', {}).get('result', {}).get('operation', {}).get('operation', {}).get('name', '')
            
            if operation_name:
                log.insert("end", f"✅ Merge started: {operation_name}\n")
                return operation_name
            else:
                log.insert("end", "⚠️ No operation name in response\n")
                return None
        else:
            log.insert("end", f"❌ Error {response.status_code}: {response.text[:200]}\n")
            return None
            
    except Exception as e:
        log.insert("end", f"❌ Merge error: {str(e)}\n")
        return None
