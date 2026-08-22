from ai_image_generation.domain.scene.scene import Scene
from ai_image_generation.domain.shoot.shoot_settings import ShootSettings
from ai_image_generation.repository.art_style_repository import ArtStyleRepository
from ai_image_generation.repository.camera_repository import CameraRepository
from ai_image_generation.repository.expression_repository import ExpressionRepository
from ai_image_generation.repository.json_io import (
    ART_STYLE_JSON,
    DIRECTORY,
    SCENE_JSON,
    SHOOT_JSON,
)
from ai_image_generation.repository.quality_repository import QualityRepository
from ai_image_generation.repository.rating_repository import RatingRepository
from ai_image_generation.repository.scene_repository import SceneRepository
from ai_image_generation.repository.subject_repository import SubjectRepository


class ShootSettingsRepository:
    ART_STYLE_JSON = ART_STYLE_JSON
    DIRECTORY = DIRECTORY
    SCENE_JSON = SCENE_JSON
    SHOOT_JSON = SHOOT_JSON

    def find(self) -> ShootSettings:
        return ShootSettings(
            cameras=CameraRepository().find(),
            subjects=SubjectRepository().find(),
            expressions=ExpressionRepository().find(),
            scene=self._scene(),
            art_style=ArtStyleRepository().find(),
            quality=QualityRepository().find(),
            rating=RatingRepository().find(),
        )

    def _scene(self) -> Scene | None:
        if not SCENE_JSON.is_file():
            return None
        return SceneRepository().find()
