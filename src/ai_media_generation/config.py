from os import getenv
from pathlib import Path


class Config:
    DEFAULT_INPUT_DIRECTORY = "ai-media-generation"
    DEFAULT_OUTPUT_DIRECTORY = "output"
    LORA_TRAINING_DIRECTORY = "lora-training"
    LORA_TRAINING_GENERATIONS_JSONL = "lora-training-generations.jsonl"
    PROMPT_DIRECTORY = "prompt"
    MUSIC_DIRECTORY = "music"

    def __init__(self) -> None:
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
        self.lora_training_generations_jsonl = (
            output_directory / self.LORA_TRAINING_GENERATIONS_JSONL
        )

    @property
    def lora_training_directory(self) -> Path:
        return _input_tree("LORA_TRAINING_DIRECTORY", self.LORA_TRAINING_DIRECTORY)

    @property
    def prompt_directory(self) -> Path:
        return _input_tree("PROMPT_DIRECTORY", self.PROMPT_DIRECTORY)

    @property
    def music_directory(self) -> Path:
        return _input_tree("MUSIC_DIRECTORY", self.MUSIC_DIRECTORY)

    @property
    def art_style_json(self) -> Path:
        return self.lora_training_directory / "art-style.json"

    @property
    def camera_json(self) -> Path:
        return self.lora_training_directory / "camera.json"

    @property
    def characters_directory(self) -> Path:
        return self.lora_training_directory / "characters"

    @property
    def expression_json(self) -> Path:
        return self.lora_training_directory / "expression.json"

    @property
    def generation_json(self) -> Path:
        return self.lora_training_directory / "generation.json"

    @property
    def pose_json(self) -> Path:
        return self.lora_training_directory / "pose.json"

    @property
    def scene_json(self) -> Path:
        return self.lora_training_directory / "scene.json"


def _input_tree(env_name: str, relative: str) -> Path:
    specified = _optional_directory(env_name)
    if specified is not None:
        return specified
    root_text = (getenv("INPUT_DIRECTORY") or "").strip()
    if not root_text:
        raise ValueError(f"{env_name} or INPUT_DIRECTORY is not set.")
    root = Path(root_text).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise NotADirectoryError(f"INPUT_DIRECTORY is not a directory: {root}")
    path = root / relative
    if path.exists() and not path.is_dir():
        raise NotADirectoryError(f"{env_name} is not a directory: {path}")
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
