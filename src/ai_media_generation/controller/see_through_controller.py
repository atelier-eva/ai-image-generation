from argparse import ArgumentParser
from pathlib import Path
from sys import argv

from ai_media_generation.config import Config
from ai_media_generation.infrastructure.see_through import SeeThrough


class SeeThroughController:
    def execute(self, parser: ArgumentParser) -> None:
        parser.add_argument("--base-seed", type=int, default=42)
        parser.add_argument(
            "files",
            nargs="+",
            help="Image paths to decompose into character layers.",
        )
        args = parser.parse_args(argv[2:])
        images = self._images(args.files)
        print(f"Processing {len(images)} image(s).")
        config = Config()
        save_directory = config.see_through_save_directory
        see_through = SeeThrough()
        for index, image in enumerate(images):
            seed = args.base_seed + index
            print(f"[{index + 1}/{len(images)}] {image} seed={seed}")
            layers = see_through.decompose(image, seed=seed)
            destination = save_directory / image.stem / "layers"
            written = see_through.write_layers(layers, destination)
            if written:
                print(f"  layers: {written} ({destination})")
        print(f"Done. {len(images)} file(s).")

    def _images(self, files: list[str]) -> tuple[Path, ...]:
        images: list[Path] = []
        seen: set[Path] = set()
        for raw in files:
            text = raw.strip()
            if not text:
                raise ValueError("Image path is empty.")
            path = Path(text).expanduser().resolve()
            if path in seen:
                raise ValueError(f"Duplicate image: {path}")
            seen.add(path)
            images.append(path)
        return tuple(images)
