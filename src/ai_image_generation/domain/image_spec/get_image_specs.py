from ai_image_generation.domain.image_spec.get_image_specs_output import (
    GetImageSpecsOutput,
)
from ai_image_generation.repository.image_spec_repository import ImageSpecRepository


class GetImageSpecs:
    def execute(self) -> GetImageSpecsOutput:
        return GetImageSpecsOutput(ImageSpecRepository().get())
