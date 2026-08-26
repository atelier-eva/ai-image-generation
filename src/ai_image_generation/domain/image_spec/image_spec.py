from dataclasses import dataclass

from ai_image_generation.domain.image_spec.lora import Lora
from ai_image_generation.domain.image_spec.pose import Pose
from ai_image_generation.domain.image_spec.prompt import Prompt


@dataclass
class ImageSpec:
    name: str
    lora: Lora
    width: int
    height: int
    prompt: Prompt
    pose: Pose | None = None
