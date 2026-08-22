import json
from pathlib import Path
from typing import Any

DIRECTORY = Path("ai-image-generation")
ART_STYLE_JSON = DIRECTORY / "art-style.json"
SCENE_JSON = DIRECTORY / "scene.json"
SHOOT_JSON = DIRECTORY / "shoot.json"


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
