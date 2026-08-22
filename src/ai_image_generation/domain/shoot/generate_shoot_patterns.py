from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.shoot.generate_shoot_patterns_output import (
    GenerateShootPatternsOutput,
)
from ai_image_generation.repository.shoot_repository import ShootRepository


class GenerateShootPatterns:
    def execute(self) -> tuple[GenerateShootPatternsOutput, ...]:
        shoot = ShootRepository().find()
        patterns: list[GenerateShootPatternsOutput] = []
        for camera in shoot.cameras:
            for subject in shoot.subjects:
                if shoot.expressions.includes(camera):
                    for expression in shoot.expressions.patterns:
                        patterns.append(self._to_output(camera))
                else:
                    patterns.append(self._to_output(camera))
        return tuple(patterns)

    def _to_output(self, camera: Camera) -> GenerateShootPatternsOutput:
        return GenerateShootPatternsOutput(
            filename_prefix="",
            width=camera.frame.width,
            height=camera.frame.height,
            positive_prompt="",
            negative_prompt="",
            caption_prompt="",
        )
