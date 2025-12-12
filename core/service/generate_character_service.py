"""Character generation service for AITool"""
import json
import re
import time
import google.generativeai as genai
from core.service import config_manager
from core.constants import animation_styles


def generate_characters_from_script(script_dict: dict, animation_style: str = "3d") -> dict:
    """Generate character image prompts from script.
    
    Args:
        script_dict: Script dict from generate_script_service
        animation_style: Animation style key (default: "3d")
        
    Returns:
        dict: Character data with enhanced prompts for image generation
    """
    # Get API key from config
    gemini_api_key = config_manager.get_gemini_key()
    if not gemini_api_key:
        return {
            "error": "GEMINI_API_KEY not configured. Please set it in Settings first.",
            "characters": []
        }
    
    if "error" in script_dict:
        return {"error": "Invalid script data", "characters": []}
    
    style = animation_styles.get_style(animation_style)
    characters = script_dict.get("characters", [])
    
    # Enhance character descriptions with animation style
    enhanced_chars = []
    for char in characters:
        enhanced = {
            "name": char.get("name", ""),
            "description": char.get("description", ""),
            "image_prompt": f"{style['character_prompt']} Character: {char.get('name', '')}. Description: {char.get('description', '')}",
            "animation_style": animation_style
        }
        enhanced_chars.append(enhanced)
    
    return {
        "title": script_dict.get("title", ""),
        "characters": enhanced_chars,
        "animation_style": animation_style
    }


def generate_character_prompts_only(num_characters: int = 2, animation_style: str = "3d") -> dict:
    """Generate standalone character prompts for image generation.
    
    Args:
        num_characters: Number of characters to generate
        animation_style: Animation style key (default: "3d")
        
    Returns:
        dict: Character data with prompts
    """
    # Get API key from config
    gemini_api_key = config_manager.get_gemini_key()
    if not gemini_api_key:
        return {
            "error": "GEMINI_API_KEY not configured. Please set it in Settings first.",
            "characters": []
        }
    
    system_prompt = f"""You are a character designer for animated fairytale films.

Generate {num_characters} unique, whimsical fairytale characters suitable for animation.

IMPORTANT: Respond in VALID JSON ONLY. No markdown, no explanations.

JSON structure:
{{
  "characters": [
    {{
      "name": "string",
      "description": "string - physical appearance, personality, and distinctive features (2-3 sentences)"
    }}
  ]
}}"""

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        user_prompt = f"Create {num_characters} unique, diverse fairytale characters for an animated story."
        full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}"

        # Helper to call model with retry and exponential backoff when quota exceeded
        def _generate_with_retry(prompt_text, max_retries=3, initial_backoff=1):
            attempt = 0
            while True:
                try:
                    return model.generate_content(prompt_text)
                except Exception as e:
                    msg = str(e)
                    if 'quota' in msg.lower() or 'quota exceeded' in msg.lower() or 'generaterequestsperday' in msg.lower():
                        attempt += 1
                        if attempt > max_retries:
                            return {"error": f"Quota exceeded: {msg}"}
                        # try to parse suggested wait seconds
                        secs = None
                        m = re.search(r"Please retry in (\d+)", msg)
                        if not m:
                            m = re.search(r"seconds:\s*(\d+)", msg)
                        if m:
                            try:
                                secs = int(m.group(1))
                            except Exception:
                                secs = None
                        backoff = secs if secs else (initial_backoff * (2 ** (attempt - 1)))
                        time.sleep(backoff)
                        continue
                    # For other exceptions, re-raise
                    raise

        response = _generate_with_retry(full_prompt)
        if isinstance(response, dict) and "error" in response:
            return {"error": response["error"], "characters": []}

        json_text = response.text
        
        # Parse JSON
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]
        
        char_data = json.loads(json_text.strip())
        
        # Enhance with animation style
        style = animation_styles.get_style(animation_style)
        enhanced_chars = []
        for char in char_data.get("characters", []):
            enhanced = {
                "name": char.get("name", ""),
                "description": char.get("description", ""),
                "image_prompt": f"{style['character_prompt']} Character: {char.get('name', '')}. Description: {char.get('description', '')}",
                "animation_style": animation_style
            }
            enhanced_chars.append(enhanced)
        
        return {
            "characters": enhanced_chars,
            "animation_style": animation_style
        }
        
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON parse error: {str(e)}",
            "characters": []
        }
    except Exception as e:
        return {
            "error": f"API error: {str(e)}",
            "characters": []
        }
