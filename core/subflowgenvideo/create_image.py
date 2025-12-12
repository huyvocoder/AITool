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
    import json
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
        try:
            log.config(state="normal")
        except Exception:
            pass
        log.insert("end", f"  🖼️ Creating image: {nanoprompt[:50]}...\n")
        response = requests.post(url, headers=headers, json=body, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            media_id = data.get('media', [{}])[0].get('name', '')

            # Debug: log a compact representation of response for troubleshooting missing images
            try:
                compact = json.dumps(data if isinstance(data, dict) else {}, ensure_ascii=False)
                log.insert('end', f"  ℹ️ Response: {compact[:300]}\n")
            except Exception:
                pass
            
            # Try to extract any direct download uri if available
            def find_uri(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        # Accept any string value that looks like an HTTP(S) URL
                        if isinstance(v, str) and (v.startswith('http://') or v.startswith('https://')):
                            return v
                        rv = find_uri(v)
                        if rv:
                            return rv
                elif isinstance(o, list):
                    for item in o:
                        rv = find_uri(item)
                        if rv:
                            return rv
                return None

            image_uri = find_uri(data)
            if media_id:
                log.insert("end", f"  ✅ Image created: {media_id}\n")
                # Always return a dict with raw response so callers can inspect for inline/base64 data
                result = {"media_id": media_id, "raw_response": data}
                if image_uri:
                    log.insert("end", f"  🔗 Download URI: {image_uri}\n")
                    result["image_uri"] = image_uri
                return result
            else:
                log.insert("end", "  ⚠️ No media ID in response\n")
                # Return raw response to allow caller to detect inline/base64 images
                return {"raw_response": data}
        else:
            log.insert("end", f"  ❌ Error {response.status_code}\n")
            return None
            
    except Exception as e:
        log.insert("end", f"  ❌ Image creation error: {str(e)}\n")
    try:
        log.config(state="disabled")
    except Exception:
        pass
        return None
