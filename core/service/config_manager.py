"""Config file I/O logic for AITool"""
from pathlib import Path
import json


def get_config_path() -> Path:
    """Get path to config.json file"""
    return Path(__file__).resolve().parent.parent / 'config.json'


def read_config() -> dict:
    """Read config.json and return as dict"""
    cfg = get_config_path()
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding='utf-8'))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def get_gemini_key() -> str:
    """Get GEMINI_API_KEY from config"""
    config = read_config()
    return config.get('GEMINI_API_KEY', '') or ''


def save_config(config_dict: dict) -> tuple[bool, str]:
    """Save config dict to config.json.
    
    Returns: (success: bool, message: str)
    """
    cfg = get_config_path()

    try:
        cfg.write_text(json.dumps(config_dict, indent=2), encoding='utf-8')
        return True, f"Đã lưu tại {cfg}"
    except Exception as e:
        return False, f"Không thể ghi file cấu hình: {e}"


def update_gemini_key(new_key: str) -> tuple[bool, str]:
    """Update GEMINI_API_KEY in config.
    
    Returns: (success: bool, message: str)
    """
    config = read_config()
    config['GEMINI_API_KEY'] = new_key
    return save_config(config)
