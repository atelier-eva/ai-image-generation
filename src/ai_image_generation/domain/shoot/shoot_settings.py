from dataclasses import dataclass

from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.character.character import Character
from ai_image_generation.domain.quality.quality import Quality
from ai_image_generation.domain.rating.content_rating import ContentRating
from ai_image_generation.domain.scene.scene import Scene
from ai_image_generation.domain.shoot.shot_exclusion_settings import (
    ShotExclusionSettings,
)


@dataclass
class ShootSettings:
    cameras: tuple[Camera, ...] = ()
    characters: tuple[Character, ...] = ()
    exclusions: tuple[ShotExclusionSettings, ...] = ()
    scene: Scene | None = None
    art_style: ArtStyle | None = None
    quality: Quality | None = None
    rating: ContentRating = ContentRating.SAFE
