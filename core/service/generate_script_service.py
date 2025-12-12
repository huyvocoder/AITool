"""Script generation service for AITool"""
import json
import re
import time
import google.generativeai as genai
from core.constants import project_constants
from core.service import config_manager


def generate_fairy_tale_script(num_scenes: int = None, num_characters: int = None) -> dict:
    """Generate a fairy tale script with characters and scenes using Gemini AI.
    
    Args:
        num_scenes: Number of scenes (default: 10)
        num_characters: Number of characters (default: 2)
        
    Returns:
        dict: Script structure with title, summary, characters, and scenes
    """
    # Get API key from config
    gemini_api_key = config_manager.get_gemini_key()
    if not gemini_api_key:
        return {
            "error": "GEMINI_API_KEY not configured. Please set it in Settings first.",
            "title": "Error",
            "summary": "Cannot generate script without API key",
            "characters": [],
            "scenes": []
        }
    if num_scenes is None:
        num_scenes = project_constants.DEFAULT_NUM_SCENES
    if num_characters is None:
        num_characters = project_constants.DEFAULT_NUM_CHARACTERS
    
    system_prompt = f"""You are a creative fairy tale script generator for animated films.

Your task is to generate a complete fairy tale script with:
1. A creative title
2. A plot summary
3. {num_characters} diverse characters with descriptions
4. {num_scenes} scenes with visual prompts

IMPORTANT: You MUST respond in VALID JSON ONLY. No markdown, no explanations, no extra text.

The JSON structure MUST be exactly:
{{
  "title": "string - creative fairy tale title",
  "summary": "string - 2-3 sentence plot summary",
  "characters": [
    {{
      "name": "string",
      "description": "string - physical appearance and personality (2-3 sentences)"
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "scene_title": "string - brief scene title",
      "description": "string - what happens in this scene",
      "nanoprompt": "string - visual prompt for the key frame image (describe the 2 characters, their poses, the setting, camera framing, and mood)",
      "prompt": "string - detailed video generation prompt (describe character actions, movement, dialogue if any, camera movement, lighting, emotions, and cinematic details)"
    }}
  ]
}}

Rules:
- All characters must be fairytale-appropriate (animals, magical creatures, or fantasy beings)
- Each scene must feature the {num_characters} characters
- nanoprompt should be concise (1-2 sentences) for image generation
- prompt should be detailed (3-5 sentences) for video generation
- Scenes should flow logically and tell a cohesive story
- Include magic, adventure, and heartwarming moments
- Output MUST be valid JSON that can be parsed"""

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        user_prompt = f"""Create a fairy tale script with:
- {num_characters} unique characters
- {num_scenes} scenes
- A complete story arc with beginning, middle, and end

The story should be whimsical, magical, and suitable for animation."""
        
        full_prompt = f"{system_prompt}\n\nUser request: {user_prompt}"

        # Helper to call model with retry and exponential backoff when quota exceeded
        def _generate_with_retry(prompt_text, max_retries=3, initial_backoff=1):
            attempt = 0
            while True:
                try:
                    return model.generate_content(prompt_text)
                except Exception as e:
                    msg = str(e)
                    # Detect quota errors heuristically
                    if 'quota' in msg.lower() or 'quota exceeded' in msg.lower() or 'GenerateRequestsPerDay' in msg:
                        attempt += 1
                        if attempt > max_retries:
                            # Surface the raw message to caller for UI display
                            return {"error": f"Quota exceeded: {msg}"}
                        # Try to extract suggested wait seconds
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
                    # Other errors: raise for UI to surface
                    raise

        response = _generate_with_retry(full_prompt)
        if isinstance(response, dict) and "error" in response:
            # This is our custom quota error dict
            return {"error": response["error"], "raw_response": "Quota error"}

        json_text = response.text
        
        # Try to parse JSON
        # Sometimes Gemini wraps JSON in markdown code blocks
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]
        
        script_data = json.loads(json_text.strip())
        return script_data
        
    except json.JSONDecodeError as e:
        # Return error with fallback data
        return {
            "error": f"JSON parse error: {str(e)}",
            "raw_response": json_text,
            "title": "Error in Script Generation",
            "summary": "Failed to generate script",
            "characters": [],
            "scenes": []
        }
    except Exception as e:
        return {
            "error": f"API error: {str(e)}",
            "title": "Error in Script Generation",
            "summary": "Failed to generate script",
            "characters": [],
            "scenes": []
        }


def format_script_for_display(script: dict) -> str:
    """Format script data into readable text.
    
    Args:
        script: Script dict from generate_fairy_tale_script
        
    Returns:
        str: Formatted script text
    """
    output = []
    
    if "error" in script:
        output.append(f"❌ Error: {script['error']}")
        return "\n".join(output)
    
    output.append(f"{'='*60}")
    output.append(f"📽️ {script.get('title', 'Untitled')}")
    output.append(f"{'='*60}\n")
    
    output.append(f"📖 Summary:\n{script.get('summary', 'N/A')}\n")
    
    output.append(f"{'='*60}")
    output.append("👥 Characters:")
    output.append(f"{'='*60}")
    for char in script.get('characters', []):
        output.append(f"\n• {char.get('name', 'Unknown')}")
        output.append(f"  {char.get('description', 'N/A')}")
    
    output.append(f"\n\n{'='*60}")
    output.append("🎬 Scenes:")
    output.append(f"{'='*60}")
    
    for scene in script.get('scenes', []):
        output.append(f"\n📍 Scene {scene.get('scene_number', '?')}: {scene.get('scene_title', 'Untitled')}")
        output.append(f"\n   Description: {scene.get('description', 'N/A')}")
        output.append(f"\n   🖼️  Key Frame Prompt (nanoprompt):\n   {scene.get('nanoprompt', 'N/A')}")
        output.append(f"\n   🎥 Video Generation Prompt:\n   {scene.get('prompt', 'N/A')}")
        output.append(f"\n   {'-'*56}")
    
    return "\n".join(output)
