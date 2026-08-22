from argparse import ArgumentParser
from importlib.resources import files
from os import getenv
from pathlib import Path
from sys import argv

from ai_image_generation.config import Config

_JSON_FILES = (
    "art-style.json",
    "scene.json",
    "shoot.json",
)


class InitController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--directory",
            help=(
                "Root directory for feature input folders. "
                f"LoRA templates go in {Config.LORA_TRAINING_DIRECTORY}/. "
                f"Defaults to INPUT_DIRECTORY or {Config.DEFAULT_INPUT_DIRECTORY}."
            ),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing JSON files.",
        )
        args = parser.parse_args(argv[2:])
        text = (
            args.directory
            or getenv("INPUT_DIRECTORY")
            or Config.DEFAULT_INPUT_DIRECTORY
        ).strip()
        if not text:
            raise ValueError("INPUT_DIRECTORY is not set.")
        path = Path(text).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        lora_training = path / Config.LORA_TRAINING_DIRECTORY
        lora_training.mkdir(parents=True, exist_ok=True)
        for name in _JSON_FILES:
            self._write_json(lora_training / name, args.force)
        self._write_env(text)
        print(f"Input directory: {path}")
        print("Fill in the JSON tags, then run: ai-image-generation generate")

    def _with_input_directory(self, text: str, directory: str) -> str:
        lines: list[str] = []
        replaced = False
        for line in text.splitlines(keepends=True):
            body = line.rstrip("\r\n")
            ending = line[len(body) :]
            if body.strip().startswith("INPUT_DIRECTORY="):
                indent = body[: len(body) - len(body.lstrip())]
                lines.append(f"{indent}INPUT_DIRECTORY={directory}{ending}")
                replaced = True
            else:
                lines.append(line)
        result = "".join(lines)
        if replaced:
            return result
        if result and not result.endswith("\n"):
            result += "\n"
        return result + f"INPUT_DIRECTORY={directory}\n"

    def _write_env(self, directory: str) -> None:
        env_path = Path(".env")
        if env_path.exists():
            print(f"Skipped existing: {env_path.resolve()}")
            return
        example = files("ai_image_generation.resources").joinpath("env.example")
        env_path.write_text(
            self._with_input_directory(
                example.read_text(encoding="utf-8"),
                directory,
            ),
            encoding="utf-8",
        )
        print(f"Created: {env_path.resolve()}")

    def _write_json(self, destination: Path, force: bool) -> None:
        existed = destination.exists()
        if existed and not force:
            print(f"Skipped existing: {destination}")
            return
        source = files("ai_image_generation.resources").joinpath(
            Config.LORA_TRAINING_DIRECTORY,
            destination.name,
        )
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        action = "Overwrote" if existed else "Created"
        print(f"{action}: {destination}")
