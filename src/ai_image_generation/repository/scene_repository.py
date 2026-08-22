from typing import Any

from ai_image_generation.domain.scene.background.scene_background import (
    SceneBackground,
)
from ai_image_generation.domain.scene.lighting.scene_lighting import SceneLighting
from ai_image_generation.domain.scene.scene import Scene
from ai_image_generation.repository.json_io import SCENE_JSON, read_json, to_string_tuple


class SceneRepository:
    def find(self) -> Scene:
        data = read_json(SCENE_JSON)
        return Scene(
            background=self._to_background(data.get("background")),
            lighting=self._to_lighting(data.get("lighting")),
        )

    def _to_background(self, data: Any) -> SceneBackground | None:
        if not data:
            return None
        return SceneBackground(
            positive_features=to_string_tuple(data.get("positive")),
            negative_features=to_string_tuple(data.get("negative")),
        )

    def _to_lighting(self, data: Any) -> SceneLighting | None:
        if not data:
            return None
        return SceneLighting(
            positive_features=to_string_tuple(data.get("positive")),
            negative_features=to_string_tuple(data.get("negative")),
        )
