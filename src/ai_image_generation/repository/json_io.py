import json
from os import getenv
from pathlib import Path
from typing import Any


def art_style_json() -> Path:
    return _input_directory() / "art-style.json"


def scene_json() -> Path:
    return _input_directory() / "scene.json"


def shoot_json() -> Path:
    return _input_directory() / "shoot.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"JSON not found: {path.resolve()}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON must be an object: {path}")
    return loaded


def to_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    return tuple(tag.strip() for tag in value if str(tag).strip())


def _input_directory() -> Path:
    value = (getenv("INPUT_DIRECTORY") or "").strip()
    if not value:
        raise ValueError("INPUT_DIRECTORY is not set.")
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"INPUT_DIRECTORY not found: {path}")
    return path
