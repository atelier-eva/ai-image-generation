from dataclasses import dataclass

from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.character.character import Character
from ai_image_generation.domain.character.feature.character_feature import (
    CharacterFeature,
)
from ai_image_generation.domain.quality.quality import Quality
from ai_image_generation.domain.rating.content_rating import ContentRating
from ai_image_generation.domain.scene.scene import Scene
from ai_image_generation.domain.shoot.shot_exclusion import ShotExclusion
from ai_image_generation.domain.shoot.shot_filter import ShotFilter


@dataclass
class ShootSettings:
    cameras: tuple[Camera, ...] = ()
    characters: tuple[Character, ...] = ()
    exclusions: tuple[ShotExclusion, ...] = ()
    filters: tuple[ShotFilter, ...] = ()
    scene: Scene | None = None
    art_style: ArtStyle | None = None
    quality: Quality | None = None
    rating: ContentRating | None = None

    def includes_expression_patterns(
        self, character: Character, camera: Camera
    ) -> bool:
        if any(
            rule.exclude_expressions and rule.applies_to(camera) for rule in self.filters
        ):
            return False
        return bool(character.expressions)

    def is_excluded(self, camera: Camera) -> bool:
        return any(rule.excludes(camera) for rule in self.exclusions)

    def filtered_features(
        self, character: Character, camera: Camera
    ) -> tuple[CharacterFeature, ...]:
        hidden = [
            rule.feature
            for rule in self.filters
            if rule.feature is not None and rule.applies_to(camera)
        ]
        return tuple(
            feature for feature in character.features if feature not in hidden
        )
