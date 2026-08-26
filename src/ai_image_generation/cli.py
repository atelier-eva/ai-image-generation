"""Command-line entry point for the AI image generation assistant."""

from argparse import ArgumentParser
from importlib.metadata import version
from pathlib import Path
from sys import argv

from dotenv import load_dotenv

from ai_image_generation.controller.generate_images_controller import (
    GenerateImagesController,
)
from ai_image_generation.controller.generate_lora_training_images_controller import (
    GenerateLoraTrainingImagesController,
)
from ai_image_generation.controller.init_controller import InitController
from ai_image_generation.controller.report_lora_training_patterns_controller import (
    ReportLoraTrainingPatternsController,
)


def main() -> None:
    load_dotenv(Path.cwd() / ".env")
    arguments = argv[1:]
    command = arguments[0] if arguments else ""
    if command == "init":
        InitController().execute(_command_parser("init"))
        return
    if command == "lora-training":
        GenerateLoraTrainingImagesController().execute(_command_parser("lora-training"))
        return
    if command == "image":
        GenerateImagesController().execute(_command_parser("image"))
        return
    if command == "report":
        ReportLoraTrainingPatternsController().execute(_command_parser("report"))
        return
    _parser().parse_args(arguments)


def _command_parser(command: str) -> ArgumentParser:
    return ArgumentParser(prog=f"ai-image-generation {command}")


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="ai-image-generation")
    parser.add_argument(
        "--version",
        action="version",
        version=f"ai-image-generation {version('ai-image-generation')}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "lora-training",
        help="Generate LoRA training images.",
    )
    subparsers.add_parser(
        "image",
        help="Generate images from prompt/*.json specs.",
    )
    subparsers.add_parser(
        "init",
        help="Create input JSON templates in INPUT_DIRECTORY.",
    )
    subparsers.add_parser(
        "report",
        help="Write LoRA training pattern rows to CSV.",
    )
    return parser
