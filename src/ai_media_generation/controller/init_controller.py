from argparse import ArgumentParser
from importlib.resources import files
from os import getenv
from pathlib import Path
from sys import argv

from ai_media_generation.config import Config

_JSON_FILES = (
    "art-style.json",
    "camera.json",
    "expression.json",
    "generation.json",
    "pose.json",
    "scene.json",
)
_CHARACTERS_DIRECTORY = "characters"


class InitController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--directory",
            help=(
                "Root directory for feature input folders. "
                f"LoRA templates go in {Config.LORA_TRAINING_DIRECTORY}/. "
                f"Prompt templates go in {Config.PROMPT_DIRECTORY}/. "
                f"Music templates go in {Config.MUSIC_DIRECTORY}/. "
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
        prompt = path / Config.PROMPT_DIRECTORY
        music = path / Config.MUSIC_DIRECTORY
        lora_training.mkdir(parents=True, exist_ok=True)
        for name in _JSON_FILES:
            self._write_json(lora_training / name, args.force)
        self._write_characters(lora_training / _CHARACTERS_DIRECTORY, args.force)
        self._write_directory(
            (Config.PROMPT_DIRECTORY,),
            prompt,
            args.force,
        )
        self._write_directory(
            (Config.MUSIC_DIRECTORY,),
            music,
            args.force,
        )
        self._write_env(
            {
                "INPUT_DIRECTORY": str(path),
                "LORA_TRAINING_DIRECTORY": str(lora_training),
                "PROMPT_DIRECTORY": str(prompt),
                "MUSIC_DIRECTORY": str(music),
            }
        )
        print(f"Input directory: {path}")
        print(
            "Fill in the JSON tags, then run: "
            "ai-media-generation lora-training, image, or music"
        )

    def _with_env_values(self, text: str, values: dict[str, str]) -> str:
        remaining = dict(values)
        lines: list[str] = []
        for line in text.splitlines(keepends=True):
            body = line.rstrip("\r\n")
            ending = line[len(body) :]
            stripped = body.strip()
            matched: str | None = None
            for key in remaining:
                if stripped.startswith(f"{key}="):
                    matched = key
                    break
            if matched is None:
                lines.append(line)
                continue
            indent = body[: len(body) - len(body.lstrip())]
            lines.append(f"{indent}{matched}={remaining.pop(matched)}{ending}")
        result = "".join(lines)
        if remaining:
            if result and not result.endswith("\n"):
                result += "\n"
            for key, value in remaining.items():
                result += f"{key}={value}\n"
        return result

    def _write_env(self, values: dict[str, str]) -> None:
        env_path = Path(".env")
        if env_path.exists():
            print(f"Skipped existing: {env_path.resolve()}")
            return
        example = files("ai_media_generation.resources").joinpath("env.example")
        env_path.write_text(
            self._with_env_values(example.read_text(encoding="utf-8"), values),
            encoding="utf-8",
        )
        print(f"Created: {env_path.resolve()}")

    def _write_characters(self, destination: Path, force: bool) -> None:
        self._write_directory(
            (Config.LORA_TRAINING_DIRECTORY, destination.name),
            destination,
            force,
        )

    def _write_directory(
        self, relative: tuple[str, ...], destination: Path, force: bool
    ) -> None:
        if destination.exists() and not destination.is_dir():
            raise NotADirectoryError(f"Not a directory: {destination}")
        existed = destination.exists()
        destination.mkdir(parents=True, exist_ok=True)
        source_dir = files("ai_media_generation.resources").joinpath(*relative)
        names = tuple(
            sorted(
                item.name
                for item in source_dir.iterdir()
                if item.name.endswith(".json") and item.is_file()
            )
        )
        if not names:
            action = "Skipped existing" if existed else "Created"
            print(f"{action}: {destination}")
            return
        for name in names:
            self._write_resource((*relative, name), destination / name, force)

    def _write_json(self, destination: Path, force: bool) -> None:
        self._write_resource(
            (Config.LORA_TRAINING_DIRECTORY, destination.name),
            destination,
            force,
        )

    def _write_resource(
        self, relative: tuple[str, ...], destination: Path, force: bool
    ) -> None:
        existed = destination.exists()
        if existed and not force:
            print(f"Skipped existing: {destination}")
            return
        source = files("ai_media_generation.resources").joinpath(*relative)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        action = "Overwrote" if existed else "Created"
        print(f"{action}: {destination}")
