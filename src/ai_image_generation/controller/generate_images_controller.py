from argparse import ArgumentParser
from sys import argv

from ai_image_generation.domain.image_spec.get_image_specs import GetImageSpecs


class GenerateImagesController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.parse_args(argv[2:])
        GetImageSpecs().execute()
