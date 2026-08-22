from os import getenv
from pathlib import Path


class Config:
    def __init__(self) -> None:
        directory = _directory("INPUT_DIRECTORY")
        self.art_style_json = directory / "art-style.json"
        self.scene_json = directory / "scene.json"
        self.shoot_json = directory / "shoot.json"
        self.comfy_ui_url = _text("COMFY_UI_URL").rstrip("/")
        self.output_directory = _optional_directory("OUTPUT_DIRECTORY")


def _directory(name: str) -> Path:
    path = Path(_text(name)).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"{name} not found: {path}")
    return path


def _optional_directory(name: str) -> Path | None:
    text = (getenv(name) or "").strip()
    if not text:
        return None
    path = Path(text).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"{name} not found: {path}")
    return path


def _text(name: str) -> str:
    value = (getenv(name) or "").strip()
    if not value:
        raise ValueError(f"{name} is not set.")
    return value
