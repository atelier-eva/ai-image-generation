from argparse import ArgumentParser
from pathlib import Path
from sys import argv
from typing import Any

from ai_image_generation.config import Config
from ai_image_generation.domain.music_spec.get_music_specs import GetMusicSpecs
from ai_image_generation.infrastructure.ace_step import AceStep


class GenerateMusicController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.add_argument("--base-seed", type=int, default=0)
        parser.add_argument("--batch-size", type=int, default=1)
        parser.add_argument(
            "files",
            nargs="*",
            help=(
                "Music JSON filenames under music/. "
                "Omit to generate every file."
            ),
        )
        args = parser.parse_args(argv[2:])
        specs = GetMusicSpecs().execute(self._music_ids(args.files)).dtos
        if not specs:
            raise ValueError("No music JSON to generate.")
        print(f"Processing {len(specs)} music JSON file(s).")
        prefix = Config().ace_step_filename_prefix
        ace_step = AceStep()
        for index, spec in enumerate(specs):
            filename_prefix = f"{prefix}_{spec.id}"
            seed = args.base_seed + index * args.batch_size
            print(f"[{index + 1}/{len(specs)}] {filename_prefix} seed={seed}")
            options: dict[str, Any] = {
                "seed": seed,
                "batch_size": args.batch_size,
            }
            if spec.vocal_language:
                options["vocal_language"] = spec.vocal_language
            if spec.duration is not None:
                options["audio_duration"] = spec.duration
            if spec.bpm is not None:
                options["bpm"] = spec.bpm
            audios = ace_step.generate(
                filename_prefix, spec.prompt, spec.lyrics, **options
            )
            written = ace_step.write_audio(audios)
            if written:
                print(f"  audio: {written}")
        print(f"Done. {len(specs)} file(s).")

    def _music_ids(self, files: list[str]) -> tuple[str, ...]:
        ids: list[str] = []
        seen: set[str] = set()
        for raw in files:
            identifier = self._music_id(raw)
            if identifier in seen:
                raise ValueError(f"Duplicate music id: {identifier}")
            seen.add(identifier)
            ids.append(identifier)
        return tuple(ids)

    def _music_id(self, value: str) -> str:
        filename = Path(value).name.strip()
        if filename.endswith(".json"):
            filename = filename[: -len(".json")]
        if not filename:
            raise ValueError("Music id is empty.")
        return filename
