def preprocess_json_output(json_string, log):
    """Parse JSON string từ Gemini output.
    
    Args:
        json_string: JSON string từ Gemini
        log: Widget tkinter để hiển thị log
        
    Returns:
        dict: Parsed JSON data
    """
    import json
    import re
    
    log.insert("end", "🔹 Đang parse JSON output...\n")
    
    try:
        # Remove markdown code blocks nếu có
        cleaned = json_string.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Parse JSON
        parsed_json = json.loads(cleaned)
        
        # Validate structure
        if 'scenes' not in parsed_json:
            raise ValueError("Missing 'scenes' key in JSON")
        
        scene_count = len(parsed_json['scenes'])
        log.insert("end", f"✅ Parsed {scene_count} scenes\n")
        
        return parsed_json
        
    except json.JSONDecodeError as e:
        log.insert("end", f"❌ JSON parse error: {str(e)}\n")
        return None
    except Exception as e:
        log.insert("end", f"❌ Lỗi preprocessing: {str(e)}\n")
        return None
