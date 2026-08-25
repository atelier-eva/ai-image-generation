from dataclasses import dataclass

from ai_image_generation.domain.image_spec.prompt import Prompt


@dataclass
class ImageSpec:
    name: str
    lora_name: str
    width: int
    height: int
    prompt: Prompt
    strength_model: float = 1.0
    strength_clip: float = 1.0
    pose_image: str | None = None
