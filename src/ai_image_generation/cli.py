"""Command-line entry point for the AI image generation assistant."""

from argparse import ArgumentParser
from importlib.metadata import version
from sys import argv

from dotenv import load_dotenv

from ai_image_generation.controller.generate_lora_training_images_controller import (
    GenerateLoraTrainingImagesController,
)
from ai_image_generation.controller.init_controller import InitController


def main() -> None:
    load_dotenv()
    arguments = argv[1:]
    command = arguments[0] if arguments else ""
    if command == "init":
        InitController().execute(_command_parser("init"))
        return
    if command == "generate":
        GenerateLoraTrainingImagesController().execute(_command_parser("generate"))
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
        "generate",
        help="Generate LoRA training images.",
    )
    subparsers.add_parser(
        "init",
        help="Create input JSON templates in INPUT_DIRECTORY.",
    )
    return parser
