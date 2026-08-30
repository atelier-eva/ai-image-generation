from pathlib import Path
from typing import Any

from ai_media_generation.config import Config
from ai_media_generation.domain.image_spec.image_spec import ImageSpec
from ai_media_generation.domain.image_spec.prompt import Prompt
from ai_media_generation.repository.json_io import read_json, to_string_tuple


class ImageSpecRepository:
    def get(self, ids: tuple[str, ...] = ()) -> tuple[ImageSpec, ...]:
        paths = self._paths_for(ids) if ids else self._json_paths()
        return tuple(self._to_image_spec(read_json(path), path.stem) for path in paths)

    def _paths_for(self, ids: tuple[str, ...]) -> tuple[Path, ...]:
        directory = self._prompt_directory()
        paths: list[Path] = []
        for identifier in ids:
            self._validate_id(identifier)
            path = directory / f"{identifier}.json"
            if not path.is_file():
                raise FileNotFoundError(f"Prompt JSON not found: {path.name}")
            paths.append(path)
        return tuple(paths)

    def _json_paths(self) -> tuple[Path, ...]:
        directory = self._prompt_directory()
        paths = tuple(
            sorted(path for path in directory.glob("*.json") if path.is_file())
        )
        if not paths:
            raise FileNotFoundError(f"No prompt JSON in {directory}")
        return paths

    def _prompt_directory(self) -> Path:
        directory = Config().prompt_directory
        if not directory.exists():
            raise FileNotFoundError(f"Prompt directory not found: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(
                f"Prompt directory is not a directory: {directory}"
            )
        return directory

    def _validate_id(self, identifier: str) -> None:
        if not identifier or Path(identifier).name != identifier:
            raise ValueError(f"Invalid prompt id: {identifier}")

    def _to_image_spec(self, data: dict[str, Any], identifier: str) -> ImageSpec:
        lora = data.get("lora") or {}
        size = data["image_size"]
        return ImageSpec(
            id=identifier,
            lora_id=self._to_lora_id(data),
            width=size["width"],
            height=size["height"],
            prompt=Prompt(
                positive_features=to_string_tuple(data.get("positive")),
                negative_features=to_string_tuple(data.get("negative")),
            ),
            model_strength=self._to_strength(lora.get("strength_model")),
            text_encoder_strength=self._to_strength(lora.get("strength_clip")),
            pose_id=self._to_pose_id(data),
        )

    def _to_lora_id(self, data: dict[str, Any]) -> str | None:
        lora = data.get("lora")
        if not lora:
            return None
        identifier = str(lora["id"]).strip()
        if not identifier:
            raise ValueError("lora.id is empty or missing.")
        return identifier

    def _to_pose_id(self, data: dict[str, Any]) -> str | None:
        pose = data.get("pose")
        if not pose:
            return None
        identifier = str(pose["id"]).strip()
        if not identifier:
            raise ValueError("pose.id is empty or missing.")
        return identifier

    def _to_strength(self, value: Any, default: float = 1.0) -> float:
        if value is None:
            return default
        return float(value)
