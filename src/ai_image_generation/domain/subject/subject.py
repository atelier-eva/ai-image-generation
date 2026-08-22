from dataclasses import dataclass

from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.subject.feature.subject_feature import SubjectFeature


@dataclass
class Subject:
    name: str
    kinds: tuple[str, ...] = ()
    features: tuple[SubjectFeature, ...] = ()

    def filtered_features(self, camera: Camera) -> tuple[SubjectFeature, ...]:
        return tuple(
            feature for feature in self.features if not feature.skips(camera)
        )
