from dataclasses import dataclass

from ai_image_generation.domain.scene.background.scene_background import (
    SceneBackground,
)
from ai_image_generation.domain.scene.lighting.scene_lighting import SceneLighting


@dataclass
class Scene:
    background: SceneBackground | None = None
    lighting: SceneLighting | None = None

    @property
    def negative_features(self) -> tuple[str, ...]:
        return (
            *(self.background.negative_features if self.background else ()),
            *(self.lighting.negative_features if self.lighting else ()),
        )

    @property
    def positive_features(self) -> tuple[str, ...]:
        return (
            *(self.background.positive_features if self.background else ()),
            *(self.lighting.positive_features if self.lighting else ()),
        )
