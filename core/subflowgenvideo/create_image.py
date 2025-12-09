def create_image(project_id, access_token, seed, nanoprompt, log):
    """Tạo image từ nanoprompt.
    
    Args:
        project_id: Project ID từ create_project
        access_token: Access token
        seed: Random seed
        nanoprompt: Nano prompt để gen image
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Media ID của image đã tạo
    """
    import requests
    from core.constants.project_constants import (
        GOOGLE_SANDBOX_API_URL,
        API_TIMEOUT,
        IMAGE_ASPECT_RATIO,
        MODEL_IMAGE_KEYS
    )
    
    url = f"{GOOGLE_SANDBOX_API_URL}/projects/{project_id}/flowMedia:batchGenerateImages"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "content-type": "application/json"
    }
    
    body = {
        "requests": [{
            "clientContext": {},
            "seed": seed,
            "imageModelName": MODEL_IMAGE_KEYS['nano_banana_pro'],
            "imageAspectRatio": IMAGE_ASPECT_RATIO,
            "prompt": nanoprompt,
            "imageInputs": []
        }]
    }
    
    try:
        log.insert("end", f"  🖼️ Creating image: {nanoprompt[:50]}...\n")
        response = requests.post(url, headers=headers, json=body, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            media_id = data.get('media', [{}])[0].get('name', '')
            
            if media_id:
                log.insert("end", f"  ✅ Image created: {media_id}\n")
                return media_id
            else:
                log.insert("end", "  ⚠️ No media ID in response\n")
                return None
        else:
            log.insert("end", f"  ❌ Error {response.status_code}\n")
            return None
            
    except Exception as e:
        log.insert("end", f"  ❌ Image creation error: {str(e)}\n")
        return None
