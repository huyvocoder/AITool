def create_json_prompt_with_gemini(gemini_api_key, log, num_scenes):
    """Generate JSON prompts cho wildlife video scenes với Gemini AI.
    
    Args:
        gemini_api_key: API key cho Google Gemini
        log: Widget tkinter để hiển thị log
        num_scenes: Số lượng scenes muốn gen
        
    Returns:
        str: JSON string chứa 
    """
    import google.generativeai as genai
    
    log.insert("end", f"🔹 Đang tạo {num_scenes} prompts với Gemini AI...\n")
    
    system_prompt = f"""You are an AI Prompt Generator used in an n8n automation system.
Your ONLY task:

Convert any user request into exactly {num_scenes} high-quality AI VIDEO GENERATION SCENES about wild animals in natural environments.

Always return output in STRICT JSON format ONLY.

Your response MUST follow this exact structure:

{{
"scenes": [
{{
"scene": 1,
"nanoprompt": "",
"prompt": ""
}}....],
"output_format": "",
"fallback_model": "",
"options": {{}}
}}

Rules:

No explanations.
No markdown.
No extra text outside JSON.
No emojis.

Each nanoprompt must be a simple image generation prompt:
- Only describe one wild animal
- Simple pose
- Clear subject
- Natural environment
- Used only for image generation reference

Each prompt must:
- Describe only ONE continuous video scene
- Be a simplified video prompt based on the generated reference image
- Feature wild animals in real natural environments (forest, savanna, jungle, river, mountain, ocean, etc)
- Be cinematic, realistic, ultra-detailed
- Clearly describe camera type, camera movement, lens, and framing
- Motion must be realistic and natural (walking, hunting, flying, swimming, resting, reacting)
- Lighting, time of day, and weather must be included
- No fantasy creatures
- No sci-fi
- No cartoon

output_format must always be "AI_VIDEO".
fallback_model must always be "veo3".
options must always be an empty object {{}}.

IMPORTANT: You MUST generate exactly {num_scenes} scenes. Each scene must feature a DIFFERENT wild animal species.

If user input is unclear or too short, you must still generate full, detailed {num_scenes} wildlife video scenes based on wild animal cinematography."""
    
    try:
        genai.configure(api_key=gemini_api_key)
        # Sử dụng model mới: gemini-1.5-flash hoặc gemini-1.5-pro
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        user_prompt = f"Create {num_scenes} diverse animal AI video scenes with different species"
        
        # Gemini 1.5 không dùng system prompt riêng, combine vào user prompt
        full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}"
        
        response = model.generate_content(full_prompt)
        json_output = response.text
        
        log.insert("end", f"✅ Gemini đã tạo prompts\n")
        log.insert("end", f"📝 Output length: {len(json_output)} chars\n")
        
        return json_output
        
    except Exception as e:
        log.insert("end", f"❌ Lỗi Gemini API: {str(e)}\n")
        # Return mock data nếu lỗi
        return '''{
  "scenes": [
    {
      "scene": 1,
      "nanoprompt": "A majestic lion in savanna grassland",
      "prompt": "Cinematic shot of a lion walking through golden savanna, 4K, wildlife documentary style"
    }
  ],
  "output_format": "AI_VIDEO",
  "fallback_model": "veo3",
  "options": {}
}'''
