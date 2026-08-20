from dataclasses import dataclass

from ai_image_generation.domain.camera.angle.camera_angle import CameraAngleName
from ai_image_generation.domain.camera.distance.camera_distance import CameraDistanceName
from ai_image_generation.domain.character.feature.character_feature import (
    CharacterFeature,
)


@dataclass
class ShotExclusionSettings:
    angle_name: CameraAngleName | None = None
    distance_name: CameraDistanceName | None = None
    feature: CharacterFeature | None = None
