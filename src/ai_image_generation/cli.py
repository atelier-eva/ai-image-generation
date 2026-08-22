"""Command-line entry point for the AI image generation assistant."""

from argparse import ArgumentParser
from importlib.metadata import version

from ai_image_generation.controller.generate_lora_training_images import (
    GenerateLoraTrainingImages,
)


def main() -> None:
    parser = ArgumentParser(prog="ai-image-generation")
    parser.add_argument(
        "--version",
        action="version",
        version=f"ai-image-generation {version('ai-image-generation')}",
    )
    parser.add_argument("--base-seed", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--comfy-ui-url", default="http://127.0.0.1:8188")
    args = parser.parse_args()
    GenerateLoraTrainingImages().execute(
        base_seed=args.base_seed,
        batch_size=args.batch_size,
        comfy_ui_url=args.comfy_ui_url,
    )
