"""Animation styles for AITool"""

# Animation style templates
ANIMATION_STYLES = {
    "3d": {
        "name": "Hoạt hình 3D",
        "character_prompt": "3D animated character, pixar style, professional 3D render, high quality, clean character design, white background, front view, no text.",
        "scene_image_prompt": "3D animation style, pixar quality, high quality render",
        "scene_video_prompt": "with 3D animation style, pixar quality, smooth lighting, cinematic"
    }
}

# Get style by key
def get_style(style_key: str) -> dict:
    """Get animation style by key"""
    return ANIMATION_STYLES.get(style_key, ANIMATION_STYLES["3d"])

# Get all available styles
def get_available_styles() -> list:
    """Get list of available animation styles"""
    return list(ANIMATION_STYLES.keys())

# Get style display names
def get_style_names() -> dict:
    """Get display names for all styles"""
    return {k: v["name"] for k, v in ANIMATION_STYLES.items()}
