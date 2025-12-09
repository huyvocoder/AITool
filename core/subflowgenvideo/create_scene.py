def create_scene(project_id, access_token, seed, veo_prompt, media_id, model_key, log):
    """Tạo video scene từ image và prompt.
    
    Args:
        project_id: Project ID
        access_token: Access token
        seed: Random seed
        veo_prompt: Veo prompt cho video
        media_id: Media ID của image reference
        model_key: Video model key (veo3, etc)
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Operation name để check status
    """
    import requests
    from core.constants.project_constants import (
        BATCH_ASYNC_GENERATE_VIDEO_URL,
        API_TIMEOUT,
        VIDEO_ASPECT_RATIO,
        TOOL_NAME,
        USER_PAYGATE_TIER
    )
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "content-type": "application/json"
    }
    
    body = {
        "clientContext": {
            "projectId": project_id,
            "tool": TOOL_NAME,
            "userPaygateTier": USER_PAYGATE_TIER
        },
        "requests": [{
            "aspectRatio": VIDEO_ASPECT_RATIO,
            "seed": seed,
            "textInput": {
                "prompt": veo_prompt
            },
            "videoModelKey": model_key,
            "startImage": {
                "mediaId": media_id
            }
        }]
    }
    
    try:
        log.insert("end", f"  🎬 Creating scene: {veo_prompt[:50]}...\n")
        response = requests.post(BATCH_ASYNC_GENERATE_VIDEO_URL, headers=headers, json=body, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            operation_name = data.get('operations', [{}])[0].get('operation', {}).get('name', '')
            
            if operation_name:
                log.insert("end", f"  ✅ Scene started: {operation_name}\n")
                return operation_name
            else:
                log.insert("end", "  ⚠️ No operation name\n")
                return None
        else:
            log.insert("end", f"  ❌ Error {response.status_code}\n")
            return None
            
    except Exception as e:
        log.insert("end", f"  ❌ Scene creation error: {str(e)}\n")
        return None
