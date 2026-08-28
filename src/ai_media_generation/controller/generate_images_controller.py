from argparse import ArgumentParser
from pathlib import Path
from sys import argv

from ai_media_generation.config import Config
from ai_media_generation.domain.image_spec.get_image_specs import GetImageSpecs
from ai_media_generation.infrastructure.comfy_ui import ComfyUi


class GenerateImagesController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.add_argument("--base-seed", type=int, default=0)
        parser.add_argument("--batch-size", type=int, default=4)
        parser.add_argument(
            "files",
            nargs="*",
            help=(
                "Prompt JSON filenames under prompt/. "
                "Omit to generate every file."
            ),
        )
        args = parser.parse_args(argv[2:])
        specs = GetImageSpecs().execute(self._prompt_ids(args.files)).dtos
        if not specs:
            raise ValueError("No prompt JSON to generate.")
        print(f"Processing {len(specs)} prompt JSON file(s).")
        prefix = Config().comfy_ui_filename_prefix
        comfy_ui = ComfyUi()
        for index, spec in enumerate(specs):
            filename_prefix = f"{prefix}_{spec.id}"
            seed = args.base_seed + index
            print(f"[{index + 1}/{len(specs)}] {filename_prefix} seed={seed}")
            images = comfy_ui.generate_images(
                filename_prefix,
                spec.width,
                spec.height,
                spec.positive_prompt,
                spec.negative_prompt,
                spec.lora_id,
                spec.model_strength,
                spec.text_encoder_strength,
                spec.pose_id,
                seed,
                args.batch_size,
            )
            written = comfy_ui.write_images(images)
            if written:
                print(f"  images: {written}")
        print(f"Done. {len(specs)} file(s).")

    def _prompt_ids(self, files: list[str]) -> tuple[str, ...]:
        ids: list[str] = []
        seen: set[str] = set()
        for raw in files:
            identifier = self._prompt_id(raw)
            if identifier in seen:
                raise ValueError(f"Duplicate prompt id: {identifier}")
            seen.add(identifier)
            ids.append(identifier)
        return tuple(ids)

    def _prompt_id(self, value: str) -> str:
        filename = Path(value).name.strip()
        if filename.endswith(".json"):
            filename = filename[: -len(".json")]
        if not filename:
            raise ValueError("Prompt id is empty.")
        return filename
