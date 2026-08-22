from ai_image_generation.domain.shoot.generate_shoot_patterns import (
    GenerateShootPatterns,
)
from ai_image_generation.infrastructure.comfy_ui import ComfyUi


class GenerateLoraTrainingImages:
    def execute(
        self,
        base_seed: int = 0,
        batch_size: int = 4,
        comfy_ui_url: str = "http://127.0.0.1:8188",
    ) -> None:
        patterns = GenerateShootPatterns().execute()
        comfy_ui = ComfyUi(comfy_ui_url)
        for index, pattern in enumerate(patterns):
            seed = base_seed + index * batch_size
            comfy_ui.generate_images(
                pattern.filename_prefix,
                pattern.width,
                pattern.height,
                pattern.positive_prompt,
                pattern.negative_prompt,
                seed,
                batch_size,
            )
