"""Command-line entry point for the AI image generation assistant."""

from argparse import ArgumentParser
from importlib.metadata import version

from dotenv import load_dotenv

from ai_image_generation.controller.generate_lora_training_images_controller import (
    GenerateLoraTrainingImagesController,
)


def main() -> None:
    load_dotenv()
    parser = ArgumentParser(prog="ai-image-generation")
    parser.add_argument(
        "--version",
        action="version",
        version=f"ai-image-generation {version('ai-image-generation')}",
    )
    parser.add_argument("--base-seed", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument(
        "--from-row",
        type=int,
        default=1,
        help="1-based first prompt row to generate (inclusive).",
    )
    parser.add_argument(
        "--to-row",
        type=int,
        default=0,
        help="1-based last prompt row to generate (inclusive). 0 means the last row.",
    )
    args = parser.parse_args()
    GenerateLoraTrainingImagesController().execute(
        base_seed=args.base_seed,
        batch_size=args.batch_size,
        from_row=args.from_row,
        to_row=args.to_row,
    )
