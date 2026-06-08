import json
import os
from pathlib import Path
from typing import Any


MAX_SLOTS = 10
APP_NAME = "quick-board"


def get_app_data_dir() -> Path:
    appdata_path = os.getenv("APPDATA")

    if appdata_path:
        return Path(appdata_path) / APP_NAME

    return Path.home() / f".{APP_NAME}"


DATA_DIR = get_app_data_dir()
SLOTS_FILE = DATA_DIR / "slots.json"


def ensure_storage_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SLOTS_FILE.exists():
        SLOTS_FILE.write_text("[]", encoding="utf-8")


def load_slots() -> list[dict[str, Any]]:
    ensure_storage_file()

    try:
        raw_content = SLOTS_FILE.read_text(encoding="utf-8").strip()

        if not raw_content:
            return []

        slots = json.loads(raw_content)

        if not isinstance(slots, list):
            return []

        valid_slots = []

        for slot in slots:
            if not isinstance(slot, dict):
                continue

            title = str(slot.get("title", "")).strip()
            content = str(slot.get("content", "")).strip()
            color = str(slot.get("color", "#FDE68A")).strip()

            if not title or not content:
                continue

            valid_slots.append(
                {
                    "title": title,
                    "content": content,
                    "color": color,
                }
            )

        return valid_slots[:MAX_SLOTS]

    except json.JSONDecodeError:
        return []


def save_slots(slots: list[dict[str, Any]]) -> None:
    ensure_storage_file()

    clean_slots = []

    for slot in slots[:MAX_SLOTS]:
        title = str(slot.get("title", "")).strip()
        content = str(slot.get("content", "")).strip()
        color = str(slot.get("color", "#FDE68A")).strip()

        if not title or not content:
            continue

        clean_slots.append(
            {
                "title": title,
                "content": content,
                "color": color,
            }
        )

    SLOTS_FILE.write_text(
        json.dumps(clean_slots, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )