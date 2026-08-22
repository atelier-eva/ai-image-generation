"""Command-line entry point for the AI image generation assistant."""

from argparse import ArgumentParser
from importlib.metadata import version
from sys import argv

from dotenv import load_dotenv

from ai_image_generation.config import Config
from ai_image_generation.controller.generate_lora_training_images_controller import (
    GenerateLoraTrainingImagesController,
)
from ai_image_generation.controller.init_controller import InitController

_COMMANDS = frozenset({"generate", "init"})


def main() -> None:
    load_dotenv()
    parser = _parser()
    args = parser.parse_args(_with_default_command(argv[1:]))
    if args.command == "init":
        InitController().execute(
            directory=args.directory,
            force=args.force,
        )
        return
    GenerateLoraTrainingImagesController().execute(
        base_seed=args.base_seed,
        batch_size=args.batch_size,
        from_row=args.from_row,
        to_row=args.to_row,
    )


def _add_generate_arguments(parser: ArgumentParser) -> None:
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


def _parser() -> ArgumentParser:
    parser = ArgumentParser(prog="ai-image-generation")
    parser.add_argument(
        "--version",
        action="version",
        version=f"ai-image-generation {version('ai-image-generation')}",
    )
    subparsers = parser.add_subparsers(dest="command")
    _add_generate_arguments(
        subparsers.add_parser("generate", help="Generate LoRA training images.")
    )
    init_parser = subparsers.add_parser(
        "init",
        help="Create input JSON templates in INPUT_DIRECTORY.",
    )
    init_parser.add_argument(
        "--directory",
        help=(
            "Directory for input JSON files. "
            f"Defaults to INPUT_DIRECTORY or {Config.DEFAULT_INPUT_DIRECTORY}."
        ),
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing JSON files.",
    )
    return parser


def _with_default_command(arguments: list[str]) -> list[str]:
    if not arguments:
        return ["generate"]
    if arguments[0] in _COMMANDS or arguments[0] in ("-h", "--help", "--version"):
        return arguments
    return ["generate", *arguments]
