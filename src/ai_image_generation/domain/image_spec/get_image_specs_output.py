from dataclasses import dataclass

from ai_image_generation.domain.image_spec.image_spec import ImageSpec


@dataclass
class ImageSpecDto:
    name: str
    width: int
    height: int
    positive_prompt: str
    negative_prompt: str
    lora_name: str
    model_strength: float
    text_encoder_strength: float
    pose_image: str | None


class GetImageSpecsOutput:
    def __init__(self, specs: tuple[ImageSpec, ...]) -> None:
        self.dtos = tuple(self._to_dto(spec) for spec in specs)

    @staticmethod
    def _to_dto(spec: ImageSpec) -> ImageSpecDto:
        return ImageSpecDto(
            name=spec.name,
            width=spec.width,
            height=spec.height,
            positive_prompt=spec.prompt.positive_text(),
            negative_prompt=spec.prompt.negative_text(),
            lora_name=spec.lora_name,
            model_strength=spec.model_strength,
            text_encoder_strength=spec.text_encoder_strength,
            pose_image=spec.pose_image,
        )
