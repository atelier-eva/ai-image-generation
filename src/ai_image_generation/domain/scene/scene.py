from dataclasses import dataclass

from ai_image_generation.domain.scene.background.scene_background import (
    SceneBackground,
)
from ai_image_generation.domain.scene.lighting.scene_lighting import SceneLighting


@dataclass
class Scene:
    background: SceneBackground | None = None
    lighting: SceneLighting | None = None
