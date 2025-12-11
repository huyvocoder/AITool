from core.mainflowgenVideo.get_config_sheet import get_token_from_sheet
from core.mainflowgenVideo.email_parse import email_parse
from core.mainflowgenVideo.get_access_token import get_access_token
from core.mainflowgenVideo.token_setup import build_token_setup
from core.mainflowgenVideo.create_project import create_project
from core.mainflowgenVideo.create_json_prompt import create_json_prompt_with_gemini
from core.mainflowgenVideo.preprocessing_json import preprocess_json_output
from core.mainflowgenVideo.generate_veo_prompts import generate_veo_prompts
from core.subflowgenvideo.run_subflow import run_gen_video_subflow
from core.subflowgenvideo.merge_video_json import merge_video_json
from core.subflowgenvideo.create_video import create_video
from core.subflowgenvideo.check_status_video import check_status_video
from core.subflowgenvideo.download_video import download_video
from core.constants.project_constants import GEMENI_KEY, SCENES_PER_BATCH
import random
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_full_flow(model_key, log, num_scenes=4):
    """Main flow để generate video với Google Labs Veo3.
    
    Args:
        model_key: Video model key (veo_3_1_i2v_s_fast_ultra_relaxed, etc)
        log: Widget tkinter để hiển thị log
        num_scenes: Số lượng scenes muốn gen (sẽ gen theo batch)
        
    Returns:
        dict: {"encoded_video": base64_string, "seed": int, "project_id": str}
    """
    
    # Generate random seed nếu không có
    seed = random.randint(1, 1000000000)
    log.insert("end", f"🎲 Seed: {seed}\n\n")
    
    # Step 1: Get config from Google Sheet
    log.insert("end", "=" * 60 + "\n")
    log.insert("end", "STEP 1: GET CONFIG\n")
    log.insert("end", "=" * 60 + "\n")
    token_data = get_token_from_sheet(log)
    
    # Step 2: Parse email
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "STEP 2: PARSE EMAIL\n")
    log.insert("end", "=" * 60 + "\n")
    raw_email = token_data['email']
    email_parse_data = email_parse(raw_email)
    log.insert("end", f"✅ Email: {email_parse_data['emailDefault']}\n")
    
     # Step 4: Get access token
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "STEP 4: GET ACCESS TOKEN\n")
    log.insert("end", "=" * 60 + "\n")
    access_token = get_access_token(token_data, email_parse_data, log)
    if not access_token:
        return "ERROR: Không có access token"
    
    # Step 5: Create project
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "STEP 5: CREATE PROJECT\n")
    log.insert("end", "=" * 60 + "\n")
    project_id = create_project(cookie_string, log)
    if not project_id:
        return "ERROR: Không tạo được project"
    
    # Step 6: Generate prompts with Gemini (Optional - cần API key)
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "STEP 6: GENERATE PROMPTS\n")
    log.insert("end", "=" * 60 + "\n")
    
    gemini_api_key = GEMENI_KEY
    if gemini_api_key:
        json_output = create_json_prompt_with_gemini(gemini_api_key, log, num_scenes)
        parsed_json = preprocess_json_output(json_output, log)
    else:
        log.insert("end", "⚠️ No GEMINI_API_KEY - using default prompt\n")
        parsed_json = {
            "scenes": [{
                "scene": 1,
                "nanoprompt": "A majestic lion standing in golden savanna grassland at sunset",
                "prompt": "Cinematic wildlife documentary shot of a male lion with full mane standing proudly in African savanna, golden hour lighting, 4K ultra detailed, slow camera dolly forward, wide angle lens, dramatic sky"
            }]
        }
    
    if not parsed_json:
        return "ERROR: Không parse được JSON"
    
    # Step 7: Generate veo prompts
    scenes = generate_veo_prompts(parsed_json, log)
    
    # Giới hạn số scenes theo input
    scenes = scenes[:num_scenes]
    
    # Step 8: Loop through scenes và generate videos theo batch
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", f"STEP 7: GENERATE {len(scenes)} VIDEOS (batch size: {SCENES_PER_BATCH})\n")
    log.insert("end", "=" * 60 + "\n")
    
    # Collect generated media as list of objects: {"scene_num": int, "media_id": str}
    media_generation_results = []
    total_scenes = len(scenes)
    
    # Chia scenes thành các batch
    for batch_start in range(0, total_scenes, SCENES_PER_BATCH):
        batch_end = min(batch_start + SCENES_PER_BATCH, total_scenes)
        batch_scenes = scenes[batch_start:batch_end]
        batch_num = (batch_start // SCENES_PER_BATCH) + 1
        
        log.insert("end", f"\n🔄 BATCH {batch_num}: Gen {len(batch_scenes)} scenes SONG SONG (#{batch_start+1} -> #{batch_end})...\n")
        
        # Gen SONG SONG tất cả scenes trong batch này
        # For this batch, collect objects with scene number + media id
        batch_media_items = []
        
        def process_scene(idx, scene):
            """Helper function để process 1 scene."""
            scene_num = batch_start + idx + 1
            nanoprompt = scene.get('nano_prompt_en', '')
            log.insert("end", f"\n  🎬 Scene {scene_num}/{total_scenes}: {nanoprompt[:60]}...\n")
            
            media_id = run_gen_video_subflow(project_id, access_token, seed, scene, model_key, log)
            return (scene_num, media_id)
        
        # Chạy song song với ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=SCENES_PER_BATCH) as executor:
            # Submit tất cả scenes trong batch
            future_to_scene = {
                executor.submit(process_scene, idx, scene): (batch_start + idx + 1)
                for idx, scene in enumerate(batch_scenes)
            }
            
            # Thu thập kết quả khi hoàn thành
            for future in as_completed(future_to_scene):
                scene_num = future_to_scene[future]
                try:
                    result_scene_num, media_id = future.result()
                    if media_id:
                        batch_media_items.append({"scene_num": result_scene_num, "media_id": media_id})
                        log.insert("end", f"  ✅ Scene {result_scene_num} hoàn thành!\n")
                    else:
                        log.insert("end", f"  ⚠️ Scene {result_scene_num} thất bại - Skip!\n")
                except Exception as e:
                    log.insert("end", f"  ❌ Scene {scene_num} lỗi: {str(e)}\n")
        
        # Chỉ chuyển batch tiếp theo nếu có ít nhất 1 scene thành công
        if batch_media_items:
            media_generation_results.extend(batch_media_items)
            log.insert("end", f"\n✅ BATCH {batch_num} hoàn tất: {len(batch_media_items)}/{len(batch_scenes)} scenes\n")
        else:
            log.insert("end", f"\n❌ BATCH {batch_num} thất bại hoàn toàn - Tiếp tục batch tiếp theo...\n")
    
    if not media_generation_results:
        return "ERROR: Không tạo được video nào"

    log.insert("end", f"\n🎉 TỔNG KẾT: Tạo thành công {len(media_generation_results)}/{total_scenes} videos\n")
    
    # Step 9: Merge videos
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "STEP 8: MERGE VIDEOS\n")
    log.insert("end", "=" * 60 + "\n")
    
    # merge_video_json expects a list of media ids; sort results by scene_num
    sorted_results = sorted(media_generation_results, key=lambda x: x.get('scene_num', 0))
    media_ids_for_merge = [item['media_id'] for item in sorted_results]
    merge_json = merge_video_json(media_ids_for_merge)
    operation_name = create_video(token_setup_data['cookie'], merge_json, log)
    
    if not operation_name:
        return "ERROR: Không merge được videos"
    
    # Step 10: Check merge status
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "STEP 9: WAIT FOR MERGE\n")
    log.insert("end", "=" * 60 + "\n")
    
    encoded_video = check_status_video(access_token, operation_name, log)
    
    if not encoded_video:
        return "ERROR: Không lấy được video sau merge"
    
    # Hoàn tất - trả về encoded_video thay vì download ngay
    log.insert("end", "\n" + "=" * 60 + "\n")
    log.insert("end", "🎉 HOÀN TẤT!\n")
    log.insert("end", "=" * 60 + "\n")
    log.insert("end", "💡 Video đã sẵn sàng - chọn Download để lưu file\n")
    
    # Return encoded video để xử lý sau
    return {"encoded_video": encoded_video, "seed": seed, "project_id": project_id}
