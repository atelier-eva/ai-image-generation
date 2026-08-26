from argparse import ArgumentParser
from sys import argv

from ai_image_generation.domain.image_spec.get_image_specs import GetImageSpecs
from ai_image_generation.domain.image_spec.get_image_specs_output import ImageSpecDto


class GenerateImagesController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.parse_args(argv[2:])
        specs = GetImageSpecs().execute().dtos
        if not specs:
            raise ValueError("No image specs to generate.")
        print(f"Loaded {len(specs)} image specs.")
        for index, spec in enumerate(specs, start=1):
            print(f"[{index}/{len(specs)}] {self._line(spec)}")

    def _line(self, spec: ImageSpecDto) -> str:
        pose = spec.pose_id or "-"
        return (
            f"{spec.name} {spec.width}x{spec.height} "
            f"lora={spec.lora_id} pose={pose}"
        )
