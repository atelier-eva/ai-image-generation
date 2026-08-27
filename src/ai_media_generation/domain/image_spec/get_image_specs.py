from ai_media_generation.domain.image_spec.get_image_specs_output import (
    GetImageSpecsOutput,
)
from ai_media_generation.repository.image_spec_repository import ImageSpecRepository


class GetImageSpecs:
    def execute(self, ids: tuple[str, ...] = ()) -> GetImageSpecsOutput:
        return GetImageSpecsOutput(ImageSpecRepository().get(ids))
