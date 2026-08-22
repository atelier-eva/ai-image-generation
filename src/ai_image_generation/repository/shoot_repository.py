from ai_image_generation.config import Config
from ai_image_generation.domain.scene.scene import Scene
from ai_image_generation.domain.shoot.shoot import Shoot
from ai_image_generation.repository.art_style_repository import ArtStyleRepository
from ai_image_generation.repository.camera_repository import CameraRepository
from ai_image_generation.repository.expression_repository import ExpressionRepository
from ai_image_generation.repository.pose_repository import PoseRepository
from ai_image_generation.repository.quality_repository import QualityRepository
from ai_image_generation.repository.rating_repository import RatingRepository
from ai_image_generation.repository.scene_repository import SceneRepository
from ai_image_generation.repository.subject_repository import SubjectRepository


class ShootRepository:
    def find(self) -> Shoot:
        return Shoot(
            cameras=CameraRepository().find(),
            subjects=SubjectRepository().find(),
            expressions=ExpressionRepository().find(),
            poses=PoseRepository().find(),
            scene=self._scene(),
            art_style=ArtStyleRepository().find(),
            quality=QualityRepository().find(),
            rating=RatingRepository().find(),
        )

    def _scene(self) -> Scene | None:
        if not Config().scene_json.is_file():
            return None
        return SceneRepository().find()
