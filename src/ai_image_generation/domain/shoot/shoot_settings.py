from dataclasses import dataclass

from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.character.character import Character
from ai_image_generation.domain.shoot.shot_exclusion_settings import (
    ShotExclusionSettings,
)


@dataclass
class ShootSettings:
    cameras: tuple[Camera, ...] = ()
    characters: tuple[Character, ...] = ()
    exclusions: tuple[ShotExclusionSettings, ...] = ()
