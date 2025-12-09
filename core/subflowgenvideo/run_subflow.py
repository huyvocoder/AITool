def run_gen_video_subflow(project_id, access_token, seed, scene, model_key, log):
    """Chạy subflow gen video: create image -> create scene -> check status.
    
    Args:
        project_id: Project ID
        access_token: Access token
        seed: Random seed
        scene: Dict chứa nano_prompt_en và veo_prompt_en
        model_key: Video model key
        log: Widget tkinter để hiển thị log
        
    Returns:
        str: Media generation ID của video hoặc None
    """
    from .create_image import create_image
    from .create_scene import create_scene
    from .check_status_scene import check_status_scene
    
    scene_num = scene.get('scene_number', 0)
    nanoprompt = scene.get('nano_prompt_en', '')
    veo_prompt = scene.get('veo_prompt_en', '')
    
    log.insert("end", f"\n🎬 Scene {scene_num}:\n")
    
    # Step 1: Create image
    media_id = create_image(project_id, access_token, seed, nanoprompt, log)
    if not media_id:
        return None
    
    # Step 2: Create video scene
    operation_name = create_scene(project_id, access_token, seed, veo_prompt, media_id, model_key, log)
    if not operation_name:
        return None
    
    # Step 3: Check status until complete
    result = check_status_scene(access_token, operation_name, log)
    
    return result.get('mediaGenerationId')
