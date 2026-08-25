import re

from ai_image_generation.domain.image_spec.generate_image_spec_output import (
    GenerateImageSpecOutput,
)
from ai_image_generation.domain.image_spec.image_spec import ImageSpec


class GenerateImageSpec:
    def execute(
        self,
        specs: tuple[ImageSpec, ...],
        filename_prefix: str,
    ) -> tuple[GenerateImageSpecOutput, ...]:
        return tuple(
            self._to_output(spec, row_number, filename_prefix)
            for row_number, spec in enumerate(specs, start=1)
        )

    def _filename_prefix(self, spec: ImageSpec, row_number: int, prefix: str) -> str:
        return f"{self._slug(prefix)}_{row_number:03d}_{self._slug(spec.name)}"

    def _slug(self, name: str) -> str:
        return re.sub(r"\s+", "-", name.strip().lower())

    def _to_output(
        self,
        spec: ImageSpec,
        row_number: int,
        prefix: str,
    ) -> GenerateImageSpecOutput:
        return GenerateImageSpecOutput(
            name=spec.name,
            filename_prefix=self._filename_prefix(spec, row_number, prefix),
            width=spec.width,
            height=spec.height,
            positive_prompt=spec.prompt.positive_text(),
            negative_prompt=spec.prompt.negative_text(),
            lora_name=spec.lora_name,
            model_strength=spec.model_strength,
            text_encoder_strength=spec.text_encoder_strength,
            pose_image=spec.pose_image,
        )
