def check_status_scene(access_token, operation_name, log):
    """Check status của video scene generation.
    
    Args:
        access_token: Access token
        operation_name: Operation name từ create_scene
        log: Widget tkinter để hiển thị log
        
    Returns:
        dict: {'status': status_code, 'mediaGenerationId': media_id}
    """
    import requests
    import time
    from core.constants.project_constants import (
        CHECK_VIDEO_STATUS_URL,
        API_TIMEOUT,
        POLL_INTERVAL,
        MAX_RETRIES,
        STATUS_SUCCESSFUL,
        STATUS_FAILED,
        STATUS_ACTIVE
    )
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "content-type": "application/json"
    }
    
    body = {
        "operations": [{
            "operation": {
                "name": operation_name
            },
            "sceneId": "1",
            "status": STATUS_ACTIVE
        }]
    }
    
    log.insert("end", f"  ⏳ Checking status...\n")
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(CHECK_VIDEO_STATUS_URL, headers=headers, json=body, timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                operations = data.get('operations', [])
                
                if operations:
                    status = operations[0].get('status', '')
                    media_id = operations[0].get('mediaGenerationId', '')
                    
                    if status == STATUS_SUCCESSFUL:
                        log.insert("end", f"  ✅ Scene completed: {media_id}\n")
                        return {'status': status, 'mediaGenerationId': media_id}
                    elif status == STATUS_FAILED:
                        log.insert("end", f"  ❌ Scene failed\n")
                        return {'status': status, 'mediaGenerationId': None}
                    else:
                        # Still processing
                        if attempt % 6 == 0:  # Log every minute
                            log.insert("end", f"  ⏳ Still processing... ({attempt * POLL_INTERVAL}s)\n")
                        time.sleep(POLL_INTERVAL)
            else:
                log.insert("end", f"  ⚠️ Check status error {response.status_code}\n")
                time.sleep(POLL_INTERVAL)
                
        except Exception as e:
            log.insert("end", f"  ⚠️ Status check error: {str(e)}\n")
            time.sleep(POLL_INTERVAL)
    
    log.insert("end", f"  ❌ Timeout after {MAX_RETRIES * POLL_INTERVAL}s\n")
    return {'status': 'TIMEOUT', 'mediaGenerationId': None}
