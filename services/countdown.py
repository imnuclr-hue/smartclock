from datetime import datetime
from utils.settings import load_settings, save_settings

def save_countdown(iso_str: str | None):
    settings = load_settings()
    settings["countdown_target"] = iso_str
    save_settings(settings)

def get_countdown_remaining():
    settings = load_settings()
    target = settings.get("countdown_target")

    if not target:
        return None

    try:
        target_dt = datetime.fromisoformat(target)
        delta = target_dt - datetime.now()

        if delta.total_seconds() <= 0:
            return 0

        return int(delta.total_seconds())

    except Exception:
        return None
