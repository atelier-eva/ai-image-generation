from dataclasses import dataclass, field

from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.expression.expression_settings import ExpressionSettings
from ai_image_generation.domain.pose.pose_settings import PoseSettings
from ai_image_generation.domain.quality.quality import Quality
from ai_image_generation.domain.rating.content_rating import ContentRating
from ai_image_generation.domain.scene.background.scene_background import SceneBackground
from ai_image_generation.domain.scene.lighting.scene_lighting import SceneLighting
from ai_image_generation.domain.subject.subject import Subject


@dataclass
class Shoot:
    cameras: tuple[Camera, ...] = ()
    subjects: tuple[Subject, ...] = ()
    expressions: ExpressionSettings = field(default_factory=ExpressionSettings)
    poses: PoseSettings = field(default_factory=PoseSettings)
    backgrounds: tuple[SceneBackground, ...] = ()
    lightings: tuple[SceneLighting, ...] = ()
    art_styles: tuple[ArtStyle, ...] = ()
    quality: Quality | None = None
    rating: ContentRating | None = None
