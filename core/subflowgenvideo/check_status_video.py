def check_status_video(access_token, operation_name, log):
    """Check status của video concatenation.
    
    Args:
        access_token: Access token
        operation_name: Operation name từ create_video
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Encoded video string hoặc None
    """
    import requests
    import time
    from core.constants.project_constants import (
        CHECK_CONCATENATION_STATUS_URL,
        API_TIMEOUT,
        POLL_INTERVAL,
        MAX_RETRIES,
        STATUS_SUCCESSFUL
    )
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "content-type": "application/json"
    }
    
    body = {
        "operation": {
            "operation": {
                "name": operation_name
            }
        }
    }
    
    log.insert("end", "⏳ Checking merge status...\n")
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(CHECK_CONCATENATION_STATUS_URL, headers=headers, json=body, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', '')
                
                if status == STATUS_SUCCESSFUL:
                    encoded_video = data.get('encodedVideo', '')
                    log.insert("end", f"✅ Video merged successfully!\n")
                    log.insert("end", f"📦 Video size: {len(encoded_video)} bytes\n")
                    return encoded_video
                else:
                    if attempt % 6 == 0:
                        log.insert("end", f"⏳ Merging... ({attempt * POLL_INTERVAL}s)\n")
                    time.sleep(POLL_INTERVAL)
            else:
                log.insert("end", f"⚠️ Check error {response.status_code}\n")
                time.sleep(POLL_INTERVAL)
                
        except Exception as e:
            log.insert("end", f"⚠️ Status check error: {str(e)}\n")
            time.sleep(POLL_INTERVAL)
    
    log.insert("end", f"❌ Timeout after {MAX_RETRIES * POLL_INTERVAL}s\n")
    return None
