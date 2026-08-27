from os import getenv
from pathlib import Path


class Config:
    DEFAULT_INPUT_DIRECTORY = "ai-image-generation"
    DEFAULT_OUTPUT_DIRECTORY = "output"
    LORA_TRAINING_DIRECTORY = "lora-training"
    PROMPT_DIRECTORY = "prompt"
    MUSIC_DIRECTORY = "music"

    def __init__(self) -> None:
        input_directory = _directory("INPUT_DIRECTORY")
        directory = input_directory / self.LORA_TRAINING_DIRECTORY
        self.art_style_json = directory / "art-style.json"
        self.camera_json = directory / "camera.json"
        self.characters_directory = directory / "characters"
        self.expression_json = directory / "expression.json"
        self.generation_json = directory / "generation.json"
        self.pose_json = directory / "pose.json"
        self.scene_json = directory / "scene.json"
        self.prompt_directory = input_directory / self.PROMPT_DIRECTORY
        self.music_directory = input_directory / self.MUSIC_DIRECTORY
        self.comfy_ui_url = _text("COMFY_UI_URL").rstrip("/")
        self.comfy_ui_ckpt_name = _text("COMFY_UI_CKPT_NAME")
        self.comfy_ui_filename_prefix = _text("COMFY_UI_FILENAME_PREFIX")
        ace_step_url = _optional_text("ACE_STEP_URL")
        self.ace_step_url = ace_step_url.rstrip("/") if ace_step_url else None
        self.ace_step_api_key = _optional_text("ACE_STEP_API_KEY")
        self.ace_step_filename_prefix = (
            _optional_text("ACE_STEP_FILENAME_PREFIX") or "music"
        )
        output_directory = _optional_directory("OUTPUT_DIRECTORY")
        if output_directory is None:
            output_directory = Path(self.DEFAULT_OUTPUT_DIRECTORY).expanduser().resolve()
            if output_directory.exists() and not output_directory.is_dir():
                raise NotADirectoryError(
                    f"OUTPUT_DIRECTORY is not a directory: {output_directory}"
                )
        self.output_directory = output_directory


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
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(f"{name} is not a directory: {path}")
    return path


def _optional_text(name: str) -> str | None:
    value = (getenv(name) or "").strip()
    if not value:
        return None
    return value


def _text(name: str) -> str:
    value = (getenv(name) or "").strip()
    if not value:
        raise ValueError(f"{name} is not set.")
    return value
