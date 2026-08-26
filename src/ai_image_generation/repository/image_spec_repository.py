from pathlib import Path
from typing import Any

from ai_image_generation.config import Config
from ai_image_generation.domain.image_spec.image_spec import ImageSpec
from ai_image_generation.domain.image_spec.lora import Lora
from ai_image_generation.domain.image_spec.pose import Pose
from ai_image_generation.domain.image_spec.prompt import Prompt
from ai_image_generation.repository.json_io import read_json, to_string_tuple


class ImageSpecRepository:
    def get(self) -> tuple[ImageSpec, ...]:
        specs: list[ImageSpec] = []
        names: dict[str, Path] = {}
        for path in self._json_paths():
            spec = self._to_image_spec(read_json(path))
            previous = names.get(spec.name)
            if previous is not None:
                raise ValueError(
                    f"Duplicate prompt name '{spec.name}': {previous} and {path}"
                )
            names[spec.name] = path
            specs.append(spec)
        return tuple(specs)

    def _json_paths(self) -> tuple[Path, ...]:
        directory = Config().prompt_directory
        if not directory.exists():
            raise FileNotFoundError(f"Prompt directory not found: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(
                f"Prompt directory is not a directory: {directory}"
            )
        paths = tuple(
            sorted(path for path in directory.glob("*.json") if path.is_file())
        )
        if not paths:
            raise FileNotFoundError(f"No prompt JSON in {directory}")
        return paths

    def _to_image_spec(self, data: dict[str, Any]) -> ImageSpec:
        size = data["image_size"]
        return ImageSpec(
            name=data["name"].strip(),
            lora=self._to_lora(data["lora"]),
            width=size["width"],
            height=size["height"],
            prompt=Prompt(
                positive_features=to_string_tuple(data.get("positive")),
                negative_features=to_string_tuple(data.get("negative")),
            ),
            pose=self._to_pose(data.get("pose")),
        )

    def _to_lora(self, data: dict[str, Any]) -> Lora:
        identifier = data["id"].strip()
        if not identifier:
            raise ValueError("lora.id is empty or missing.")
        return Lora(
            id=identifier,
            model_strength=self._to_strength(data.get("strength_model")),
            text_encoder_strength=self._to_strength(data.get("strength_clip")),
        )

    def _to_pose(self, data: dict[str, Any] | None) -> Pose | None:
        if not data:
            return None
        identifier = str(data["id"]).strip()
        if not identifier:
            raise ValueError("pose.id is empty or missing.")
        return Pose(id=identifier)

    def _to_strength(self, value: Any, default: float = 1.0) -> float:
        if value is None:
            return default
        return float(value)
