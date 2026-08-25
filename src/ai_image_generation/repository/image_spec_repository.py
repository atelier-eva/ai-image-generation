from pathlib import Path
from typing import Any

from ai_image_generation.config import Config
from ai_image_generation.domain.image_spec.image_spec import ImageSpec
from ai_image_generation.domain.image_spec.prompt import Prompt
from ai_image_generation.repository.json_io import read_json, to_string_tuple


class ImageSpecRepository:
    def find(self) -> tuple[ImageSpec, ...]:
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
        lora = data["lora"]
        size = data["image_size"]
        return ImageSpec(
            name=data["name"].strip(),
            lora_name=lora["name"].strip(),
            width=size["width"],
            height=size["height"],
            prompt=Prompt(
                positive_features=to_string_tuple(data.get("positive")),
                negative_features=to_string_tuple(data.get("negative")),
            ),
            model_strength=self._to_strength(lora.get("strength_model")),
            text_encoder_strength=self._to_strength(lora.get("strength_clip")),
            pose_image=self._to_pose_image(data),
        )

    def _to_pose_image(self, data: dict[str, Any]) -> str | None:
        pose = data.get("pose")
        if not pose:
            return None
        relative = str(pose["image"]).strip()
        if not relative:
            raise ValueError("pose.image is empty or missing.")
        directory = Config().prompt_directory
        base = directory.resolve()
        resolved = (directory / relative).resolve()
        if not resolved.is_relative_to(base):
            raise ValueError(
                f"Pose image is outside the prompt directory: {relative}"
            )
        if not resolved.is_file():
            raise FileNotFoundError(f"Pose image not found: {resolved}")
        return relative

    def _to_strength(self, value: Any, default: float = 1.0) -> float:
        if value is None:
            return default
        return float(value)
