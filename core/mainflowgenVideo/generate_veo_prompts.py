def generate_veo_prompts(parsed_json, log):
    """Split scenes và generate veo prompts.
    
    Args:
        parsed_json: Dict chứa scenes
        log: Widget tkinter để hiển thị log
        
    Returns:
        list: List of scenes với veo_prompt_en và nano_prompt_en
    """
    log.insert("end", "🔹 Đang generate veo prompts...\n")
    
    scenes = parsed_json.get('scenes', [])
    output_scenes = []
    
    for idx, scene in enumerate(scenes, 1):
        veo_prompt = scene.get('prompt', '')
        nanoprompt = scene.get('nanoprompt', '')
        
        output_scene = {
            'scene_number': idx,
            'nano_prompt_en': nanoprompt,
            'veo_prompt_en': veo_prompt
        }
        
        output_scenes.append(output_scene)
        log.insert("end", f"  ✓ Scene {idx}: {len(veo_prompt)} chars\n")
    
    log.insert("end", f"✅ Generated {len(output_scenes)} veo prompts\n")
    
    return output_scenes
