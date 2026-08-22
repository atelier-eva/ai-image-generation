from dataclasses import dataclass

from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.character.feature.character_feature import (
    CharacterFeature,
)


@dataclass
class ShotFilter:
    angles: tuple[str, ...] = ()
    distances: tuple[str, ...] = ()
    exclude_expressions: bool = False
    feature: CharacterFeature | None = None

    def applies_to(self, camera: Camera) -> bool:
        angle_ok = not self.angles or camera.angle.name in self.angles
        distance_ok = not self.distances or camera.distance.name in self.distances
        return angle_ok and distance_ok
