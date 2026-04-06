import json
from pathlib import Path
from utils.logger import log_error

SETTINGS_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.json"

def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_error("Failed to load settings.json", e)
        return {}

def save_settings(data: dict):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_error("Failed to save settings.json", e)
