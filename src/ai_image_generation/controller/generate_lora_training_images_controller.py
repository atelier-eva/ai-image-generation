from ai_image_generation.domain.shoot.generate_shoot_patterns import (
    GenerateShootPatterns,
)
from ai_image_generation.domain.shoot.generate_shoot_patterns_output import (
    GenerateShootPatternsOutput,
)
from ai_image_generation.infrastructure.comfy_ui import ComfyUi


class GenerateLoraTrainingImagesController:
    def execute(
        self,
        base_seed: int = 0,
        batch_size: int = 4,
        from_row: int = 1,
        to_row: int = 0,
    ) -> None:
        patterns = GenerateShootPatterns().execute()
        start, end = self._row_range(from_row, to_row, patterns)
        print(f"Processing rows {start + 1}..{end} of {len(patterns)}.")
        comfy_ui = ComfyUi()
        for index in range(start, end):
            pattern = patterns[index]
            print(f"[{index + 1}/{end}] {pattern.filename_prefix}")
            seed = base_seed + index * batch_size
            images = comfy_ui.generate_images(
                pattern.filename_prefix,
                pattern.width,
                pattern.height,
                pattern.positive_prompt,
                pattern.negative_prompt,
                seed,
                batch_size,
            )
            written = comfy_ui.write_captions(images, pattern.caption_prompt)
            if written:
                print(f"  captions: {written}")
        print(f"Done. {end - start} rows.")

    def _row_range(
        self,
        from_row: int,
        to_row: int,
        patterns: tuple[GenerateShootPatternsOutput, ...],
    ) -> tuple[int, int]:
        if not patterns:
            raise ValueError("No prompt patterns to generate.")
        if from_row < 1:
            raise ValueError("FromRow must be >= 1.")
        last_row = len(patterns) if to_row <= 0 else to_row
        if last_row > len(patterns):
            raise ValueError(
                f"ToRow ({last_row}) exceeds row count ({len(patterns)})."
            )
        if from_row > last_row:
            raise ValueError(f"FromRow ({from_row}) must be <= ToRow ({last_row}).")
        return from_row - 1, last_row
