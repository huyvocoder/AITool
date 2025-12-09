def create_project(cookie_string, log):
    """Tạo project mới trên Google Labs.
    
    Args:
        cookie_string: Cookie string từ token_setup
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Project ID
    """
    import requests
    from datetime import datetime
    from core.constants.project_constants import CREATE_PROJECT_URL, API_TIMEOUT, USER_AGENT, TOOL_NAME
    
    log.insert("end", "🔹 Đang tạo project mới...\n")
    
    # Tạo project title với timestamp
    now = datetime.now()
    project_title = now.strftime("%b %H:%M:%S").replace(" 0", " ")
    
    headers = {
        "cookie": cookie_string,
        "content-type": "application/json",
        "user-agent": USER_AGENT
    }
    
    body = {
        "json": {
            "projectTitle": project_title,
            "toolName": TOOL_NAME
        }
    }
    
    try:
        response = requests.post(CREATE_PROJECT_URL, headers=headers, json=body, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            project_id = data.get('result', {}).get('data', {}).get('json', {}).get('result', {}).get('projectId')
            
            if project_id:
                log.insert("end", f"✅ Project ID: {project_id}\n")
                log.insert("end", f"✅ Project Title: {project_title}\n")
                return project_id
            else:
                log.insert("end", "⚠️ Không tìm thấy projectId trong response\n")
                return None
        else:
            log.insert("end", f"❌ Lỗi HTTP {response.status_code}: {response.text[:200]}\n")
            return None
            
    except Exception as e:
        log.insert("end", f"❌ Lỗi khi tạo project: {str(e)}\n")
        return None
