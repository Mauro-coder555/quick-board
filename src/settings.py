import json
import os
from pathlib import Path
from typing import Any


APP_NAME = "quick-board"


def get_app_data_dir() -> Path:
    appdata_path = os.getenv("APPDATA")

    if appdata_path:
        return Path(appdata_path) / APP_NAME

    return Path.home() / f".{APP_NAME}"


DATA_DIR = get_app_data_dir()
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "language": "es",
    "background_color": "#8B5E34",
}


def ensure_settings_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(
            json.dumps(DEFAULT_SETTINGS, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def load_settings() -> dict[str, Any]:
    ensure_settings_file()

    try:
        raw_content = SETTINGS_FILE.read_text(encoding="utf-8").strip()

        if not raw_content:
            return DEFAULT_SETTINGS.copy()

        settings = json.loads(raw_content)

        if not isinstance(settings, dict):
            return DEFAULT_SETTINGS.copy()

        return {
            "language": settings.get("language", DEFAULT_SETTINGS["language"]),
            "background_color": settings.get(
                "background_color",
                DEFAULT_SETTINGS["background_color"],
            ),
        }

    except json.JSONDecodeError:
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    clean_settings = {
        "language": settings.get("language", DEFAULT_SETTINGS["language"]),
        "background_color": settings.get(
            "background_color",
            DEFAULT_SETTINGS["background_color"],
        ),
    }

    SETTINGS_FILE.write_text(
        json.dumps(clean_settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )