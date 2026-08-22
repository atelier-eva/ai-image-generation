from ai_image_generation.domain.shoot.shoot_settings import ShootSettings
from ai_image_generation.repository.json_io import (
    ART_STYLE_JSON,
    DIRECTORY,
    SCENE_JSON,
    SHOOT_JSON,
)


class ShootSettingsRepository:
    ART_STYLE_JSON = ART_STYLE_JSON
    DIRECTORY = DIRECTORY
    SCENE_JSON = SCENE_JSON
    SHOOT_JSON = SHOOT_JSON

    def find(self) -> ShootSettings:
        raise NotImplementedError
